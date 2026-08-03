"""
Full Graph Simulation Script.
Usage: python simulate_graph.py "your message here"

State persists between runs via simulation_state.json.
Results are appended to simulation_results.txt.
To reset: delete simulation_state.json and simulation_results.txt
"""
import os
import sys
import json

# Fix Windows console Unicode encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.job_search_agent.models.job_knowledge import JobKnowledge
from app.models.candidate_insights import CandidateInsights
from app.models.candidate_profile import CandidateProfile
from app.models.user import User

STATE_FILE = "simulation_state.json"
RESULTS_FILE = "simulation_results.txt"


def run_turn(user_message):
    from app.resume_tailoring_agent_v2.graph import build_graph

    # ---- Load or Initialize State ----
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state_input = json.load(f)
        print(f"[Loaded State] Messages: {len(state_input.get('messages', []))}, Drafts: {list(state_input.get('drafts', {}).keys())}")
    else:
        db = SessionLocal()
        try:
            job_doc = db.query(JobKnowledge).first()
            cand_doc = db.query(CandidateInsights).first()
            state_input = {
                "session_id": "full_simulation",
                "job_knowledge": job_doc.raw_knowledge,
                "user_knowledge": cand_doc.artifact_json,
                "messages": [],
                "drafts": {},
                "active_section": None,
                "pending_sections": ["summary", "experience", "education", "skills", "projects", "certifications"],
                "current_section": None,
            }
            print("[Fresh State] Created from database.")
        finally:
            db.close()

    # ---- Add user message & reset router field ----
    state_input["messages"].append({"role": "user", "content": user_message})
    state_input["active_section"] = None

    # ---- Build fresh graph & run ----
    graph = build_graph()
    config = {"configurable": {"thread_id": "simulation_thread"}}

    print(f'\n>> User: "{user_message}"')
    print(">> Running graph...\n")

    result = graph.invoke(state_input, config)

    # ---- Normalise result to dict ----
    if hasattr(result, "model_dump"):
        state_dict = result.model_dump()
    elif isinstance(result, dict):
        state_dict = dict(result)
    else:
        state_dict = result

    for key in state_input:
        if key not in state_dict:
            state_dict[key] = state_input[key]

    # ---- Save state to disk ----
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state_dict, f, indent=2, default=str)

    # ---- Extract & display results ----
    messages = state_dict.get("messages", [])
    assistant_msg = (
        messages[-1].get("content", "No message")
        if messages and messages[-1].get("role") == "assistant"
        else "No assistant reply generated."
    )
    active = state_dict.get("active_section", "unknown")
    draft_keys = list(state_dict.get("drafts", {}).keys())
    turn_num = len([m for m in messages if m.get("role") == "user"])

    print(f"   Routed To : {active}")
    print(f"   Assistant : {assistant_msg}")
    print(f"   Drafts    : {draft_keys}")

    # ---- Append to results log ----
    # Also dump the latest draft for the active section
    latest_draft = ""
    if active and active in state_dict.get("drafts", {}):
        section_drafts = state_dict["drafts"][active]
        if section_drafts:
            latest_draft = json.dumps(section_drafts[-1] if isinstance(section_drafts, list) else section_drafts, indent=2)

    entry = (
        f"\n{'='*60}\n"
        f"TURN {turn_num}\n"
        f"{'='*60}\n"
        f"User: {user_message}\n"
        f"Routed To: {active}\n\n"
        f"Assistant:\n{assistant_msg}\n\n"
        f"Latest Draft ({active}):\n{latest_draft}\n\n"
        f"All Drafts So Far: {draft_keys}\n"
    )

    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    print(f"\n   State saved to {STATE_FILE}")
    print(f"   Results appended to {RESULTS_FILE}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python simulate_graph.py "your message here"')
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    run_turn(message)

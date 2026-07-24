import sys
sys.path.append('.')
from app.resume_tailoring_agent.graph import get_resume_agent_app

def test():
    app = get_resume_agent_app()
    config = {"configurable": {"thread_id": "e63581f6-6bf8-4e68-b2a8-a5eefd22b736"}}
    snapshot = app.get_state(config)
    
    if snapshot and snapshot.values:
        resume_content = snapshot.values.get("resume_content")
        print("Current resume_content:")
        import json
        print(json.dumps(resume_content, indent=2))
    else:
        print("No active snapshot found.")

if __name__ == "__main__":
    test()

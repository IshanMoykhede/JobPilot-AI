import sys
sys.path.append('.')
from app.resume_tailoring_agent.services.resume_execution_manager import ResumeExecutionManager

manager = ResumeExecutionManager()
state = manager.get_graph_state("a762af22-9e79-431b-9043-2f124e9b058b")

if state:
    print("State found!")
    print(f"Messages count: {len(state.get('messages', []))}")
    content = state.get("resume_content", {})
    if hasattr(content, 'sections'):
        print(f"Sections count: {len(content.sections)}")
    elif isinstance(content, dict):
        print(f"Sections count: {len(content.get('sections', []))}")
else:
    print("State is None!")

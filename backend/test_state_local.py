import sys
sys.path.append('.')
from app.resume_tailoring_agent.services.resume_execution_manager import ResumeExecutionManager

manager = ResumeExecutionManager()
state = manager.get_graph_state("a762af22-9e79-431b-9043-2f124e9b058b")

print(f"State type: {type(state)}")
if state:
    print(f"State boolean value: {bool(state)}")
    print(f"Keys: {state.keys() if isinstance(state, dict) else dir(state)}")
else:
    print("State is falsy or None")

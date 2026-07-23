import sys
sys.path.append('.')
import json
from app.resume_tailoring_agent.services.resume_execution_manager import ResumeExecutionManager

manager = ResumeExecutionManager()
state = manager.get_graph_state("a762af22-9e79-431b-9043-2f124e9b058b")

try:
    serialized = manager._serialize_state(state)
    print("Serialized successfully!")
    data = json.loads(serialized)
    print(f"Resume Content: {data.get('resume_content')}")
    print(f"Messages count: {len(data.get('messages', []))}")
except Exception as e:
    print(f"Error: {e}")

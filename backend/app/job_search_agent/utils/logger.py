import logging
import os
from datetime import datetime

# Define log directory at the root of the backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

# Generate a log file name based on the current date, or just a single growing log file
log_file = os.path.join(LOG_DIR, "job_search_agent.log")

agent_logger = logging.getLogger("job_search_agent")
agent_logger.setLevel(logging.DEBUG) # Set to DEBUG to capture detailed inputs/outputs

# File handler
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Formatter - captures timestamp, level, file where log originated, and message
formatter = logging.Formatter(
    fmt='%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)d] | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Prevent duplicate handlers if module is imported multiple times
if not agent_logger.handlers:
    agent_logger.addHandler(file_handler)
    
# Optional: also log to console so you can see it in terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
if len(agent_logger.handlers) == 1:
    agent_logger.addHandler(console_handler)

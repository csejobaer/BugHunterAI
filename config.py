import os

# Scanner settings
MAX_THREADS = 10
TIMEOUT = 10
DELAY = 0.5

# User Agent
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
]

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAYLOAD_DIR = os.path.join(BASE_DIR, "payloads")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Create directories
for dir_path in [PAYLOAD_DIR, REPORT_DIR, MODEL_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# AI Settings
AI_CONFIDENCE_THRESHOLD = 0.75

# Enabled modules
ENABLED_MODULES = ['sqli', 'xss', 'lfi', 'idor']
VULTR_API_KEY = 'V4MLLTDNI2GZHVHZ6PJQD3JTYMRLB6MQN37A'
VULTR_API_BASE = "https://api.vultrinference.com/v1"
VULTR_MODEL = 'llama-3.3-70b-instruct-fp8'

API_KEY = "gliksbot"  # Your API key (string)
API_HOST = "127.0.0.1"
API_PORT = 8080
import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
SKILLS_DIR = os.path.join(PROJECT_DIR, "skills_versions")

if not os.path.exists(SKILLS_DIR):
    os.makedirs(SKILLS_DIR)

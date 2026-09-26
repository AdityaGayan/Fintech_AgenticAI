import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory resolution
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "requirements.db"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
KB_DIR = DATA_DIR / "knowledge_base"

# Ensure core directories exist
DATA_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(exist_ok=True)
KB_DIR.mkdir(exist_ok=True)
(KB_DIR / "regulations").mkdir(exist_ok=True)
(KB_DIR / "policies").mkdir(exist_ok=True)

# Application Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Security Configurations
ALLOWED_ROLES = ["Admin", "Compliance_Officer", "Business_Analyst", "Project_Manager", "Stakeholder"]

# Updated to use Gemini and local HuggingFace embeddings
DEFAULT_LLM_MODEL = "gemini-3.8-flash" 
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
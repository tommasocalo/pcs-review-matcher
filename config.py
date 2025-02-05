# config.py
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# PCS credentials and URL
PCS_BASE_URL = os.getenv("PCS_BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
CONFERENCE_NAME = os.getenv("CONFERENCE_NAME", "CHI 2025")

# Flags
UPDATE_SUBMISSIONS = os.getenv("UPDATE_SUBMISSIONS", "false").lower() == "true"
EXPERT_ONLY = os.getenv("EXPERT_ONLY", "false").lower() == "true"

# Additional variables if needed
PPLX_API_KEY = os.getenv("PPLX_API_KEY")
EMAIL_TEMPLATE = os.getenv("EMAIL_TEMPLATE")

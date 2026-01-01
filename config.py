import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and URLs
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
ELSEVIER_API_KEY = os.getenv("ELSEVIER_API_KEY")

# LM Studio Configuration
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "local-model")

# Search Configuration
# "brain waves" or "EEG" related keywords
SEARCH_QUERY = 'EEG OR "brain waves" OR "brain-computer interface"'

# Fetch interval (seconds) - Default: 1 day (86400 seconds)
FETCH_INTERVAL_SECONDS = 86400

# Path to store notified paper IDs to avoid duplicates
SENT_PAPERS_LOG = "sent_papers.json"
# Path to store the last check timestamp
LAST_CHECK_FILE = "last_check.txt"

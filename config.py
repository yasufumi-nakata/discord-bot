import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and URLs
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
ELSEVIER_API_KEY = os.getenv("ELSEVIER_API_KEY")

# LM Studio Configuration
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "local-model"  # Default or specific model name if known

# Search Configuration
# "brain waves" or "EEG" related keywords
SEARCH_QUERY = '("brain waves" OR "EEG" OR "brain-computer interface" OR "electroencephalography")'

# Fetch interval (seconds) - Default: 30 minutes (1800 seconds)
FETCH_INTERVAL_SECONDS = 1800

# Path to store notified paper IDs to avoid duplicates
SENT_PAPERS_LOG = "sent_papers.json"
# Path to store the last check timestamp
LAST_CHECK_FILE = "last_check.txt"

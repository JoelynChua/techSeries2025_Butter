from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Ensure .env is loaded for SUPABASE_URL/KEY
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Table names
USERS_TABLE         = "users"
MOOD_TABLE          = "moodMetric"
FRIENDS_TABLE       = "friend"
QUIZQN_TABLE        = "quizqn"
LABEL_OPTIONS_TABLE = "label_options"
RANGE_CONFIG_TABLE  = "range_config"
MASCOT_TABLE        = "mascot"


def exec_data(response):
    """
    Normalize supabase-py response to a list (or value) and raise readable errors for older SDK shapes.
    """
    if hasattr(response, "data") and hasattr(response, "count"):
        return response.data
    elif isinstance(response, dict):
        if response.get("error"):
            err = response["error"]
            msg = err.get("message") if isinstance(err, dict) else str(err)
            raise Exception(msg)
        return response.get("data")
    else:
        return response

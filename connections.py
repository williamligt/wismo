import os
from sqlalchemy import create_engine
from pathlib import Path

DB = "DAGSTER_IO"
SCHEMA = "DS_DEV"

# Load environment variables from .env file only in development
if Path('.env').is_file():
    from dotenv import load_dotenv
    load_dotenv()

# check that these env vars are set
SF_ACCOUNT = os.getenv('sf-account')
SF_USERNAME = os.getenv('sf-username')
SF_PASSWORD = os.getenv('sf-password')
SF_ROLE = os.getenv('sf-role')
SF_WAREHOUSE = os.getenv('sf-warehouse')

if not all([SF_ACCOUNT, SF_USERNAME, SF_PASSWORD, SF_ROLE]):
    raise ValueError("Missing required Snowflake environment variables")

# Create engine once and reuse
_engine = None

def sf_engine():
    global _engine
    if _engine is None:
        user = SF_USERNAME
        pwd = SF_PASSWORD
        acct = SF_ACCOUNT           # e.g., abc12345.us-east-1
        wh = SF_WAREHOUSE
        role = SF_ROLE

        url = f"snowflake://{user}:{pwd}@{acct}/{DB}/{SCHEMA}"
        params = []
        if wh: params.append(f"warehouse={wh}")
        if role: params.append(f"role={role}")
        if params:
            url += "?" + "&".join(params)

        _engine = create_engine(url)
    return _engine
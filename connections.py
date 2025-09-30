import os
from sqlalchemy import create_engine

DB = "DAGSTER_IO"
SCHEMA = "DS_DEV"

SF_ACCOUNT = os.getenv('SF_ACCOUNT')
SF_USERNAME = os.getenv('SF_USERNAME')
SF_PASSWORD = os.getenv('SF_PASSWORD')
SF_ROLE = os.getenv('SF_ROLE')
SF_WAREHOUSE = os.getenv('SF_WAREHOUSE')

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
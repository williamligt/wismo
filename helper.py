from connections import DB, SCHEMA, sf_engine
import pandas as pd

def exists_in_original(order_number: str, conn) -> bool:
    """
    Check if the row exists in DAGSTER_IO.DS_DEV.CHURN_READ_SQL
    where ORDERNUMBER equals the given order_number.
    """
    # Compose the full table reference safely
    full_table = f"{DB}.{SCHEMA}.{'wismo_orders'}"
    sql = f"""
        SELECT 1
        FROM {full_table}
        WHERE ORIGINALORDERNUMBER = {order_number}
    """
    df = pd.read_sql(sql, conn)

    return not df.empty

def get_cartons(order_number: str, original: bool, conn) -> list:
    """
    Get the cartons from DAGSTER_IO.DS_DEV.CHURN_READ_SQL
    where ORDERNUMBER equals the given order_number.
    """
    if original:
        # Compose the full table reference safely
        full_table = f"{DB}.{SCHEMA}.{'wismo_cartons'}"
        sql = f"""
            SELECT *
            FROM {full_table}
            WHERE originalordernumber = {order_number}
        """

    else:
        # Compose the full table reference safely
        full_table = f"{DB}.{SCHEMA}.{'wismo_cartons'}"
        sql = f"""
            SELECT *
            FROM {full_table}
            WHERE postsplitordernumber = {order_number}
        """

    df = pd.read_sql(sql, conn)

    if df.empty:
        return []
    
    rows = [
        {k: str(v) for k, v in row.items()}
        for _, row in df.iterrows()
    ]

    return rows

def get_skus(order_number: str, original: bool, conn) -> list:
    """
    Get the skus from DAGSTER_IO.DS_DEV.wismo_skus
    where ORDERNUMBER equals the given order_number.
    """
    if original:
        # Compose the full table reference safely
        full_table = f"{DB}.{SCHEMA}.{'wismo_skus'}"
        sql = f"""
            SELECT *
            FROM {full_table}
            WHERE originalordernumber = {order_number}
        """

    else:
        # Compose the full table reference safely
        full_table = f"{DB}.{SCHEMA}.{'wismo_skus'}"
        sql = f"""
            SELECT *
            FROM {full_table}
            WHERE postsplitordernumber = {order_number}
        """
    df = pd.read_sql(sql, conn)

    rows = [
        {k: str(v) for k, v in row.items()}
        for _, row in df.iterrows()
    ]

    return rows

def get_orders(order_number: str, original: bool, conn) -> list:
    """
    Fetch rows from DAGSTER_IO.DS_DEV.wismo_orders
    where ORIGINALORDERNUMBER or POSTSPLITORDERNUMBER equals the given order_number.
    """
    full_table = f"{DB}.{SCHEMA}.{'wismo_orders'}"
    if original:
        sql = f"""
            SELECT *
            FROM {full_table}
            WHERE ORIGINALORDERNUMBER = {order_number}
        """
    else:
        sql = f"""
            SELECT *
            FROM {full_table}
            WHERE POSTSPLITORDERNUMBER = {order_number}
        """
    df = pd.read_sql(sql, conn)

    if df.empty:
        return []
    
    rows = [
        {k: str(v) for k, v in row.items()}
        for _, row in df.iterrows()
    ]
    return rows

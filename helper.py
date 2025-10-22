
from typing import Tuple
from connections import DB, SCHEMA, sf_engine
import pandas as pd
from custom_types import OrderNumber, Carton, Sku, Product
from constants import status_map
from cache import TTLCache

order_cache = TTLCache(ttl_hours=1)

def process_none(value):
    import pandas as pd
    if value == "None" or pd.isna(value):
        return None
    else:
        return value


def check_in_original(order_number: str, conn) -> bool:
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

def get_orders(order_number:int, conn) -> list:

    # Compose the full table reference safely
    full_table = f"{DB}.{SCHEMA}.{'wismo_orders'}"
    sql = f"""
        SELECT *
        FROM {full_table}
        WHERE postsplitordernumber = {order_number}
    """

    df = pd.read_sql(sql, conn)

    if df.empty:
        return []
    
    rows = [
        {k: v for k, v in row.items()}
        for _, row in df.iterrows()
    ]

    return rows

def original_order_query(order_number, conn):
    full_table = f"{DB}.{SCHEMA}.{'wismo_orders'}"
    sql = f"""
    SELECT *
    FROM {full_table}
    WHERE ORIGINALORDERNUMBER = {order_number}
    """
    df = pd.read_sql(sql, conn)

    rows = [
        {k: process_none(v) for k, v in row.items()}
        for _, row in df.iterrows()
    ]

    return rows

def get_skus(order_number, conn):
    # Compose the full table reference safely
    full_table = f"{DB}.{SCHEMA}.{'wismo_skus'}"
    sql = f"""
        SELECT *
        FROM {full_table}
        WHERE postsplitordernumber = {order_number}
    """
    df = pd.read_sql(sql, conn)

    rows = [
        {k: process_none(v) for k, v in row.items()}
        for _, row in df.iterrows()
    ]

    return rows

def get_cartons(order_number: str, conn) -> list:
    """
    Get the cartons from DAGSTER_IO.DS_DEV.CHURN_READ_SQL
    where ORDERNUMBER equals the given order_number.
    """

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
        {k: process_none(v) for k, v in row.items()}
        for _, row in df.iterrows()
    ]

    return rows

def get_products(skus: list, conn) -> list:
    """
    Get the products from DAGSTER_IO.DS_DEV.WISMO_PRODUCTS
    where skus is a list of the skus.
    """
    
    if not skus:
        return []
    
    # Compose the full table reference safely
    full_table = f"{DB}.{SCHEMA}.{'wismo_products'}"
    
    # Create placeholders for the IN clause
    sku_list ="'" +  "','".join(skus) + "'"
    sql = f"""
        SELECT *
        FROM {full_table}
        WHERE PROD_SKU IN ({sku_list})
    """
    
    try:
        df = pd.read_sql(sql, conn)
        print(f"Query executed successfully. Rows returned: {len(df)}")
        print(f"DataFrame: {df}")
    except Exception as e:
        print(f"Error executing query: {e}")
        return []
    
    products = []

    rows = [
        {k: process_none(v) for k, v in row.items()}
        for _, row in df.iterrows()
    ]

    for item in rows:
        product = Product(
            sku=item.get("prod_sku"),
            hfaDescription=item.get("prod_hfadescription1"),
            manufacturerName=item.get("prod_manufacturername")
        )

        products.append(product)
    

    return products



def process_order_number(order_number: int, conn) -> list:
    """
    recursively creates a list of all the 
    orders that match the order number, includes all the split orders
    for which the function is run again until there are no more split
    orders
    """
    # Check cache first
    cache_key = f"order_{order_number}"
    cached_result = order_cache.get(cache_key)
    if cached_result is not None:
        print(f"Cache hit for order {order_number}")
        return cached_result
    
    print(f"Cache miss for order {order_number} - querying database")


    # create an empty list to hold OrderNumber objects
    order_list = []

    # all order numbers might have multiple orders due to back order levels
    # we will treat all backorder levels as separate orders

    orders = get_orders(order_number, conn)

    exists_in_original = check_in_original(order_number, conn)

    # snowflake query to get all the skus under
    skus = get_skus(order_number, conn)

    # query snowflake to get all the cartons under the postsplitordernumber 
    cartons = get_cartons(order_number, conn)
    
    # iterate through each order that appears under the postsplitordernumber
    for order in orders:

        sku_list = []
        # for each order get all the skus that are for it
        for sku in skus:
            if sku['postsplitordernumber'] == order['postsplitordernumber'] and sku['ordersuffix'] == order['ordersuffix']:
                pick_qty = None if sku["pickqty"] is None else int(float(sku["pickqty"]))
                sku_list.append(
                    Sku(
                        orderNumber=int(sku["postsplitordernumber"]),
                        orderSuffix=sku["ordersuffix"],
                        sku=sku["sku"],
                        pickQty=pick_qty
                    )
                )

        # for each order
        carton_list = []

        # for each carton we add to list of cartons but only if it matches the 
        for carton in cartons:
            carton_sku_list = []
            for sku in skus:
                if sku['postsplitordernumber'] == carton["postsplitordernumber"] and sku["ordersuffix"] == carton["ordersuffix"]:
                    pick_qty = None if sku["pickqty"] is None else int(float(sku["pickqty"]))
                    carton_sku_list.append(
                        Sku(
                            orderNumber=sku["postsplitordernumber"],
                            orderSuffix=sku["ordersuffix"],
                            sku=sku["sku"],
                            pickQty=pick_qty
                        )
                    )

            if carton['postsplitordernumber'] == order['postsplitordernumber'] and carton['ordersuffix'] == order['ordersuffix']:
                carton_list.append(
                    Carton(
                        orderNumber=carton["postsplitordernumber"],
                        orderSuffix=carton['ordersuffix'],
                        cartonId=carton["cartonid"],
                        deliveryStatusDescription=carton["deliverystatusdescription"],
                        actualDeliveryDate=carton["actualdeliverydate"],
                        expectedDeliveryDate=carton["expecteddeliverydate"],
                        carrierCode=carton["carriercode"],
                        carrierDescription=carton["carrierdescription"],
                        traceAndTraceLink=carton["trace_and_trace_link"],
                        skus=carton_sku_list
                    )
                )

        if exists_in_original:
            # make snowflake query to query the original order column
            split_orders = original_order_query(order_number, conn)
            split_order_list = []
            for order in split_orders:
                split_order_list.extend(process_order_number(order['postsplitordernumber'], conn))
        else:
            split_order_list=None
        
        order_list.append(
            OrderNumber(
                orderNumber=order_number,
                orderBookedDate=order['orderbookeddate'],
                orderSuffix=order['ordersuffix'],
                orderStatus=status_map.get(order['orderstatus'], order['orderstatus']),  # Map the status using status_map
                orderContactFullName=order['ordercontactfullname'],
                contactEmailAddress=order['contactemailaddress'],
                contactPhone=order['contactphone'],
                shipTo=order['shipto'],
                shipToName=order['shiptoname'],
                splitOrders=split_order_list,
                skus=sku_list,
                cartons=carton_list
                ))
    # Cache the result
    order_cache.set(cache_key, order_list)    
    return order_list

def run(order_number, sf_engine = sf_engine):
    with sf_engine().connect() as conn:
        order_data = process_order_number(order_number, conn)
    return order_data

def run_get_products(skus: list, sf_engine = sf_engine):
    try:
        with sf_engine().connect() as conn:
            product_data = get_products(skus, conn)
        return product_data
    except Exception as e:
        print(f"Error in run_get_products: {e}")
        raise Exception(f"Failed to get products: {str(e)}")
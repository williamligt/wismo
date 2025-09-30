# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
import os
import pandas as pd
from helper import exists_in_original, get_orders, get_cartons, get_skus
from email_generator import generate_email
from connections import sf_engine
import sys
import time

def run(order_number: str):
    """
    Return the row from DAGSTER_IO.DS_DEV.wismo_orders
    where ORDERNUMBER equals the given order_number.
    """
    
    with sf_engine().connect() as conn:
        exists_in_original_flag = exists_in_original(order_number, conn)
        orders = get_orders(order_number, exists_in_original_flag, conn)
        cartons = get_cartons(order_number, exists_in_original_flag, conn)
        skus = get_skus(order_number, exists_in_original_flag, conn)
    
    email = generate_email(order_number, orders, cartons, skus, exists_in_original_flag)
    
    return {
        "email": email,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python wismo.py <order_number>")
    else:
        result = run(sys.argv[1])
        print(result)
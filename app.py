# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
import os
import pandas as pd
from utils.helper import run, run_get_products
from fastapi import FastAPI, HTTPException
import uvicorn
from typing import List
from utils.custom_types import OrderNumber, ProductRequest, Product
from utils.connections import sf_engine
from sqlalchemy import text
from utils.email_generator import generate_order_email
from fastapi import Path

app = FastAPI(
    title="Wismo Order API",
    description="API for retrieving order information",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Wismo API. Use /order_number to get email data."}

@app.get("/health")
def health_check():
    try:
        # Test database connection
        engine = sf_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.get("/{order_number}", response_model=List[OrderNumber])
def get_order(order_number: str = Path(...,example='533212')):
    try:
        result = run(order_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/email/{order_number}")
def get_email(order_number: str = Path(...,example='533212')):
    try:
        results = run(order_number)
        if not results:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Since the API returns a list, we'll generate an email for the first order
        # You might want to adjust this logic based on your needs
        main_order = results[0]
        return generate_order_email(main_order)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/products/", response_model=List[Product])    
def get_products(request: ProductRequest):
    try:
        return run_get_products(request.skus)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
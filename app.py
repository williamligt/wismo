# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
import os
import pandas as pd
from helper import run
from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()

@app.get("/email/{order_number}")
async def get_email(order_number: str):
    try:
        result = run(order_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
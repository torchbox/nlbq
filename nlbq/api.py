from typing import Union
from fastapi import FastAPI
import uvicorn

from nlbq.core import NLBQ

# Todo: move to config file
UVICORN_HOST = "127.0.0.1"
UVICORN_PORT = 8000

app = FastAPI()

@app.get("/api/dry_run")
async def dry_run(q: Union[str, None] = None):
    """Process a text query and return the SQL statement, results, and explanation."""
    nlbq = NLBQ()
    statement = await nlbq.text_to_bq(q)
    data, qpm = nlbq.dry_run(statement)
    return {
        "response": {
            "statement": statement,
            "data": data,
            "qpm": qpm,
        }
    }

def serve():
    uvicorn.run("nlbq.api:app", host=UVICORN_HOST, port=UVICORN_PORT, workers=1)
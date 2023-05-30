from typing import Union
from fastapi import FastAPI
import uvicorn

from nlbq.config import get_settings
from nlbq.core import NLBQ

settings = get_settings()

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
    uvicorn.run("nlbq.api:app", host=settings.uvicorn_host, port=settings.uvicorn_port, workers=1)

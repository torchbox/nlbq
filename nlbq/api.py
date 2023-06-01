import uvicorn
from fastapi import FastAPI

from nlbq.config import get_settings
from nlbq.core import NLBQ

settings = get_settings()

app = FastAPI()


@app.get("/api/dry_run")
async def dry_run(q: str):
    """Process a text query and return the SQL statement, results, and explanation."""
    nlbq = NLBQ()
    statement = await nlbq.text_to_bq(q)

    bytes_info = nlbq.dry_run(statement)
    return {
        "response": {
            "statement": statement,
            "data": bytes_info.human_bytes,
            "qpm": bytes_info.queries_per_month,
        }
    }


def serve():
    uvicorn.run(
        "nlbq.api:app",
        host=settings.uvicorn_host,
        port=settings.uvicorn_port,
        workers=1,
    )

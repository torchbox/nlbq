import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from tabulate import tabulate

from nlbq.core import NLBQ

# Todo: move to config file
UVICORN_HOST = "127.0.0.1"
UVICORN_PORT = 8000

app = FastAPI()


class DryRunResp(BaseModel):
    statement: str
    data: str
    qpm: int


class StatementReq(BaseModel):
    statement: str
    question: str


class StatementResp(BaseModel):
    text_results: str
    html_results: str


class AnswerReq(BaseModel):
    question: str
    statement: str
    results: str


@app.get("/api/dry_run")
async def dry_run(q: str) -> DryRunResp:
    """Process a text query and return the SQL statement, results, and explanation."""
    nlbq = NLBQ()
    statement = await nlbq.text_to_bq(q)
    data, qpm = nlbq.dry_run(statement)
    return DryRunResp(statement=statement, data=data, qpm=qpm)


@app.post("/api/run_statement")
async def run_statement(request_data: StatementReq) -> StatementResp:
    nlbq = NLBQ()
    fields, rows = nlbq.execute(request_data.statement)
    return StatementResp(
        text_results=tabulate(rows, headers=fields),
        html_results=tabulate(rows, headers=fields, tablefmt="html"),
    )


@app.post("/api/answer")
async def answer(request_data: AnswerReq):
    nlbq = NLBQ()
    resp = await nlbq.answer(
        request_data.question, request_data.statement, request_data.results
    )
    return {"answer": resp}


@app.get("/")
async def serve_index():
    """Serve index.html"""
    return FileResponse("index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")


def serve():
    uvicorn.run("nlbq.api:app", host=UVICORN_HOST, port=UVICORN_PORT, workers=1)

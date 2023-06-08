import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from tabulate import tabulate

from nlbq.config import get_settings
from nlbq.core import NLBQ

settings = get_settings()

app = FastAPI()

# Allow all origins
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DryRunRequest(BaseModel):
    question: str
    model: str


class DryRunResponse(BaseModel):
    statement: str
    data: str
    qpm: int
    gpt_cost: float


class StatementRequest(BaseModel):
    statement: str
    question: str


class StatementResponse(BaseModel):
    text_results: str
    html_results: str


class AnswerRequest(BaseModel):
    question: str
    statement: str
    results: str


@app.post("/api/dry_run")
async def dry_run(request_data: DryRunRequest) -> DryRunResponse:
    """Process a text query and return a SQL statement, results, and explanation."""
    nlbq = NLBQ(model=request_data.model)
    statement, cost = await nlbq.text_to_bq(request_data.question)
    bytes_info = nlbq.dry_run(statement)
    return DryRunResponse(
        statement=statement,
        data=bytes_info.human_bytes,
        qpm=bytes_info.queries_per_month,
        gpt_cost=cost,
    )


@app.post("/api/run_statement")
async def run_statement(request_data: StatementRequest) -> StatementResponse:
    """Execute a SQL statement and return the results in HTML and plain text formats."""
    nlbq = NLBQ()
    fields, rows = nlbq.execute(request_data.statement)
    return StatementResponse(
        text_results=tabulate(rows, headers=fields),
        html_results=tabulate(rows, headers=fields, tablefmt="html"),
    )


@app.post("/api/answer")
async def answer(request_data: AnswerRequest):
    """Explain the results, using the supplied question and results."""
    nlbq = NLBQ()
    resp = await nlbq.answer(
        request_data.question, request_data.statement, request_data.results
    )
    return {"answer": resp}


@app.get("/")
async def serve_index():
    """Serve index.html"""
    return FileResponse("index.html")


def serve():
    uvicorn.run(
        "nlbq.api:app",
        host=settings.uvicorn_host,
        port=settings.uvicorn_port,
        workers=1,
    )

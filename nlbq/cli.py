import sys

import typer
from tabulate import tabulate

from nlbq.core import NLBQ, DEFAULT_MODEL

app = typer.Typer()


@app.command()
def ask(query: str, model: str = DEFAULT_MODEL) -> str:
    """Convert question to BQ query, report on bytes used, offer to execute"""
    nlbq = NLBQ(model=model)
    print(f"Converting your question to a BigQuery query, using {nlbq.model}..." "")
    statement = nlbq.text_to_bq(query)
    print(f"\n{statement}\n")
    data, qpm = nlbq.dry_run(statement)
    print(
        f"This query will process {data}.",
        f"You could run {qpm} queries like this per month.",
    )
    if input("Do you want to run it? (Y/n) ").lower() not in ["y", ""]:
        sys.exit(0)
    fields, rows = nlbq.execute(statement)
    print("\n" + tabulate(rows, headers=fields, tablefmt="pipe") + "\n")


@app.command()
def init():
    """Create stub files: prompt.txt, index.html, Dockerfile"""
    print("Todo")


@app.command()
def serve():
    """Start a FastAPI server"""
    print("Todo")


def cli_wrapper():
    """Wrapper for flit entrypoint"""
    app()


if __name__ == "__main__":
    cli_wrapper()

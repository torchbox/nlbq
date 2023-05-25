import sys
import typer
from nlbq.core import NLBQ
from tabulate import tabulate

app = typer.Typer()

@app.command()
def ask(query: str):
    """Convert question to BQ query, report on bytes used, offer to execute"""
    nlbq = NLBQ()
    statement = nlbq.text_to_bq(query)
    print(f"Statement: {statement}")
    human_bytes, queries_per_month = nlbq.dry_run(statement)
    print(
        f"This query will process {human_bytes}.",
        f"You could run {queries_per_month} queries like this per month.",
    )
    if input("Do you want to run it? (Y/n) ").lower() not in ["y", ""]:
        sys.exit(0)
    field_names, rows = nlbq.execute(statement)
    print("\n" + tabulate(rows, headers=field_names, tablefmt="pipe") + "\n")

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
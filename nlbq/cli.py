import sys
from asyncio import run
from functools import wraps

import typer
from tabulate import tabulate

from nlbq.api import serve as api_serve
from nlbq.core import DEFAULT_MODEL, NLBQ


class AsyncTyper(typer.Typer):
    """
    A subclass of Typer that allows async functions to be used as commands
    https://github.com/tiangolo/typer/issues/88#issuecomment-1478432421
    """

    def async_command(self, *args, **kwargs):
        def decorator(async_func):
            @wraps(async_func)
            def sync_func(*_args, **_kwargs):
                return run(async_func(*_args, **_kwargs))

            self.command(*args, **kwargs)(sync_func)
            return async_func

        return decorator


app = AsyncTyper()


@app.async_command()
async def ask(query: str, model: str = DEFAULT_MODEL) -> str:
    """Convert question to BQ query, report on bytes used, offer to execute"""
    nlbq = NLBQ(model=model)
    print(f"Converting your question to a BigQuery query, using {nlbq.model}..." "")
    statement = await nlbq.text_to_bq(query)
    print(f"\n{statement}\n")

    data = nlbq.dry_run(statement)
    print(
        f"This query will process {data.human_bytes}.",
        f"You could run {data.queries_per_month} queries like this per month.",
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
    api_serve()


def cli_wrapper():
    """Wrapper for flit entrypoint"""
    app()


if __name__ == "__main__":
    cli_wrapper()

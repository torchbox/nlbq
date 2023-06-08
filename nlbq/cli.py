import shutil
import sys
from asyncio import run
from functools import wraps
from pathlib import Path
from typing import Annotated

import typer
from tabulate import tabulate

from nlbq.api import serve as api_serve
from nlbq.core import DEFAULT_MODEL, NLBQ
from nlbq.helpers import generate_prompt_from_dataset_table


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
    statement, cost = await nlbq.text_to_bq(query)
    print(f"\n{statement}\n")
    data = nlbq.dry_run(statement)
    print(
        f"This query will process {data.human_bytes}.",
        f"You could run {data.queries_per_month} queries like this per month.",
        f"Building this query cost ${cost:.4f}.",
    )
    if input("Do you want to run it? (Y/n) ").lower() not in ["y", ""]:
        sys.exit(0)
    fields, rows = nlbq.execute(statement)
    print("\n" + tabulate(rows, headers=fields, tablefmt="pipe") + "\n")


def validate_table_format(table_in_dataset: str) -> str:
    """Validate dataset format"""    
    if table_in_dataset and "." not in table_in_dataset:
        raise typer.BadParameter(
            "The target table value must be in the format dataset.table_id"
        )
    return table_in_dataset


@app.command()
def init(
    table_in_dataset: Annotated[
        str,
        typer.Option(
            "--table",
            "-t",
            help="The target table in the form of dataset.table_id",
            callback=validate_table_format,
        ),
    ] = None
):
    """Create stub files: prompt.txt, index.html, Dockerfile"""
    package_dir = Path(__file__).parent
    current_dir = Path.cwd()
    prefix_success = typer.style("✔", fg=typer.colors.GREEN, bold=True)
    prefix_error = typer.style("✘", fg=typer.colors.RED, bold=True)

    for file in ["Dockerfile", "index.html"]:
        dest = current_dir / file
        if dest.exists():
            typer.echo(f"{prefix_error} {file} already exists here")
            raise typer.Abort()
        else:
            shutil.copyfile(package_dir / "templates" / file, dest)
            typer.echo(f"{prefix_success} Created {file} at {dest}")

    prompt_file = current_dir / "prompt.txt"
    if prompt_file.exists():
        typer.echo(f"{prefix_error} {file} already exists here")
        raise typer.Abort()

    if table_in_dataset:
        shutil.copyfile(package_dir / "templates" / "prompt_template.txt", prompt_file)
        print(f"⠹ Creating prompt.txt using {table_in_dataset}", end="\r")
        generate_prompt_from_dataset_table(table_in_dataset, prompt_file, NLBQ())
    else:
        shutil.copyfile(package_dir / "templates" / "prompt.txt", prompt_file)

    typer.echo(f"{prefix_success} Created prompt.txt at {prompt_file}")


@app.command()
def serve():
    """Start a FastAPI server"""
    api_serve()


def cli_wrapper():
    """Wrapper for flit entrypoint"""
    app()


if __name__ == "__main__":
    cli_wrapper()

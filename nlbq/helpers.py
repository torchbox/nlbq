import json
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nlbq.core import NLBQ


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime | date):
            return o.isoformat()
        return super().default(o)


def generate_prompt_from_dataset_table(
    table_in_dataset: str, prompt_file: Path, nlbq: "NLBQ"
):
    """Generate a prompt file from a dataset and table"""
    dataset_id, table_id = table_in_dataset.split(".")

    fields = {
        field.name: str(field)
        for field in nlbq.client.get_table(table_in_dataset).schema
    }

    column_description_glue = ": add column description here\n"
    content = prompt_file.read_text()
    updated_content = (
        content.replace("{{ project_id }}", nlbq.client.project)
        .replace("{{ dataset }}", dataset_id)
        .replace("{{ table_id }}", table_id)
        .replace("{{ schema }}", "\n".join(fields.values()))
        .replace(
            "{{ columns }}",
            column_description_glue.join(fields.keys()) + column_description_glue,
        )
    )

    preview_rows = list(nlbq.client.list_rows(table_in_dataset, max_results=3))
    preview = json.dumps(
        [dict(row) for row in preview_rows], indent=2, cls=CustomJsonEncoder
    )
    updated_content = updated_content.replace("{{ sample_data }}", preview)

    prompt_file.write_text(updated_content)

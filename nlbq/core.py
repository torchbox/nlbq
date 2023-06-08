import openai
from google.cloud import bigquery
from pydantic import BaseModel

from nlbq.config import get_settings

DEFAULT_MODEL = "gpt-3.5-turbo"

settings = get_settings()


class BytesInfo(BaseModel):
    bytes_used: int
    human_bytes: str
    queries_per_month: int


def get_bytes_info(bytes_used: int) -> BytesInfo:
    """Convert bytes into human readable figure, calculate queries per month"""
    if bytes_used < 1000000:
        human_bytes = f"{bytes_used/1000:.2f}KB"
    else:
        human_bytes = f"{bytes_used/1000000:.2f}MB"
    free_tier_bytes_per_month = 1024**4  # 1TB
    queries_per_month = free_tier_bytes_per_month // bytes_used
    return BytesInfo(
        bytes_used=bytes_used,
        human_bytes=human_bytes,
        queries_per_month=queries_per_month,
    )


def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    MODEL_COSTS = {
        "gpt-3.5-turbo": {"prompt": 0.002 / 1000, "completion": 0.002 / 1000},
        "gpt-4": {"prompt": 0.03 / 1000, "completion": 0.06 / 1000},
    }
    if model not in MODEL_COSTS:
        raise ValueError(f"Unknown model: {model}")
    costs = MODEL_COSTS[model]
    return (prompt_tokens * costs["prompt"]) + (completion_tokens * costs["completion"])


class NLBQ:
    """Natural language to BigQuery methods"""

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.prompt_template = self.get_prompt_template()
        self.client = bigquery.Client.from_service_account_json(
            settings.google_application_credentials
        )

    def get_prompt_template(self) -> str:
        """returns the prompt template as a string, with comments removed"""
        lines = open(settings.prompt_template_file).read().split("\n")
        uncommented_lines = [line for line in lines if not line.strip().startswith("#")]
        return "\n".join(uncommented_lines).strip()

    async def text_to_bq(self, question: str) -> tuple:
        """Use an LLM to convert a question into a BigQuery SQL query"""
        prompt_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": self.prompt_template % question},
        ]
        resp = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=prompt_messages,
            temperature=0,
            api_key=settings.openai_api_key,
        )

        usage = resp["usage"]
        statement = resp["choices"][0]["message"]["content"].strip()
        cost = calculate_cost(
            usage["prompt_tokens"], usage["completion_tokens"], self.model
        )
        return (statement, cost)

    def dry_run(self, query: str) -> BytesInfo:
        """Report on the data this query would use"""
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        query_job = self.client.query(query, job_config=job_config)
        return get_bytes_info(query_job.total_bytes_processed)

    def execute(self, query: str) -> tuple:
        """Execute the query, return the results"""
        bq_query = self.client.query(query)
        results = bq_query.result()
        field_names = [field.name for field in results.schema]
        rows = [row.values() for row in results]
        return field_names, rows

    async def answer(self, question, statement, results) -> str:
        prompt_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": self.prompt_template % question},
            {"role": "assistant", "content": statement},
            {
                "role": "system",
                "content": "The SQL statement returned the following results:\n\n"
                + results,
            },
            {
                "role": "system",
                "content": f"Using these results, answer the question: {question}",
            },
            {
                "role": "system",
                "content": "Don't say what the query was, just answer the question.",
            },
        ]
        resp = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=prompt_messages,
            temperature=0,
        )
        return resp["choices"][0]["message"]["content"].strip()

# nlbq
Natural language interface to BigQuery

## Google credentials

The Python BigQuery library expects the environment variable `GOOGLE_APPLICATION_CREDENTIALS`, which should point to a JSON file containing the credentials of a Google service account. You can create a service account and download its credentials from the [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts). Then set the environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/google-service-account.json
```

## Creating a demo environment

```bash
mkdir demo # Git will ignore this directory
cd demo
python3 -m venv venv
source venv/bin/activate
pip install -e ../ # Install the local package in editable mode
nlbq init  # generates prompt.txt, Dockerfile and index.html
# make changes then
pip uninstall nlbq --yes; pip install -e ../
```

You can initialise with prepopulated BigQuery dataset table schema information with

```bash
nlbq init --table dataset.table_id
```

## Usage

```bash
nlbq --help
```

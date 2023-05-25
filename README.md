# nlbq
Natural language interface to BigQuery

## Creating a demo environment

```bash
mkdir demo # Git will ignore this directory
python3 -m venv venv
source venv/bin/activate
pip install -e ../ # Install the local package in editable mode
nlbq init
# make changes then
pip uninstall nlbq --yes; pip install -e ../
```
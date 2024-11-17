# rag-streamlit-app

An open example retrieval augmented generation app for questioning your data.

## Prerequisites

You must have a pre-running instance of OpenSearch.

Also create a local `.env` file containing the needed arguments like so:

```commandline
cp .env.template .env
```

## Getting started: WebApp

Using a venv (Virtual Environment) perform the following install steps.

```commandline
pip install --upgrade pip
pip install poetry
poetry install
streamlit run rag-webapp/main.py
```
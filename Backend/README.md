# Mesh Compliance Core

Advanced title compliance and verification engine.

## Structure

- `app/api`: FastAPI routes and request models.
- `app/compliance`: Validation rules and engines.
- `app/intelligence`: AI/ML similarity engines.
- `app/orchestration`: Control flow.
- `app/persistence`: Database and repositories.
- `app/monitoring`: Logging and performance.

## Setup

1. Create virtualenv: `python -m venv venv`
2. Install requirements: `pip install -r requirements.txt`
3. Run app: `uvicorn app.main:app --reload`

# Task Tracker API - Module 1

Minimal FastAPI skeleton for the Module 1 Task Tracker learning project.

Currently exposes a health check endpoint only. CRUD endpoints, authentication,
database implementation, Docker, deployment, and the frontend are out of scope
for this step.

## Structure

    app/
      api/      HTTP routes
      core/     configuration and shared settings
      models/   Pydantic models (added later)
      storage/  persistence layer and tasks.json
    tests/      pytest suite

## Setup

    cd C:\Users\wadih\OneDrive\Desktop\AUB\proj\task-tracker-api
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    Copy-Item .env.example .env

## Run

    python -m uvicorn app.main:app --reload --port 8000

## Test the health endpoint

    curl.exe http://127.0.0.1:8000/health

Expected response:

    {"status":"ok","timestamp":"2026-07-26T10:00:00.000000+00:00"}

## Swagger UI

    http://127.0.0.1:8000/docs

## Run the test suite

    python -m pytest

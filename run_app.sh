#!/bin/bash
# Script to activate virtual environment and run the FastAPI application

# Activate virtual environment
source salon_venv/bin/activate

# Run the FastAPI application
uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
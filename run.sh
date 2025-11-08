#!/bin/bash

# CycleGuard AI Startup Script

echo "Starting CycleGuard AI..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Please create one from .env.example"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please update .env with your credentials"
fi

# Create uploads directory
mkdir -p uploads

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting FastAPI server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000


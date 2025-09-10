#!/bin/bash
# Start script for Smart Meeting Minutes Generator (Unix/Linux/macOS)

echo "Smart Meeting Minutes Generator - Starting Application"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup first:"
    echo "python setup.py"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Some features may not work."
    echo "Please create .env file with your HuggingFace token."
fi

# Start the application
echo "Starting FastAPI server..."
echo "Access the application at: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

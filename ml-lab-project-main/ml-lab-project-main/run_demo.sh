#!/bin/bash

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    echo ""
    echo "======================================================="
    echo "uv has been installed! Rebooting terminal session..."
    echo "======================================================="
    echo ""
    
    # Re-exec into a new login shell to refresh PATH and re-run this script
    exec bash -l -c "$0"
    exit 0
fi

echo "Setting up environment and installing demo dependencies..."
uv venv
source .venv/bin/activate
uv pip install -r requirements_demo.txt

echo "Opening the application in the browser..."
# Wait 2 seconds for the server to start, then open the browser
if command -v xdg-open &> /dev/null; then
    (sleep 2 && xdg-open http://127.0.0.1:8050) &
elif command -v open &> /dev/null; then
    (sleep 2 && open http://127.0.0.1:8050) &
fi

echo "Running the Demo..."
uv run app.py

#!/bin/bash

echo "=== AirCursor Installer ==="

echo "Installing system dependencies..."
sudo dnf install -y python3-tkinter ydotool

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Installation completed!"
echo ""
echo "To run:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "Note: Run 'ydotoold --socket-perm 666 &' manually the first time if needed."

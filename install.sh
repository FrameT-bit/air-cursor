#!/bin/bash
echo "========================================"
echo "       AirCursor Installer"
echo "========================================"

echo "Installing system dependencies..."
sudo dnf install -y python3-tkinter ydotool

echo "Creating virtual environment..."
python3 -m venv venv

echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setting up ydotool permissions..."

# Add user to input group
if ! groups | grep -q "input"; then
    echo "Adding your user to the 'input' group..."
    sudo usermod -a -G input $USER
    echo "✅ User added to input group."
    echo "   ⚠️  You MUST reboot your computer for permissions to take effect."
else
    echo "✅ Your user is already in the input group."
fi

# Temporary permission (for immediate use)
sudo chmod 666 /dev/uinput 2>/dev/null || true

echo ""
echo "✅ Installation completed!"
echo ""
echo "To run AirCursor:"
echo "   1. Reboot your computer (required for permissions)"
echo "   2. source venv/bin/activate"
echo "   3. python main.py"
echo ""
echo "Tip: You can add 'ydotoold --socket-perm 666 &' to your ~/.bashrc"

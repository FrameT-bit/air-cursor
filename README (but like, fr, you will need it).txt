# AirCursor

**AirCursor** is a gesture-based mouse control system for Linux (Fedora/GNOME Wayland). It allows you to control your computer using hand gestures through your webcam — no extra hardware required.

## Features

- Smooth mouse movement with index finger
- Left click via thumb + index pinch
- Two gesture menus (Media and Navigation)
- Clean floating overlay interface
- Headless operation (no permanent camera window)
- Runs silently in background

## Gestures

### Basic Control
- **Move mouse**: Point with your index finger (hand open)
- **Left click**: Pinch thumb and index finger

### Menu System
- **Menu 1 (Media)**: Raise only index finger (hand open) → close fist to open menu
- **Menu 2 (Navigation)**: Raise index + middle finger (hand open) → close fist to open menu

**Inside any menu**:
- Move hand up/down with fist closed to select option
- Open hand to confirm and execute the selected action

## Installation

```bash
git clone https://github.com/FrameT-bit/air-cursor.git
cd air-cursor
chmod +x install.sh
./install.sh

Then run (inside the folder):
source venv/bin/activate
python main.py

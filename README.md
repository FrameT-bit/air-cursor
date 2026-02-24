# air-cursor
**AirCursor! Hand gesture mouse control for Linux (Fedora/Wayland/Or anything that has a camera and can run python). Control your computer with natural hand gestures using only your webcam.**

Built after staying up all night instead of playing Minecraft because I saw a bunch of jarvis videos on instagram.

### How it works

- **Open hand with index finger pointing** = normal smooth mouse mode  
- **Raise only index finger** (hand still open) = preparing Media Menu  
- **Raise index + middle finger** (hand still open) = preparing Navigation Menu  
- **Close fist** = open the menu  
- **Move hand up/down with fist closed** = select option  
- **Open hand** = confirm action and return to normal mouse mode

### Current Menus

**Menu 1 - Media**
- Volume +
- Volume -
- Play/Pause
- Next
- Previous

**Menu 2 - Navigation**
- Page Up
- Page Down
- Alt+Tab
- Minimize
- Close Window

### Installation

```bash
git clone https://github.com/FrameT-bit/air-cursor.git
cd air-cursor
chmod +x install.sh
./install.sh
```
Then run:
```bash
source venv/bin/activate
python main.py
```

### Important Notes

Works best with good lighting
Optimized for right hand (also tested on left hand)
Tested on Fedora 43 + Wayland
Still a personal project, works great for me, but may need some tuning for you.

Made with caffeine.

Want to contribute? Pull requests are welcome.
Want to complain? Also welcome!

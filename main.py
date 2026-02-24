import cv2
import mediapipe as mp
import subprocess
import time
import tkinter as tk
import os
import atexit
import numpy as np
import sys

# ==================== VENV CHECK ====================
if sys.prefix == sys.base_prefix:
    print("WARNING: You are not running inside a virtual environment.")
    print("It is strongly recommended to activate the venv first:")
    print("   source venv/bin/activate")
    print("")

# ==================== ANTI-SPAM LOCK ====================
LOCK_FILE = "/tmp/air_cursor.lock"
if os.path.exists(LOCK_FILE):
    try:
        with open(LOCK_FILE, 'r') as f:
            os.kill(int(f.read().strip()), 9)
    except:
        pass
    os.remove(LOCK_FILE)

with open(LOCK_FILE, 'w') as f:
    f.write(str(os.getpid()))
atexit.register(lambda: os.path.exists(LOCK_FILE) and os.remove(LOCK_FILE))

os.environ["QT_QPA_PLATFORM"] = "xcb"

# had to add this because there was a problem with dead processes spamming windows like crazy

# ==================== YDOTOOL AUTO START ====================
subprocess.run(['pkill', '-9', 'ydotoold'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.5)
subprocess.Popen(['ydotoold', '--socket-perm', '666'])
time.sleep(1.5)

# ==================== SCREEN RESOLUTION ====================
try:
    root = tk.Tk()
    SCREEN_WIDTH = root.winfo_screenwidth()
    SCREEN_HEIGHT = root.winfo_screenheight()
    root.destroy()
except:
    SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080

# ==================== MEDIAPIPE SETUP ====================
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.8,
    min_tracking_confidence=0.8
)

# ==================== SETTINGS ====================
SMOOTH = 0.89
DEADZONE = 5
PINCH_THRESHOLD = 0.052

prev_x = prev_y = 0
locked_x = locked_y = 0
is_clicking = False
last_action_time = 0

# ==================== MENU STATE ====================
menu_state = "neutral"   # neutral, preparing1, preparing2, menu1, menu2
menu_selection = 0
menu_start_y = 0

MENU1_OPTIONS = ["Volume +", "Volume -", "Play/Pause", "Next", "Previous"]
MENU2_OPTIONS = ["Page Up", "Page Down", "Alt+Tab", "Minimize", "Close Window"]

def count_extended_fingers(landmarks):
    count = 0
    if landmarks[8].y < landmarks[6].y - 0.03: count += 1
    if landmarks[12].y < landmarks[10].y - 0.03: count += 1
    return count

print("AirCursor started.")

if not os.path.exists("hand_landmarker.task"):
    print("Downloading model file (first time only, ~70MB)...")
    subprocess.run(["wget", "-q", "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"])

print("Ctrl + C to stop.\n")

# ==================== TKINTER OVERLAY ====================
root = tk.Tk()
root.withdraw()

overlay = tk.Toplevel(root)
overlay.title("AirCursor")
overlay.geometry("520x460")
overlay.configure(bg="#0f0f0f")
overlay.attributes("-topmost", True)
overlay.overrideredirect(True)
overlay.attributes("-alpha", 0.96)

canvas = tk.Canvas(overlay, width=520, height=460, bg="#0f0f0f", highlightthickness=0)
canvas.pack()

def draw_menu(state, selection):
    canvas.delete("all")
    options = MENU1_OPTIONS if state == "menu1" else MENU2_OPTIONS
    title = "Media Controls" if state == "menu1" else "Navigation"
    
    canvas.create_rectangle(30, 30, 490, 430, outline="#00FF88", width=4, fill="#1a1a1a")
    canvas.create_text(260, 75, text=title, fill="#00FFCC", font=("Arial", 16, "bold"))

    for i, text in enumerate(options):
        color = "#00FF88" if i == selection else "#EEEEEE"
        canvas.create_rectangle(60, 130 + i*55, 460, 175 + i*55, outline=color, width=3 if i == selection else 1)
        canvas.create_text(260, 153 + i*55, text=text, fill=color, font=("Arial", 14, "bold" if i == selection else "normal"))

# ==================== MAIN LOOP ====================
try:
    with HandLandmarker.create_from_options(options) as landmarker:
        camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
        camera.set(3, 640)
        camera.set(4, 480)
        timestamp = time.time()

        while True:
            ret, frame = camera.read()
            if not ret: break

            frame = cv2.flip(frame, 1)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            result = landmarker.detect_for_video(mp_image, int((time.time() - timestamp) * 1000))

            if result.hand_landmarks:
                for hand in result.hand_landmarks:
                    index_tip = hand[8]
                    thumb_tip = hand[4]
                    index_pip = hand[6]
                    middle_tip = hand[12]
                    middle_pip = hand[10]
                    wrist = hand[0]

                    extended = count_extended_fingers(hand)
                    fist_closed = extended == 0

                    # State transitions
                    if extended == 1 and not fist_closed and menu_state == "neutral":
                        menu_state = "preparing1"
                    elif extended == 2 and not fist_closed and menu_state == "neutral":
                        menu_state = "preparing2"

                    if fist_closed:
                        if menu_state == "preparing1":
                            menu_state = "menu1"
                            menu_start_y = wrist.y
                            menu_selection = 0
                            draw_menu("menu1", menu_selection)
                        elif menu_state == "preparing2":
                            menu_state = "menu2"
                            menu_start_y = wrist.y
                            menu_selection = 0
                            draw_menu("menu2", menu_selection)

                    if menu_state in ["menu1", "menu2"] and fist_closed:
                        delta_y = menu_start_y - wrist.y
                        if abs(delta_y) > 0.08:
                            options = MENU1_OPTIONS if menu_state == "menu1" else MENU2_OPTIONS
                            menu_selection = max(0, min(len(options)-1, menu_selection + (1 if delta_y < 0 else -1)))
                            menu_start_y = wrist.y
                            draw_menu(menu_state, menu_selection)

                    if menu_state in ["menu1", "menu2"] and not fist_closed:
                        options = MENU1_OPTIONS if menu_state == "menu1" else MENU2_OPTIONS
                        action = options[menu_selection]
                        print(f"Executing: {action}")

                        if menu_state == "menu1":
                            if action == "Volume +": subprocess.run(['ydotool', 'key', '122'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif action == "Volume -": subprocess.run(['ydotool', 'key', '123'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif action == "Play/Pause": subprocess.run(['ydotool', 'key', '164'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif action == "Next": subprocess.run(['ydotool', 'key', '163'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif action == "Previous": subprocess.run(['ydotool', 'key', '165'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        else:
                            if action == "Page Up": subprocess.run(['ydotool', 'key', '112'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif action == "Page Down": subprocess.run(['ydotool', 'key', '117'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif action == "Alt+Tab": subprocess.run(['ydotool', 'key', '56:1', '15:1', '15:0', '56:0'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif action == "Minimize": subprocess.run(['ydotool', 'key', '125:1', '109:1', '109:0', '125:0'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            elif action == "Close Window": subprocess.run(['ydotool', 'key', '56:1', '62:1', '62:0', '56:0'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        menu_state = "neutral"
                        overlay.withdraw()

                    if menu_state in ["neutral", "preparing1", "preparing2"]:
                        norm_x = max(0.0, min(1.0, (index_tip.x - 0.04) / 0.92))
                        norm_y = max(0.0, min(1.0, (index_tip.y - 0.04) / 0.87))
                        x_raw = int(norm_x * SCREEN_WIDTH)
                        y_raw = int(norm_y * SCREEN_HEIGHT)

                        if abs(x_raw - prev_x) < DEADZONE and abs(y_raw - prev_y) < DEADZONE:
                            x_tela = prev_x
                            y_tela = prev_y
                        else:
                            x_tela = int(prev_x * (1 - SMOOTH) + x_raw * SMOOTH)
                            y_tela = int(prev_y * (1 - SMOOTH) + y_raw * SMOOTH)

                        prev_x, prev_y = x_tela, y_tela

                        dist_click = ((thumb_tip.x - index_pip.x)**2 + (thumb_tip.y - index_pip.y)**2) ** 0.5
                        if dist_click < PINCH_THRESHOLD:
                            if not is_clicking:
                                locked_x, locked_y = x_tela, y_tela
                                is_clicking = True
                                if time.time() - last_action_time > 0.35:
                                    subprocess.run(['ydotool', 'click', '0xC0'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=0.1)
                                    last_action_time = time.time()
                            subprocess.run(['ydotool', 'mousemove', '--absolute', str(locked_x), str(locked_y)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=0.05)
                        else:
                            is_clicking = False
                            subprocess.run(['ydotool', 'mousemove', '--absolute', str(x_tela), str(y_tela)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=0.05)

                    if menu_state in ["menu1", "menu2"]:
                        overlay.deiconify()
                        overlay.lift()
                        draw_menu(menu_state, menu_selection)
                        overlay.update()

            else:
                if menu_state in ["menu1", "menu2"]:
                    menu_state = "neutral"
                overlay.withdraw()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

except KeyboardInterrupt:
    print("\nStopping AirCursor...")

camera.release()
overlay.destroy()
root.destroy()
print("AirCursor stopped.")

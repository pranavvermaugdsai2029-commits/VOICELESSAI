print("🔥 PLAYER.PY FILE EXECUTED:", __file__)

import cv2
import os

import cv2
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "assets", "sign_clips")

def play_clip(label):
    path = os.path.join(VIDEO_DIR, f"{label}.mp4")
    print("📁 Trying to play:", path)

    if not os.path.exists(path):
        print("❌ File not found")
        return

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print("❌ Could not open video")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 25  # fallback

    delay = int(1000 / fps)

    cv2.namedWindow("Sign Output", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Sign Output", frame)

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

    from realtime import is_playing_output
    is_playing_output = False
      

    cap.release()






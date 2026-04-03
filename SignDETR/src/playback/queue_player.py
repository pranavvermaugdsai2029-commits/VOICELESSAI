import cv2
import os
import time
import threading
import queue

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "assets", "sign_clips")

class PlaybackQueue:
    def __init__(self, pause_ms=300):
        self.queue = queue.Queue()
        self.pause_ms = pause_ms
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def enqueue(self, clip_key):
        self.queue.put(clip_key)

    def _worker(self):
         print("▶️ Playback worker started")
         cv2.namedWindow("Sign Output", cv2.WINDOW_NORMAL)

         while True:
            clip_key = self.queue.get()
            path = os.path.join(VIDEO_DIR, f"{clip_key}.mp4")

            if not os.path.exists(path):
                print("❌ Clip not found:", path)
                continue

            cap = cv2.VideoCapture(path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 25
            delay = int(1000 / fps)

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow("Sign Output", frame)
                cv2.waitKey(delay)

            cap.release()
            time.sleep(self.pause_ms / 1000)

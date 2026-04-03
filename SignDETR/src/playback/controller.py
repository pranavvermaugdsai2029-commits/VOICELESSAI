import queue
import threading
import time
from .player import play_clip

class PlaybackController:
    def __init__(self, pause_ms=300):
        self.queue = queue.Queue()
        self.pause_ms = pause_ms

        self.worker = threading.Thread(
            target=self._run,
            daemon=True
        )
        self.worker.start()

    def enqueue(self, label):
        self.queue.put(label)

    def _run(self):
        print("🎬 Playback worker started") 
        while True:
            label = self.queue.get()
            play_clip(label)
            print("🎬 Playing clip:", label)  # ADD THIS

            # pause BETWEEN clips (non-blocking)
            time.sleep(self.pause_ms / 1000)
            

            self.queue.task_done()

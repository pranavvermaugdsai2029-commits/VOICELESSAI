import cv2
import threading

import torch
from torch import load
from model import DETR
import albumentations as A
from utils.boxes import rescale_bboxes
from utils.setup import get_classes, get_colors
from utils.logger import get_logger
from utils.rich_handlers import DetectionHandler, create_detection_live_display
import sys
import time 
import subprocess
import time
import requests
from playback.queue_player import PlaybackQueue
import re
import random

CLASSES = [
    "a",
    "b",
    "c",
    "d",
    "i",
    "hello",
    "thank_you",
    "yes",
    "no",
    "please",
    "help",
    "good",
    "change",
    "this",
    "okay",
    "i_love_you"
]

NUM_CLASSES = 16 # MUST match checkpoint
random.seed(42)
COLORS = [
    (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )
    for _ in range(NUM_CLASSES)
]





def normalize_text(s: str) -> str:
    s = s.lower()
    s = s.replace("’", "'")        # smart quotes → normal
    s = re.sub(r"\s+", " ", s)     # collapse multiple spaces
    s = s.strip()
    return s

hello_sent = False
is_playing_output = False


def send_to_rasa(token):
    message = SIGN_TO_RASA_INTENT.get(token, token)

    print("🧠 Sending to Rasa:", message)

    r = requests.post(
        "http://localhost:5005/webhooks/rest/webhook",
        json={
            "sender": "signdetr",
            "message": message
        },
        timeout=2
    )
    return r.json()



playback = PlaybackQueue(pause_ms=400)


SIGN_TO_RASA = {
    "thank_you": "thank you",
    "hello": "hello",
    "yes": "yes",
    "a": "a",
    "b": "b",
    "c": "c",
    "i": "i",
    "i_love_you": "i love you",
    "please": "please",
    "no": "no",
    "help": "help",
    "sorry": "sorry",
    "this": "this",
    "okay": "okay",
}

SIGN_TO_RASA_INTENT = {
    "thank_you": "/sign_thank_you",
    "thanks": "/sign_thank_you",
    "thank you": "/sign_thank_you",

    "okay": "/sign_okay",
    "ok": "/sign_okay",

    "hello": "/sign_hello",
    "yes": "/sign_yes",
    "this": "/sign_this",

    "a": "/sign_a",
    "b": "/sign_b",
    "c": "/sign_c",
    "i": "/sign_i"
}

RASA_RESPONSE_TO_CLIP_RAW = {
    # thank you
    "you're welcome!. what else can i do for you?": "thank_you_response",

    # okay
    "i got that . what else can i do for you?": "okay_response",

    # hello
    "hello! how can i help you?": "hello_response",

    # alphabets
    "you signed the letter a. what else can i do for you?": "a_response",
    "you signed the letter b. what else can i do for you?": "b_response",
    "you signed the letter c. what else can i do for you?": "c_response",
    "you signed the letter i. what else can i do for you?": "i_response",

    # misc
    "i understood the reference. what else can i do for you?": "this_response",
    "okay, noted.what else can i do for you?": "yes_response"
}

RASA_RESPONSE_TO_CLIP = {
    normalize_text(k): v
    for k, v in RASA_RESPONSE_TO_CLIP_RAW.items()
}


def rasa_already_running():
    try:
        r = requests.get("http://127.0.0.1:5005/status", timeout=0.2)
        return r.status_code == 200
    except:
        return False


def start_rasa():
    import os
    import subprocess
    import time
    import requests

    RASA_PROJECT_DIR = r"C:\Users\Pranav\my-rasa-assistant"
    RASA_PYTHON = r"C:\Users\Pranav\my-rasa-assistant\.venv\Scripts\python.exe"

    env = os.environ.copy()
    env["RASA_LICENSE"] = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJjN2U0YzE5ZS1mYmQ0LTQxZGMtYTkyMi03NWQ2YjczNDFkY2UiLCJpYXQiOjE3NjgxMzg2ODAsIm5iZiI6MTc2ODEzODY4MCwic2NvcGUiOiJyYXNhOnBybyByYXNhOnBybzpjaGFtcGlvbiByYXNhOnZvaWNlIiwiZXhwIjoxODYyODMzMDgwLCJlbWFpbCI6InByYW5hdi52ZXJtYV91Z2RzYWkyMDI5QG1hc3RlcnN1bmlvbi5vcmciLCJjb21wYW55IjoiUmFzYSBDaGFtcGlvbnMifQ.CWyeJL7O7DD5l3O-09TeL4QT7sTsFRV3YzHhbPqeMiRJok3aS5FYcg-k24pi485jcQwSfBy-QNA9w93U05TegJdMVfHSwxrTzhUZUEYp73JJ-aPDyXcpmt3EF64Em4ygfd0qQueHhGpzDsR61rNLI1dOVKm1c5W_hEdOs1YFc5iO00nMe9JDublAQRUPkarJXM6DnYT6v_2vhUbgcVICFaowQnU1BbrJqKeyhxE5PKlIWsLP26Qp1aoXTFfWrLjp51LDnokNQDR6oOBdXPf5eR6AWIwe3HEIYyMFTudPM1d8UskY5Oe02qDateRecuCTdYZHjIG9KfEKYfC-n4Hgyg"

    subprocess.Popen(
        [
            RASA_PYTHON,
            "-m", "rasa",
            "run",
            "--enable-api"
        ],
        cwd=RASA_PROJECT_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False
    )

    for _ in range(30):
        try:
            r = requests.get("http://127.0.0.1:5005/status", timeout=0.3)
            if r.status_code == 200:
                print("✅ Rasa is running")
                return
        except:
            time.sleep(0.5)

    raise RuntimeError("❌ Rasa failed to start")

def handle_rasa(token):
    print("🔥 ENTERED handle_rasa with token:", token)

    try:
        responses = send_to_rasa(token)
        print("🔥 send_to_rasa returned:", responses)

        for msg in responses:
            raw_text = msg.get("text", "")
            normalized = normalize_text(raw_text)
            print("🤖 Rasa:", raw_text)

            clip_key = RASA_RESPONSE_TO_CLIP.get(normalized)
            if clip_key:
             print("🎬 Enqueue clip:", clip_key)

             global is_playing_output
             is_playing_output = True

             playback.enqueue(clip_key)
             threading.Timer(3.0, lambda: setattr(sys.modules[__name__], "is_playing_output", False)).start()


            else:
                print("⚠️ No clip mapped for:", raw_text)

    except Exception as e:
        print("⚠️ Rasa error:", e)




class SignEventFilter:
    def __init__(self, release_frames=8):
        self.last_sent = None
        self.release_counter = 0
        self.release_frames = release_frames

    def emit(self, label):
        # No detection → count release
        if label is None:
            if self.last_sent is not None:
                self.release_counter += 1
                if self.release_counter >= self.release_frames:
                    self.last_sent = None
                    self.release_counter = 0
            return None

        # Same label as before → block spam
        if label == self.last_sent:
            self.release_counter = 0
            return None

        # New label → emit
        self.last_sent = label
        self.release_counter = 0
        return label











# Initialize logger and handlers
logger = get_logger("realtime")
detection_handler = DetectionHandler()

logger.print_banner()
logger.realtime("Initializing real-time sign language detection...")

transforms = A.Compose(
        [   
            A.Resize(224,224),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            A.ToTensorV2()
        ]
    )


model = DETR(num_classes=NUM_CLASSES)
print("🔍 NUM_CLASSES variable =", NUM_CLASSES)
print("🔍 Model classifier weight shape =", model.linear_class.weight.shape)


model.eval()
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "checkpoints" / "99_model.pt"

model.load_pretrained(str(MODEL_PATH))


frame_filter = SignEventFilter()




def start_camera_loop():
    logger.realtime("Starting camera capture...")
    cap = cv2.VideoCapture(0)
    hello_sent = False

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    frame_filter = SignEventFilter()
    last_rasa_token = None

    while cap.isOpened():
        ret, frame = cap.read()
        # 👋 Auto hello once camera is ready
        if not hello_sent:
         print("👋 Sending auto hello")
         threading.Thread(
            target=handle_rasa,
            args=("hello",),
            daemon=True
            ).start()
         hello_sent = True

        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        transformed = transforms(image=rgb)

        result = model(torch.unsqueeze(transformed["image"], dim=0))

        probs = result["pred_logits"].softmax(-1)
        scores, labels = probs.max(-1)

        keep = (labels != NUM_CLASSES) & (scores > 0.6)
        batch_idx, query_idx = torch.where(keep)

        h, w, _ = frame.shape
        bboxes = rescale_bboxes(
            result["pred_boxes"][batch_idx, query_idx],
            (w, h)
        )

        token = None

        for cls, score, box in zip(
            labels[batch_idx, query_idx],
            scores[batch_idx, query_idx],
            bboxes
        ):
            cls = int(cls.item())
            score = float(score.item())
            x1, y1, x2, y2 = map(int, box.tolist())

            label = CLASSES[cls]

            emitted = frame_filter.emit(label)
            if emitted:
                token = emitted
          
           # Draw bounding box (ORIGINAL STYLE)
            frame = cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            COLORS[cls],
            10,  # original thickness
            )
            # Label background bar (ORIGINAL STYLE)
            frame = cv2.rectangle(
            frame,
            (x1, y1 - 100),
            (x1 + 700, y1),
            COLORS[cls],
            -1,  # solid fill
           )

         # Label text (ORIGINAL STYLE)
            frame_text = f"{CLASSES[cls]} - {round(score, 4)}"

            frame = cv2.putText(
            frame,
            frame_text,
           (x1, y1),
           cv2.FONT_HERSHEY_DUPLEX,
            2,   # original font scale
            (255, 255, 255),
           4,   # original thickness
          cv2.LINE_AA,
         )


           
            

        if token and token != last_rasa_token:
            last_rasa_token = token
            threading.Thread(
                target=handle_rasa,
                args=(token,),
                daemon=True
            ).start()

        cv2.imshow("SignDETR", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    

if __name__ == "__main__":
    if not rasa_already_running():
        start_rasa()
    start_camera_loop()



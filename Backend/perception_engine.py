import cv2
import time
from collections import defaultdict
from ultralytics import YOLO
import mediapipe as mp
from deepface import DeepFace

class PerceptionEngine:
    def __init__(
        self,
        camera_index=0,
        object_confidence=0.55,
        object_stable_frames=8,
        object_cooldown=3.0,
        emotion_stable_frames=10,
        emotion_cooldown=4.0
    ):
        # Camera
        self.cap = cv2.VideoCapture(camera_index)

        # Object detection
        self.object_model = YOLO("yolov8n.pt")
        self.object_confidence = object_confidence
        self.object_stable_frames = object_stable_frames
        self.object_cooldown = object_cooldown
        self.object_counter = defaultdict(int)
        self.last_object_time = {}

        # Emotion detection
        self.face_detector = mp.solutions.face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.7
        )
        self.emotion_stable_frames = emotion_stable_frames
        self.emotion_cooldown = emotion_cooldown
        self.emotion_counter = defaultdict(int)
        self.last_emotion_time = {}

    # -----------------------------
    # OBJECT DETECTION
    # -----------------------------
    def _detect_object(self, frame):
        results = self.object_model(frame, verbose=False)[0]
        active = set()

        for box in results.boxes:
            conf = float(box.conf[0])
            if conf < self.object_confidence:
                continue

            label = self.object_model.names[int(box.cls[0])]
            active.add(label)
            self.object_counter[label] += 1

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2),
                          (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 0), 2)

            if (
                self.object_counter[label] >= self.object_stable_frames
                and self._object_cooldown_ok(label)
            ):
                self.last_object_time[label] = time.time()
                self.object_counter[label] = 0
                return label

        for lbl in list(self.object_counter.keys()):
            if lbl not in active:
                self.object_counter[lbl] = 0

        return None

    def _object_cooldown_ok(self, label):
        last = self.last_object_time.get(label, 0)
        return (time.time() - last) > self.object_cooldown

    # -----------------------------
    # EMOTION DETECTION
    # -----------------------------
    def _detect_emotion(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.face_detector.process(rgb)

        if not faces.detections:
            self.emotion_counter.clear()
            return None

        try:
            analysis = DeepFace.analyze(
                frame,
                actions=["emotion"],
                enforce_detection=False
            )[0]

            emotion = analysis["dominant_emotion"]
            confidence = analysis["emotion"][emotion] / 100

            self.emotion_counter[emotion] += 1

            if (
                self.emotion_counter[emotion] >= self.emotion_stable_frames
                and self._emotion_cooldown_ok(emotion)
            ):
                self.last_emotion_time[emotion] = time.time()
                self.emotion_counter.clear()
                return emotion, round(confidence, 2)

        except Exception:
            pass

        return None

    def _emotion_cooldown_ok(self, emotion):
        last = self.last_emotion_time.get(emotion, 0)
        return (time.time() - last) > self.emotion_cooldown

    # -----------------------------
    # MAIN TICK
    # -----------------------------
    def tick(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None, None

        object_name = self._detect_object(frame)
        emotion_data = self._detect_emotion(frame)

        return object_name, emotion_data, frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
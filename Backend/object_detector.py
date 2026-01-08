import cv2
from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, camera_index=0, confidence=0.5):
        self.model = YOLO("yolov8n.pt")  # fast & lightweight
        self.cap = cv2.VideoCapture(camera_index)
        self.confidence = confidence
        self.last_detected = None

    def detect(self):
        """
        Returns:
            object_name (str | None)
            frame (numpy array)
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        results = self.model(frame, verbose=False)

        for r in results:
            for box in r.boxes:
                if box.conf[0] >= self.confidence:
                    cls_id = int(box.cls[0])
                    label = self.model.names[cls_id]

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2),
                                  (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                (0, 255, 0), 2)

                    if label != self.last_detected:
                        self.last_detected = label
                        return label, frame

        return None, frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import cv2
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_drawing

import pyautogui
import math
import time

class HandMouseCursor:
    def __init__(
        self,
        camera_index=0,
        smoothing=7,
        click_threshold=35
    ):
        # Camera
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise RuntimeError("❌ Camera not accessible")

        # Screen size
        self.screen_w, self.screen_h = pyautogui.size()

        # MediaPipe Hand
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.drawer = mp.solutions.drawing_utils

        # Cursor smoothing
        self.prev_x, self.prev_y = 0, 0
        self.smoothing = smoothing

        # Click
        self.click_threshold = click_threshold
        self.last_click_time = 0
        self.click_delay = 0.6  # seconds

    def _distance(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def tick(self):
        """
        Returns:
            frame (for display)
        """
        ret, frame = self.cap.read()
        if not ret:
            return None

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            self.drawer.draw_landmarks(
                frame, hand, self.mp_hands.HAND_CONNECTIONS
            )

            # Index finger tip (8)
            index_tip = hand.landmark[8]
            x = int(index_tip.x * w)
            y = int(index_tip.y * h)

            # Map to screen
            screen_x = int(index_tip.x * self.screen_w)
            screen_y = int(index_tip.y * self.screen_h)

            # Smooth movement
            curr_x = self.prev_x + (screen_x - self.prev_x) / self.smoothing
            curr_y = self.prev_y + (screen_y - self.prev_y) / self.smoothing

            pyautogui.moveTo(curr_x, curr_y)
            self.prev_x, self.prev_y = curr_x, curr_y

            # Thumb tip (4) for click
            thumb_tip = hand.landmark[4]
            tx = int(thumb_tip.x * w)
            ty = int(thumb_tip.y * h)

            dist = self._distance((x, y), (tx, ty))

            # Click gesture (pinch)
            if dist < self.click_threshold:
                now = time.time()
                if now - self.last_click_time > self.click_delay:
                    pyautogui.click()
                    self.last_click_time = now
                    cv2.putText(
                        frame,
                        "CLICK",
                        (x, y - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (0, 0, 255),
                        2
                    )

            # Visual pointers
            cv2.circle(frame, (x, y), 8, (255, 0, 0), -1)
            cv2.circle(frame, (tx, ty), 8, (0, 255, 0), -1)

        return frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()


# =====================================================
# 🔥 RUN HAND MOUSE CURSOR (THIS WAS MISSING)
# =====================================================
if __name__ == "__main__":
    print("🖐️ Hand Mouse Cursor started. Press 'Q' to quit.")

    hand_mouse = HandMouseCursor(camera_index=0)

    while True:
        frame = hand_mouse.tick()
        if frame is None:
            break

        cv2.imshow("Hand Mouse Cursor", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    hand_mouse.release()
    print("👋 Hand Mouse Cursor stopped.")

import cv2
import numpy as np
import time
import collections
from server_node import config


class FrameProcessor:
    COOLDOWN_PERIOD = 2.0
    MOTION_CONFIDENCE_THRESHOLD = 0.7

    def __init__(self, camera_id: int):
        self.camera_id = camera_id
        self.frameBackground = cv2.createBackgroundSubtractorKNN()
        self.motionBuffer = collections.deque(maxlen=5)
        self.motionLogged = False
        self.lastMotionTime = 0
        self.startTime = time.time()
        self.oneOrMoreContours = False

    def process(self, frame: np.ndarray) -> np.ndarray:
        frameMotion = self.frameBackground.apply(frame)

        # binary threshold of light gray pixels
        _, frameFiltered = cv2.threshold(
            frameMotion,
            config.settings.value("Binary Threshold", 100, type=int),
            255,
            cv2.THRESH_BINARY
        )

        # erodes then dilates pixel blobs to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        frameEroded = cv2.morphologyEx(frameFiltered, cv2.MORPH_OPEN, kernel)

        # search for object contours
        contours, _ = cv2.findContours(frameEroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        self.oneOrMoreContours = False
        for contour in contours:
            if cv2.contourArea(contour) > config.settings.value("Contour Size", 500, type=int):
                self.oneOrMoreContours = True
                x, y, w, h = cv2.boundingRect(contour)
                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        self.motion_detection()

        return frame

    def motion_detection(self):
        self.motionBuffer.append(self.oneOrMoreContours)
        motionConfidencePercentage = sum(self.motionBuffer) / len(self.motionBuffer)
        currentTime = time.time()

        if motionConfidencePercentage >= self.MOTION_CONFIDENCE_THRESHOLD:
            if not self.motionLogged and currentTime - self.lastMotionTime > self.COOLDOWN_PERIOD:
                elapsed = currentTime - self.startTime
                hours = int(elapsed // 3600)
                mins = int((elapsed % 3600) // 60)
                sec = int(elapsed % 60)
                print(f"Movement detected on camera {self.camera_id} at {hours}:{mins}:{sec}")

                self.motionLogged = True
                self.lastMotionTime = currentTime

        elif currentTime - self.lastMotionTime > self.COOLDOWN_PERIOD:
            self.motionLogged = False

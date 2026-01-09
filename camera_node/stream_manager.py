import asyncio
import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame
import numpy as np
import logging

logger = logging.getLogger("camera_stream")

class CameraStreamTrack(VideoStreamTrack):
    def __init__(self, camera_index=0):
        super().__init__()
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            logger.error(f"Could not open camera {camera_index}")
        else:
            # default to 640x480
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()
        if not ret:
            # return empty numpy frame if read fails
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

        new_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        new_frame.pts = pts
        new_frame.time_base = time_base
        return new_frame

    def stop(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
import asyncio
import uvicorn
import logging
import numpy as np
from fastapi import FastAPI, Request
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from av import VideoFrame
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from server_node import config
from .frame_processor import FrameProcessor
from .video_recorder import VideoRecorder

logger = logging.getLogger("webrtc_server")

class StreamConnectManager(QObject):
    stream_added = pyqtSignal(int)
    frame_ready = pyqtSignal(int, np.ndarray)
stream_manager = StreamConnectManager()
pcs = set()

app = FastAPI()

class VideoReceiver:
    def __init__(self, track: MediaStreamTrack, camera_id: int):
        self.track = track
        self.camera_id = camera_id
        self.processor = FrameProcessor(camera_id)
        self.recorder = VideoRecorder()
        self.frame_count = 0
        self.last_processed = None

    async def run(self):
        throttle_rate = config.settings.value("FRAME_THROTTLE_RATE", 1)
        while True:
            try:
                frame: VideoFrame = await self.track.recv()
                img = frame.to_ndarray(format="bgr24")
                
                self.frame_count += 1

                # handle recording
                # since this is async/threaded, direct config read is okay but might be racy.
                # ideally we use a signal, but polling config for now is consistent with legacy app.
                # TODO
                is_recording = config.settings.value("RECORDING_TOGGLE", False, type=bool)
                
                if is_recording:
                    if not self.recorder.recording:
                        self.recorder.start_recording()
                    self.recorder.add_frame(img)
                else:
                    if self.recorder.recording:
                        self.recorder.end_recording()
                
                if config.settings.value("Raw View", True, type=bool):
                    stream_manager.frame_ready.emit(self.camera_id, img)
                else:
                    if self.frame_count % throttle_rate == 0:
                        processed = self.processor.process(img.copy())
                        self.last_processed = processed
                    else:
                        processed = self.last_processed
                    
                    if processed is not None:
                        stream_manager.frame_ready.emit(self.camera_id, processed)

            except Exception as e:
                logger.error(f"Track ended or error for camera {self.camera_id}: {e}")
                self.recorder.end_recording()
                break

@app.post("/offer")
async def offer(request: Request):
    params = await request.json()
    camera_id = params.get("camera_id", 0) # we default to 0 if not provided
    
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("track")
    def on_track(track):
        logger.info(f"Received track {track.kind} from camera {camera_id}")
        if track.kind == "video":
            # notify GUI of new stream & start receiver
            stream_manager.stream_added.emit(camera_id)
            receiver = VideoReceiver(track, camera_id)
            asyncio.ensure_future(receiver.run())

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if pc.connectionState == "failed" or pc.connectionState == "closed":
            pcs.discard(pc)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}


class SignalingServerWorker(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
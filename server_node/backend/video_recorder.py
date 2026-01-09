import datetime, cv2, os
from server_node import config

class VideoRecorder():
    def __init__(self):
        self.recording = False
        self.video = None
        os.makedirs("recordings", exist_ok=True)
        self.fps = 15 # half of camera's fps? idk

    def startRecording(self):
        if not self.recording:
            self.recording = True
            self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.outputFileName = f"recordings/motion_{self.timestamp}.mp4"
            self.codec = cv2.VideoWriter_fourcc(*'mp4v')
            
            width = config.settings.value("CAMERA_WIDTH", type=int)
            height = config.settings.value("CAMERA_HEIGHT", type=int)

            # fallback if config is 0, but we need explicit size for writer
            # this logic might need improvement if stream resolutions are different (maybe for grid recording? TODO)
            if width == 0: width = 640
            if height == 0: height = 480

            self.video = cv2.VideoWriter(
                self.outputFileName, 
                self.codec, 
                self.fps,
                (width, height)
            )

            if not self.video.isOpened():
                print(f"Error: Failed to open video writer for {self.outputFileName}")
                self.recording = False
                return
    
    def addFrame(self, frame):
        if self.recording and self.video:
            # resize if needed to match writer resolution
            # TODO: should probably initialize writer on first frame
            pass 
            self.video.write(frame)

    def endRecording(self):
        if self.recording and self.video:
            self.recording = False
            self.video.release()
            self.video = None

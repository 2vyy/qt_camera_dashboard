import datetime, cv2, config, os

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
            self.video = cv2.VideoWriter(
                self.outputFileName, 
                self.codec, 
                self.fps,
                (config.settings.value("CAMERA_WIDTH", type=int),
                 config.settings.value("CAMERA_HEIGHT", type=int))
            )

            if not self.video.isOpened():
                print(f"Error: Failed to open video writer for {self.outputFileName}")
                self.recording = False
                return
    
    def addFrame(self, frame):
        if self.recording and self.video:
            # is this how I should do this?
            if frame.shape[0] != config.settings.value("CAMERA_HEIGHT", type=int) or frame.shape[1] != config.settings.value("CAMERA_WIDTH", type=int):
                frame = cv2.resize(
                    frame,
                    (config.settings.value("CAMERA_WIDTH", type=int),
                     config.settings.value("CAMERA_HEIGHT", type=int))
                )
            self.video.write(frame)

    def endRecording(self):
        if self.recording and self.video:
            self.recording = False
            self.video.release()
            self.video = None#
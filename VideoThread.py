from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot
from VideoRecorder import VideoRecorder
import cv2, config, numpy as np, time, collections

# shout out https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1
class VideoThread(QThread):
    frameSignal = pyqtSignal(int, np.ndarray)

    COOLDOWN_PERIOD = 2.0
    MOTION_CONFIDENCE_THRESHOLD = 0.7

    def __init__(self, cameraIndex):
        super().__init__()
        self.cameraIndex = cameraIndex
        self.running = True

        self.videoCapture = cv2.VideoCapture(cameraIndex, cv2.CAP_DSHOW) # first parameter is webcam index
        if not self.videoCapture.isOpened():
            print(f"Failed to open camera {cameraIndex}")
            return

        self.videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, config.settings.value("CAMERA_WIDTH", type=int))
        self.videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.settings.value("CAMERA_HEIGHT", type=int))

        self.frameBackground = cv2.createBackgroundSubtractorKNN() ## TODO: MOG2 or KNN? also look at params

        self.frameCount = 0
        self.motionBuffer = collections.deque(maxlen=5)
        self.motionLogged = False
        self.lastMotionTime = 0
        self.startTime = time.time()
        self.lastProcessedFrame = None
        self.confimationFrame = 3

        self.isRecording = config.settings.value("Recording", False, type=bool)
        self.videoRecorder = VideoRecorder()
        if self.isRecording:
            self.videoRecorder.startRecording()

        print(f"Camera {cameraIndex} initialized with resolution {self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

    def run(self):
        throttleRate = config.settings.value("FRAME_THROTTLE_RATE")

        while self.running:
            self.frameCount += 1

            isReturned, rawFrame = self.videoCapture.read()

            if not isReturned:
                print(f"Camera {self.cameraIndex}: Frame not returned")
                continue

            if self.isRecording:
                self.videoRecorder.addFrame(rawFrame)

            if config.settings.value("Raw View", True, type=bool):
                self.frameSignal.emit(self.cameraIndex, rawFrame)
                continue

            if self.frameCount % throttleRate == 0:
                processedFrame = self.processFrame(rawFrame.copy())
                self.lastProcessedFrame = processedFrame
            else:
                processedFrame = self.lastProcessedFrame # if processing was throttled, resort to the last frame
            
            self.frameSignal.emit(self.cameraIndex, processedFrame)

        self.videoCapture.release()

    def processFrame(self, frame):
        frameMotion = self.frameBackground.apply(frame)

        # binary threshold of light gray pixels
        retval, frameFiltered = cv2.threshold(
            frameMotion,
            config.settings.value("Binary Threshold", 100, type=int),
            255,
            cv2.THRESH_BINARY
        )

        # erodes then dialates pixel blobs to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))   
        frameEroded = cv2.morphologyEx(frameFiltered, cv2.MORPH_OPEN, kernel)

        # search for object contours
        contours, hierarchy = cv2.findContours(frameEroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        self.oneOrMoreContours = False
        for contour in contours:
            if(cv2.contourArea(contour) > config.settings.value("Contour Size", 500, type=int)):
                self.oneOrMoreContours = True 
                x, y, w, h = cv2.boundingRect(contour)
                frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)  

        self.motionDetection()

        if self.isRecording:
            cv2.putText(frame,"REC", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return frame
    
    def motionDetection(self):
        self.motionBuffer.append(self.oneOrMoreContours)
        motionConfidencePercentage = sum(self.motionBuffer)/len(self.motionBuffer)
        currentTime = time.time()

        if motionConfidencePercentage >= self.MOTION_CONFIDENCE_THRESHOLD:  # At least 70% of recent frames show motion
            if not self.motionLogged and currentTime - self.lastMotionTime > self.COOLDOWN_PERIOD:
                # Log motion event
                elapsed = currentTime - self.startTime
                hours = elapsed // 3600
                remainingSeconds = elapsed % 3600
                mins = remainingSeconds // 60
                sec = remainingSeconds % 60
                print(f"Movement detected on camera {self.cameraIndex} at {int(hours)}:{int(mins)}:{int(sec)}")

                self.motionLogged = True
                self.lastMotionTime = currentTime

        elif currentTime - self.lastMotionTime > self.COOLDOWN_PERIOD:
            # Reset state if we've had sufficient stillness
            self.motionLogged = False

    
    def setRecordingState(self, recordingStarted):
        self.isRecording = recordingStarted #am I handling recording states properly or is it too messy?
        
        if self.isRecording:
            self.videoRecorder.startRecording()
        else:
            self.videoRecorder.endRecording()

    def stop(self):
        self.running = False
        if self.isRecording:
            self.videoRecorder.endRecording()
        self.wait() # for thread to end
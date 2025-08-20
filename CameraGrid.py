from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QSizePolicy
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
import cv2, numpy as np
from VideoThread import VideoThread

class CameraGrid(QWidget):
    def __init__(self, cameraIndexes):
        super().__init__()
        self.cameraIndexes = cameraIndexes
        self.cameraLabels = {}
        self.gridLayout = QGridLayout()
        self.setLayout(self.gridLayout)
        self.cameraThreads = []
        self.arrangeCameras()
        self.initializeCameras()
    
    def arrangeCameras(self):
        numCameras = len(self.cameraIndexes)
        
        cols = int(np.ceil(np.sqrt(numCameras)))
        rows = int(np.ceil(numCameras / cols))
        
        for i, cameraIndex in enumerate(self.cameraIndexes):
            if cameraIndex not in self.cameraLabels:
                label = QLabel(self)
                label.setAlignment(Qt.AlignCenter)
                label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                self.cameraLabels[cameraIndex] = label

            row = i // cols # every n columns, move to next row
            col = i % cols
            self.gridLayout.addWidget(self.cameraLabels[cameraIndex], row, col)
    
        for r in range(rows):
            self.gridLayout.setRowStretch(r, 1)
        for c in range(cols):
            self.gridLayout.setColumnStretch(c, 1)

    def initializeCameras(self):
        for cameraIndex in self.cameraIndexes:
            thread = VideoThread(cameraIndex)
            thread.frameSignal.connect(self.updateImage)
            thread.start()
            self.cameraThreads.append(thread)

    @pyqtSlot(int, np.ndarray)
    def updateImage(self, cameraIndex, frame) -> None:
        rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        label = self.cameraLabels.get(cameraIndex)
        if label:
            height, width, channels = rgbFrame.shape
            bytesPerLine = channels * width

            qtImage = QtGui.QImage(
                rgbFrame.data, 
                width, 
                height, 
                bytesPerLine, 
                QtGui.QImage.Format_RGB888
            )
        
            pixmap = QPixmap.fromImage(qtImage)
            scaledPixmap = pixmap.scaled(
                label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            label.setPixmap(scaledPixmap)

    def stopAllThreads(self):
        for thread in self.cameraThreads:
            thread.stop()
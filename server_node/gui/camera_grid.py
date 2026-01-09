from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QSizePolicy
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
import cv2, numpy as np
from server_node.config import settings

class CameraGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.cameraLabels = {} # maps camera_id -> QLabel
        self.gridLayout = QGridLayout()
        self.setLayout(self.gridLayout)
    
    def addCamera(self, camera_id):
        if camera_id in self.cameraLabels:
            return # already added

        label = QLabel(self)
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        label.setStyleSheet("border: 1px solid gray; background-color: black;")
        
        self.cameraLabels[camera_id] = label
        self._arrangeCameras()

    def _arrangeCameras(self):
        # clear layout (remove from view but don't delete widgets yet)
        for i in reversed(range(self.gridLayout.count())): 
            self.gridLayout.itemAt(i).widget().setParent(None)

        camera_ids = sorted(self.cameraLabels.keys())
        numCameras = len(camera_ids)
        if numCameras == 0: return

        cols = int(np.ceil(np.sqrt(numCameras))) # for camera grid layout
        
        for i, cid in enumerate(camera_ids):
            label = self.cameraLabels[cid]
            row = i // cols
            col = i % cols
            self.gridLayout.addWidget(label, row, col)
    
    @pyqtSlot(int, np.ndarray)
    def updateImage(self, cameraIndex, frame) -> None:
        if cameraIndex not in self.cameraLabels:
            self.addCamera(cameraIndex)

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
        pass # no local threads anymore

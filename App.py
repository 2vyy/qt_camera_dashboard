from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import config
from ControlBar import ControlBar
from CameraGrid import CameraGrid

class App(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Multi-Camera Monitoring")
        self.resize(1200, 700)
        self.show_processed = True

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.setSpacing(0)

        self.controlBar = ControlBar()
        self.controlBar.recordingToggled.connect(self.handleRecordingToggle)
        mainLayout.addWidget(self.controlBar)

        self.cameraGrid = CameraGrid(config.settings.value("CAMERA_INDEXES", type=tuple))
        mainLayout.addWidget(self.cameraGrid, 1)  # Takes remaining space

        self.setLayout(mainLayout)

    def handleRecordingToggle(self, recordingStarted) -> None:
        for thread in self.cameraGrid.cameraThreads:
            thread.setRecordingState(recordingStarted)

    def closeEvent(self, event) -> None:
        config.settings.sync()
        self.cameraGrid.stopAllThreads()
        event.accept()
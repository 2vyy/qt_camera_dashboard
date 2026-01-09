from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from server_node import config
from .control_bar import ControlBar
from .camera_grid import CameraGrid
from server_node.backend.server import SignalingServerWorker, stream_manager

class App(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Multi-Camera Monitoring (Push Server)")
        self.resize(1200, 700)
        self.show_processed = True

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.setSpacing(0)

        self.controlBar = ControlBar()
        mainLayout.addWidget(self.controlBar)

        self.cameraGrid = CameraGrid()
        mainLayout.addWidget(self.cameraGrid, 1)

        self.setLayout(mainLayout)

        # Start Signaling Server
        self.signalingWorker = SignalingServerWorker()
        self.signalingWorker.start()

        # Connect Signals
        stream_manager.stream_added.connect(self.cameraGrid.addCamera)
        stream_manager.frame_ready.connect(self.cameraGrid.updateImage)

    def closeEvent(self, event) -> None:
        config.settings.sync()
        # self.signalingWorker.stop() # TODO: Graceful shutdown of uvicorn
        event.accept()

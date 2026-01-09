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

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        self.control_bar = ControlBar()
        main_layout.addWidget(self.control_bar)

        self.camera_grid = CameraGrid()
        main_layout.addWidget(self.camera_grid, 1)

        self.setLayout(main_layout)

        # Start Signaling Server
        # Start Signaling Server
        self.signaling_worker = SignalingServerWorker()
        self.signaling_worker.start()

        # Connect Signals
        # Connect Signals
        stream_manager.stream_added.connect(self.camera_grid.add_camera)
        stream_manager.frame_ready.connect(self.camera_grid.update_image)

    def closeEvent(self, event) -> None:
        config.settings.sync()
        # self.signaling_worker.stop() # TODO: Graceful shutdown of uvicorn
        event.accept()

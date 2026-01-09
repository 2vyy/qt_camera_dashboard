from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QSizePolicy
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap
import cv2, numpy as np
from server_node.config import settings

class CameraGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.camera_labels = {} # maps camera_id -> QLabel
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
    
    def add_camera(self, camera_id):
        if camera_id in self.camera_labels:
            return # already added

        label = QLabel(self)
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        label.setStyleSheet("border: 1px solid gray; background-color: black;")
        
        self.camera_labels[camera_id] = label
        self._arrange_cameras()

    def _arrange_cameras(self):
        # clear layout (remove from view but don't delete widgets yet)
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)

        camera_ids = sorted(self.camera_labels.keys())
        num_cameras = len(camera_ids)
        if num_cameras == 0: return

        cols = int(np.ceil(np.sqrt(num_cameras))) # for camera grid layout
        
        for i, cid in enumerate(camera_ids):
            label = self.camera_labels[cid]
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(label, row, col)
    
    @pyqtSlot(int, np.ndarray)
    def update_image(self, camera_index, frame) -> None:
        if camera_index not in self.camera_labels:
            self.add_camera(camera_index)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        label = self.camera_labels.get(camera_index)
        if label:
            height, width, channels = rgb_frame.shape
            bytes_per_line = channels * width

            qt_image = QtGui.QImage(
                rgb_frame.data, 
                width, 
                height, 
                bytes_per_line, 
                QtGui.QImage.Format_RGB888
            )
        
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            label.setPixmap(scaled_pixmap)

    def stop_all_threads(self):
        pass # no local threads anymore

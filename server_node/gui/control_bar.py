from PyQt5.QtCore import Qt, pyqtSignal  # pylint: disable=no-name-in-module
from PyQt5.QtGui import QPalette, QColor  # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QSpinBox, QHBoxLayout, QScrollArea, QGroupBox, QSizePolicy
from server_node import config

class ControlBar(QWidget):
    """
    Widget containing controls for the camera dashboard.
    
    Includes settings for binary threshold, contour size, and toggles for 
    view modes, recording, and application theme.
    """
    recording_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMaximumHeight(100)
        
        layout = QHBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setAlignment(Qt.AlignLeft)
        
        self.toggle_view_button = QPushButton("Show Raw View")
        self.toggle_view_button.clicked.connect(self.toggle_view)
        controls_layout.addWidget(self.toggle_view_button)
        
        threshold_group = QGroupBox("Threshold")
        threshold_layout = QHBoxLayout(threshold_group)
        self.threshold_spin_box = QSpinBox(minimum=0, maximum=255, value=config.settings.value("Binary Threshold", 100, type=int))
        self.threshold_spin_box.setPrefix("Value: ")
        self.threshold_spin_box.valueChanged.connect(self.set_binary_threshold)
        threshold_layout.addWidget(self.threshold_spin_box)
        controls_layout.addWidget(threshold_group)
        
        contour_group = QGroupBox("Contour Settings")
        contour_layout = QHBoxLayout(contour_group)
        self.min_contour_spin = QSpinBox(minimum=0, maximum=10000, value=config.settings.value("Contour Size", 400, type=int))
        self.min_contour_spin.setPrefix("Min Area: ")
        self.min_contour_spin.valueChanged.connect(self.set_contour_size)
        contour_layout.addWidget(self.min_contour_spin)
        controls_layout.addWidget(contour_group)

        self.toggle_theme_button = QPushButton("Use Light Mode")
        self.toggle_theme_button.clicked.connect(self.toggle_theme)
        controls_layout.addWidget(self.toggle_theme_button)

        self.is_recording = config.settings.value("RECORDING_TOGGLE", False, type=bool)
        self.toggle_recording_button = QPushButton("Start Recording")
        self.toggle_recording_button.clicked.connect(self.toggle_recording)
        controls_layout.addWidget(self.toggle_recording_button)
        
        self.update_view_button_text()
        self.update_theme_button_text()
        self.update_recording_button_text()

        controls_layout.addStretch()
        
        scroll.setWidget(controls_widget)
        layout.addWidget(scroll)
        self.setLayout(layout)

        self.set_theme()

    def toggle_view(self):
        """
        Toggles the camera view between raw and processed modes.
        """
        raw_view_toggled = not config.settings.value("Raw View", True, type=bool)
        config.settings.setValue("Raw View", raw_view_toggled)
        self.update_view_button_text()

    def toggle_theme(self):
        light_mode_toggled = not config.settings.value("Dark Mode", True, type=bool)
        config.settings.setValue("Dark Mode", light_mode_toggled)
        self.set_theme()
        self.update_theme_button_text()
    
    def set_theme(self):
        if config.settings.value("Dark Mode", True, type=bool):
            self.toggle_theme_button.setText("Use Light Mode")
            # there has to be a better way to have simple dark mode than 500 lines of whatever this is
            QApplication.setStyle("Fusion")
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, Qt.white)
            dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.ToolTipText, Qt.white)
            dark_palette.setColor(QPalette.Text, Qt.white)
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, Qt.white)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
            dark_palette.setColor(QPalette.Active, QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
            dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, Qt.darkGray)
            dark_palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
            dark_palette.setColor(QPalette.Disabled, QPalette.Light, QColor(53, 53, 53))
            QApplication.setPalette(dark_palette)
        else:
            self.toggle_theme_button.setText("Use Dark Mode")
            QApplication.setStyle("")
            QApplication.setPalette(QPalette())

    def set_binary_threshold(self):
        config.settings.setValue("Binary Threshold", self.threshold_spin_box.value())

    def set_contour_size(self):
        config.settings.setValue("Contour Size", self.min_contour_spin.value())

    def toggle_recording(self):
        self.is_recording = not self.is_recording
        config.settings.setValue("RECORDING_TOGGLE", self.is_recording)
        self.recording_toggled.emit(self.is_recording)
        self.update_recording_button_text()

    def update_recording_button_text(self):
        self.toggle_recording_button.setText(
            "Stop Recording" if self.is_recording else "Start Recording"
        )

    def update_view_button_text(self):
        processed_view = config.settings.value("Raw View", True, type=bool)
        self.toggle_view_button.setText(
            "Show Processed View" if processed_view else "Show Raw View"
        )

    def update_theme_button_text(self):
        dark_mode = config.settings.value("Dark Mode", True, type=bool)
        self.toggle_theme_button.setText(
            "Use Light Mode" if dark_mode else "Use Dark Mode"
        )

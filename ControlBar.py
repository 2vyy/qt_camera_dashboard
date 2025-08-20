from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QSpinBox, QHBoxLayout, QScrollArea, QGroupBox, QSizePolicy
import config

class ControlBar(QWidget):
    recordingToggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMaximumHeight(100)
        
        mainLayout = QHBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        controlsWidget = QWidget()
        controlsLayout = QHBoxLayout(controlsWidget)
        controlsLayout.setAlignment(Qt.AlignLeft)
        
        self.toggleViewButton = QPushButton("Show Raw View")
        self.toggleViewButton.clicked.connect(self.toggleView)
        controlsLayout.addWidget(self.toggleViewButton)
        
        thresholdGroup = QGroupBox("Threshold")
        thresholdLayout = QHBoxLayout(thresholdGroup)
        self.thresholdSpinBox = QSpinBox(minimum=0, maximum=255, value=config.settings.value("Binary Threshold", 100, type=int))
        self.thresholdSpinBox.setPrefix("Value: ")
        self.thresholdSpinBox.valueChanged.connect(self.setBinaryThreshold)
        thresholdLayout.addWidget(self.thresholdSpinBox)
        controlsLayout.addWidget(thresholdGroup)
        
        contourGroup = QGroupBox("Contour Settings")
        contourLayout = QHBoxLayout(contourGroup)
        self.minContourSpin = QSpinBox(minimum=0, maximum=10000, value=config.settings.value("Contour Size", 400, type=int))
        self.minContourSpin.setPrefix("Min Area: ")
        self.minContourSpin.valueChanged.connect(self.setContourSize)
        contourLayout.addWidget(self.minContourSpin)
        controlsLayout.addWidget(contourGroup)

        self.toggleThemeButton = QPushButton("Use Light Mode")
        self.toggleThemeButton.clicked.connect(self.toggleTheme)
        controlsLayout.addWidget(self.toggleThemeButton)

        self.isRecording = False
        self.toggleRecordingButton = QPushButton("Start Recording")
        self.toggleRecordingButton.clicked.connect(self.toggleRecording)
        controlsLayout.addWidget(self.toggleRecordingButton)
        
        self.updateViewButtonText()
        self.updateThemeButtonText()
        self.updateRecordingButtonText()

        controlsLayout.addStretch()
        
        scroll.setWidget(controlsWidget)
        mainLayout.addWidget(scroll)
        self.setLayout(mainLayout)

        self.setTheme()

    def toggleView(self):
        rawViewToggled = not config.settings.value("Raw View", True, type=bool)
        config.settings.setValue("Raw View", rawViewToggled)
        self.updateViewButtonText()

    def toggleTheme(self):
        lightModeToggled = not config.settings.value("Dark Mode", True, type=bool)
        config.settings.setValue("Dark Mode", lightModeToggled)
        self.setTheme()
        self.updateThemeButtonText()
    
    def setTheme(self):
        if config.settings.value("Dark Mode", True, type=bool):
            self.toggleThemeButton.setText("Use Light Mode")
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
            self.toggleThemeButton.setText("Use Dark Mode")
            QApplication.setStyle("")
            QApplication.setPalette(QPalette())

    def setBinaryThreshold(self):
        config.settings.setValue("Binary Threshold", self.thresholdSpinBox.value())

    def setContourSize(self):
        config.settings.setValue("Contour Size", self.minContourSpin.value())

    def toggleRecording(self):
        self.isRecording = not self.isRecording
        self.recordingToggled.emit(self.isRecording)
        self.updateRecordingButtonText()

    def updateRecordingButtonText(self):
        self.toggleRecordingButton.setText(
            "Stop Recording" if self.isRecording else "Start Recording"
        )

    def updateViewButtonText(self):
        processedView = config.settings.value("Raw View", True, type=bool)
        self.toggleViewButton.setText(
            "Show Processed View" if processedView else "Show Raw View"
        )

    def updateThemeButtonText(self):
        darkMode = config.settings.value("Dark Mode", True, type=bool)
        self.toggleThemeButton.setText(
            "Use Light Mode" if darkMode else "Use Dark Mode"
        )
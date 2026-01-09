from PyQt5 import QtCore

QtCore.QCoreApplication.setOrganizationName("2vyy")
QtCore.QCoreApplication.setApplicationName("Camera Vision Project")
 
settings = QtCore.QSettings()

settings.setValue("FRAME_THROTTLE_RATE", 1)
settings.setValue("CAMERA_WIDTH", 0)
settings.setValue("CAMERA_HEIGHT", 0)
settings.setValue("RECORDING_TOGGLE", False)

# Camera sources - list of (camera_id, camera_node_url) tuples
# For local testing, use localhost. In production, use real IPs.
CAMERA_SOURCES = [
    (0, "http://localhost:8000"),
    # (1, "http://192.168.1.101:8000"),
]

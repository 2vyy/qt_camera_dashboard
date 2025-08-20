from PyQt5 import QtCore

QtCore.QCoreApplication.setOrganizationName("2vyy")
QtCore.QCoreApplication.setApplicationName("Camera Vision Project")

settings = QtCore.QSettings()

settings.setValue("FRAME_THROTTLE_RATE", 1)
settings.setValue("CAMERA_WIDTH", 1280 // 2)
settings.setValue("CAMERA_HEIGHT", 720 // 2)
settings.setValue("CAMERA_INDEXES", {0})
settings.setValue("RECORDING_TOGGLE", False)
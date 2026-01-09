"""Configuration settings for the server node application."""
from PyQt5 import QtCore  # pylint: disable=c-extension-no-member

QtCore.QCoreApplication.setOrganizationName("2vyy")
QtCore.QCoreApplication.setApplicationName("Camera Vision Project")

settings = QtCore.QSettings()

settings.setValue("FRAME_THROTTLE_RATE", 1)
settings.setValue("CAMERA_WIDTH", 0)
settings.setValue("CAMERA_HEIGHT", 0)
settings.setValue("RECORDING_TOGGLE", False)
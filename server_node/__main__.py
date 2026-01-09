from PyQt5.QtWidgets import QApplication
from server_node.gui.app import App
import sys
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())

# non-cope TODO list:
# - figure out logs
# - fix recording output for several feeds (it currently overrides itself)
# - add time and FPS to feed
# - add console output to UI
# - give a notif when movement detected

# roadmap:
# - seperate video capture into nodes that feed to a shared processing node (server), use WebRTC or smth
# - add smart bandwidth saving features
# - use YOLOv8 or MobileNet SSD for object detection, support only searching for movement of certain objects (humans, cars, etc.)
# - facial recognition and memory
# - look into Deep SORT for tracking objects
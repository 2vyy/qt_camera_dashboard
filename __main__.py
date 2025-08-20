from PyQt5.QtWidgets import  QApplication
from App import App
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
import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
import ctypes
import platform

if platform.system() == "Windows":
    myappid = 'wlservices.signage.player.1.0.3'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
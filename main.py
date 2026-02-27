import sys, os
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from gui.main_window import MainWindow
from utils.path_helper import get_resource_path
import ctypes
import platform

if platform.system() == "Windows":
    myappid = 'wlservices.signage.player.1.0.3'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash_path = get_resource_path(os.path.join("data", "assets", "logo.png"))

    pixmap = QPixmap(splash_path)
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setAttribute(Qt.WA_TranslucentBackground)
    splash.show()
    splash.showMessage("Iniciando Sistema WL Signage...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)

    window = MainWindow()
    
    QTimer.singleShot(2500, lambda: (window.show(), splash.finish(window)))
    sys.exit(app.exec())
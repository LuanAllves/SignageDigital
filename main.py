import sys, os
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from gui.main_window import MainWindow
import ctypes
import platform

if platform.system() == "Windows":
    myappid = 'wlservices.signage.player.1.0.3'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    pixmap = QPixmap(os.path.join("gui", "assets", "splash.png"))
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setAttribute(Qt.WA_TranslucentBackground)
    splash.show()
    splash.showMessage("Iniciando Sistema WL Signage...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)

    window = MainWindow()
    
    QTimer.singleShot(2500, lambda: (window.show(), splash.finish(window)))
    sys.exit(app.exec())
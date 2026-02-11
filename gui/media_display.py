from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QUrl, QTimer, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

class MediaDisplayWindow(QWidget):
    closed = Signal()

    def __init__(self, media_list, is_muted_at_start=True, display_mode="Fullscreen"):
        super().__init__()
        self.media_list = media_list
        self.current_media_index = 0
        self.display_mode = display_mode # "Fullscreen" ou "Original"
        
        self.setCursor(Qt.BlankCursor)
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.setAttribute(Qt.WA_NativeWindow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        # No Fullscreen, queremos que a imagem ocupe tudo
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Importante: permitir que o conteúdo estique
        self.image_label.setScaledContents(True) 
        self.image_label.hide()

        self.video_widget = QVideoWidget()
        self.video_widget.hide()
        
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)
        
        self.set_muted(is_muted_at_start)
        
        self.image_timer = QTimer(self)
        self.image_timer.setSingleShot(True)
        self.image_timer.timeout.connect(self.play_next_media)
        
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(self.video_widget)
        
    def start_playback(self):
        self.play_next_media()

    def stop_playback(self):
        self.media_player.stop()
        if self.image_timer:
            self.image_timer.stop()
        self.close()
        self.deleteLater() 

    def play_next_media(self):
        if not self.media_list:
            self.stop_playback()
            return

        if self.current_media_index >= len(self.media_list):
            self.current_media_index = 0

        media_data = self.media_list[self.current_media_index]
        media_type = media_data[2]
        file_path = media_data[3]
        duration_seconds = media_data[4]

        self.image_label.hide()
        self.video_widget.hide()
        
        if media_type == "Imagem":
            self.play_image(file_path, duration_seconds)
        elif media_type == "Vídeo":
            self.play_video(file_path)

    def play_image(self, file_path, duration_seconds):
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            if self.display_mode == "Fullscreen":
                # Ignora a proporção para preencher a tela (causa distorção proposital)
                aspect_ratio = Qt.IgnoreAspectRatio
                self.resize(self.screen().size())
            else:
                # Mantém o tamanho real da imagem
                aspect_ratio = Qt.KeepAspectRatio
                self.resize(pixmap.size())

            scaled_pixmap = pixmap.scaled(
                self.size(), 
                aspect_ratio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.show()
            self.image_timer.start(duration_seconds * 1000)
            self.current_media_index += 1

    def play_video(self, file_path):
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        
        if self.display_mode == "Fullscreen":
            # Força o vídeo a esticar para preencher o QVideoWidget
            self.video_widget.setAspectRatioMode(Qt.IgnoreAspectRatio)
            self.resize(self.screen().size())
        else:
            # No modo original, teríamos que ajustar o tamanho da janela 
            # para o tamanho do vídeo (isso requer metadados do vídeo)
            self.video_widget.setAspectRatioMode(Qt.KeepAspectRatio)
            
        self.video_widget.show()
        self.media_player.play()

    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.current_media_index += 1
            self.play_next_media()

    # Metodo que para o Player ao aperta ESC (Desativada por Padrao)
    """def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.stop_playback()
        super().keyPressEvent(event)"""

    def set_muted(self, is_muted):
        self.audio_output.setMuted(is_muted)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
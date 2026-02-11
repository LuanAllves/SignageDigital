import os
import cv2
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, 
                               QGridLayout, QStyle, QCheckBox, QSizePolicy, QVBoxLayout)
from PySide6.QtGui import QPixmap, QColor, QImage
from PySide6.QtCore import Qt, Signal

# Dimensões padrão para as miniaturas
THUMBNAIL_WIDTH = 150
THUMBNAIL_HEIGHT = 100
VIDEO_THUMBNAIL_FRAME = 5

class MediaItemWidget(QWidget):
    edit_requested = Signal(object)
    checkbox_state_changed = Signal(object)

    def __init__(self, media_id, media_name, media_type, file_path, duration_seconds, scheduled_data, parent=None):
        super().__init__(parent)
        self.media_id = media_id 
        self.file_path = file_path
        self.media_type = media_type
        self.duration_seconds = duration_seconds
        
        self.schedule_start_date = scheduled_data.get('start_date')
        self.schedule_start_time = scheduled_data.get('start_time')
        self.schedule_end_date = scheduled_data.get('end_date')
        self.schedule_end_time = scheduled_data.get('end_time')

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.thumbnail_container = QWidget()
        self.thumbnail_container.setFixedSize(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)
        self.thumbnail_container.setStyleSheet("border: 1px solid #ccc; border-radius: 5px;")
        
        overlay_grid_layout = QGridLayout(self.thumbnail_container)
        overlay_grid_layout.setContentsMargins(0, 0, 0, 0)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        
        self.load_thumbnail(self.file_path)
        
        overlay_grid_layout.addWidget(self.thumbnail_label, 0, 0)
        
        overlay_buttons_widget = QWidget()
        overlay_buttons_widget.setStyleSheet("background-color: transparent;")
        
        overlay_layout = QHBoxLayout(overlay_buttons_widget)
        overlay_layout.setContentsMargins(5, 5, 5, 5)

        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px; }")
        self.checkbox.stateChanged.connect(lambda: self.checkbox_state_changed.emit(self))

        self.edit_button = QPushButton()
        self.edit_button.setFixedSize(30, 30)
        self.edit_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.edit_button.setStyleSheet("background-color: rgba(255, 255, 255, 100); border: none;")
        
        self.edit_button.clicked.connect(lambda: self.edit_requested.emit(self))

        overlay_layout.addWidget(self.checkbox, alignment=Qt.AlignTop | Qt.AlignLeft)
        overlay_layout.addStretch()
        overlay_layout.addWidget(self.edit_button, alignment=Qt.AlignTop | Qt.AlignRight)

        overlay_grid_layout.addWidget(overlay_buttons_widget, 0, 0)

        details_layout = QVBoxLayout()
        name_label = QLabel(f"<b>Nome:</b> {media_name}")
        type_label = QLabel(f"<b>Tipo:</b> {media_type}")
        
        self.duration_label = QLabel()
        self.schedule_label = QLabel()
        self.schedule_label.setWordWrap(True)
        
        details_layout.addWidget(name_label)
        details_layout.addWidget(type_label)
        details_layout.addWidget(self.duration_label)
        details_layout.addWidget(self.schedule_label)
        details_layout.addStretch()

        self.update_info_labels()
        
        main_layout.addWidget(self.thumbnail_container)
        main_layout.addLayout(details_layout)
        main_layout.addStretch()
    
    def update_info_labels(self):
        self.duration_label.setText(f"<b>Duração:</b> {self.duration_seconds} segundos")
        
        if self.schedule_start_date:
            schedule_text = f"Início: {self.schedule_start_date} às {self.schedule_start_time} <br>"
            if self.schedule_end_date:
                schedule_text += f"Fim: {self.schedule_end_date} às {self.schedule_end_time}"
            else:
                schedule_text += f"Fim: Não definido"
            self.schedule_label.setText(f"<b>Agendamento:</b><br>{schedule_text}")
        else:
            self.schedule_label.setText("<b>Agendamento:</b> Não agendado")

    def load_thumbnail(self, file_path):
        if not os.path.exists(file_path):
            self._display_placeholder()
            return

        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension in [".jpg", ".jpeg", ".png", ".gif"]:
            self._load_image_thumbnail(file_path)
        elif file_extension in [".mp4", ".avi", ".mov"]:
            self._load_video_thumbnail(file_path)
        else:
            self._display_placeholder()

    def _load_image_thumbnail(self, file_path):
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            self.thumbnail_label.setPixmap(pixmap.scaled(
                THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            self._display_placeholder()

    def _load_video_thumbnail(self, file_path):
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            self._display_placeholder()
            return
            
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        target_frame = VIDEO_THUMBNAIL_FRAME
        
        if target_frame >= frame_count:
            target_frame = 0
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        
        ret, frame = cap.read()
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            pixmap = QPixmap.fromImage(q_image)
            self.thumbnail_label.setPixmap(pixmap.scaled(
                THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            self._display_placeholder()
        cap.release()

    def _display_placeholder(self):
        placeholder_pixmap = QPixmap(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)
        placeholder_pixmap.fill(QColor(230, 230, 230))
        self.thumbnail_label.setPixmap(placeholder_pixmap)
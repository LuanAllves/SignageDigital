# ================ Início das Importações ======================
import sys
import os
import sqlite3
import cv2
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QListWidget,
                               QListWidgetItem, QCheckBox, QGridLayout, QStyle, 
                               QFileDialog, QDialog, QTimeEdit, QDialogButtonBox,
                               QSpinBox, QDateEdit, QSizePolicy, QRadioButton, QButtonGroup)
from PySide6.QtGui import QPixmap, QColor, QFont, QImage, QKeySequence
from PySide6.QtCore import Qt, QSize, Signal, QBuffer, QIODevice, QDate, QTime, QUrl, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
# ================ Fim das Importações ======================


# ================ Início das Classes ======================

# Classe para gerenciar o banco de dados SQLite
class DatabaseManager:
    def __init__(self, db_name="digital_signage.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.setup_database()

    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def setup_database(self):
        """Cria a tabela de mídias se ela não existir, com a nova coluna de duração."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medias (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                duration_seconds INTEGER,
                schedule_start_date TEXT,
                schedule_start_time TEXT,
                schedule_end_date TEXT,
                schedule_end_time TEXT
            )
        ''')
        self.conn.commit()

    def add_media(self, name, media_type, file_path, duration_seconds=None):
        """Adiciona uma nova mídia ao banco de dados."""
        self.cursor.execute('''
            INSERT INTO medias (name, type, file_path, duration_seconds, schedule_start_date, schedule_start_time, schedule_end_date, schedule_end_time)
            VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL)
        ''', (name, media_type, file_path, duration_seconds))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_medias(self):
        """Retorna todos os registros de mídias do banco de dados."""
        self.cursor.execute('SELECT * FROM medias')
        return self.cursor.fetchall()

    def delete_medias(self, media_ids):
        """Deleta mídias do banco de dados com base em seus IDs."""
        if not media_ids:
            return
        placeholders = ','.join('?' * len(media_ids))
        self.cursor.execute(f"DELETE FROM medias WHERE id IN ({placeholders})", media_ids)
        self.conn.commit()

    def update_media_schedule(self, media_id, start_date, start_time, end_date, end_time):
        """Atualiza o agendamento de uma mídia no banco de dados."""
        self.cursor.execute('''
            UPDATE medias
            SET schedule_start_date = ?,
                schedule_start_time = ?,
                schedule_end_date = ?,
                schedule_end_time = ?
            WHERE id = ?
        ''', (start_date, start_time, end_date, end_time, media_id))
        self.conn.commit()

    def update_media_duration(self, media_id, duration_seconds):
        """Atualiza a duração de uma mídia no banco de dados."""
        self.cursor.execute('''
            UPDATE medias
            SET duration_seconds = ?
            WHERE id = ?
        ''', (duration_seconds, media_id))
        self.conn.commit()
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        self.conn.close()


# Dimensões padrão para as miniaturas
THUMBNAIL_WIDTH = 200
THUMBNAIL_HEIGHT = 150
VIDEO_THUMBNAIL_FRAME = 5

# Esta classe representa um único item na nossa lista de mídias.
class MediaItemWidget(QWidget):
    edit_requested = Signal(object)
    checkbox_state_changed = Signal(object)

    def __init__(self, media_id, media_name, media_type, file_path, duration_seconds, scheduled_data, parent=None):
        super().__init__(parent)
        self.media_id = media_id 
        self.file_path = file_path
        self.media_type = media_type
        self.duration_seconds = duration_seconds
        
        # Armazena os dados de agendamento
        self.schedule_start_date = scheduled_data.get('start_date')
        self.schedule_start_time = scheduled_data.get('start_time')
        self.schedule_end_date = scheduled_data.get('end_date')
        self.schedule_end_time = scheduled_data.get('end_time')

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # --- Área da Miniatura com os botões sobrepostos ---
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

        # --- Área de Detalhes do Arquivo ---
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
        """Atualiza a label de duração e agendamento."""
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
        """Carrega a miniatura baseada no tipo de arquivo."""
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
        """Carrega a miniatura para arquivos de imagem."""
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            self.thumbnail_label.setPixmap(pixmap.scaled(
                THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            self._display_placeholder()

    def _load_video_thumbnail(self, file_path):
        """Extrai um frame de um vídeo como miniatura."""
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
        """Exibe uma miniatura placeholder cinza."""
        placeholder_pixmap = QPixmap(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)
        placeholder_pixmap.fill(QColor(230, 230, 230))
        self.thumbnail_label.setPixmap(placeholder_pixmap)


# Nova Janela de Edição de Mídia
class MediaEditDialog(QDialog):
    def __init__(self, media_type, duration_seconds, scheduled_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Mídia")
        self.setGeometry(200, 200, 400, 450)
        
        dialog_layout = QVBoxLayout(self)

        # Duração (apenas para imagens)
        self.duration_layout = QHBoxLayout()
        self.duration_label = QLabel("<b>Duração (segundos):</b>")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(1)
        self.duration_spinbox.setMaximum(3600)
        self.duration_spinbox.setValue(duration_seconds)
        self.duration_layout.addWidget(self.duration_label)
        self.duration_layout.addWidget(self.duration_spinbox)
        self.duration_layout.addStretch()
        dialog_layout.addLayout(self.duration_layout)
        
        # Esconde/mostra a duração dependendo do tipo de mídia
        if media_type != "Imagem":
            self.duration_label.hide()
            self.duration_spinbox.hide()

        # Agendamento de Início
        start_label = QLabel("<b>Agendamento de Início:</b>")
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        self.start_time_edit.setTime(QTime.currentTime())
        dialog_layout.addWidget(start_label)
        
        start_schedule_layout = QHBoxLayout()
        start_schedule_layout.addWidget(self.start_date_edit)
        start_schedule_layout.addWidget(self.start_time_edit)
        dialog_layout.addLayout(start_schedule_layout)
        
        # Agendamento de Fim (opcional)
        end_label = QLabel("<b>Agendamento de Fim:</b>")
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        self.clear_end_button = QPushButton("Limpar Agendamento")
        
        dialog_layout.addWidget(end_label)
        end_schedule_layout = QHBoxLayout()
        end_schedule_layout.addWidget(self.end_date_edit)
        end_schedule_layout.addWidget(self.end_time_edit)
        end_schedule_layout.addWidget(self.clear_end_button)
        dialog_layout.addLayout(end_schedule_layout)
        
        self.clear_end_button.clicked.connect(self._clear_end_schedule)
        self.end_date_edit.dateChanged.connect(lambda: self._set_end_schedule_enabled(True))
        self.end_time_edit.timeChanged.connect(lambda: self._set_end_schedule_enabled(True))

        if scheduled_data.get('start_date'):
            start_date = QDate.fromString(scheduled_data['start_date'], "dd/MM/yyyy")
            start_time = QTime.fromString(scheduled_data['start_time'], "HH:mm")
            self.start_date_edit.setDate(start_date)
            self.start_time_edit.setTime(start_time)
            
        if scheduled_data.get('end_date'):
            end_date = QDate.fromString(scheduled_data['end_date'], "dd/MM/yyyy")
            end_time = QTime.fromString(scheduled_data['end_time'], "HH:mm")
            self.end_date_edit.setDate(end_date)
            self.end_time_edit.setTime(end_time)
        else:
            self._clear_end_schedule()

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        dialog_layout.addWidget(button_box)

    def _set_end_schedule_enabled(self, enabled):
        self.end_date_edit.setEnabled(enabled)
        self.end_time_edit.setEnabled(enabled)

    def _clear_end_schedule(self):
        """Limpa e desabilita os campos de agendamento de fim."""
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_time_edit.setTime(QTime(0, 0))
        self._set_end_schedule_enabled(False)

    def get_schedule_data(self):
        start_date = self.start_date_edit.date().toString("dd/MM/yyyy")
        start_time = self.start_time_edit.time().toString("HH:mm")
        
        end_date = None
        end_time = None
        if self.end_date_edit.isEnabled():
            end_date = self.end_date_edit.date().toString("dd/MM/yyyy")
            end_time = self.end_time_edit.time().toString("HH:mm")
        
        duration = self.duration_spinbox.value()
        
        return {
            "start_date": start_date,
            "start_time": start_time,
            "end_date": end_date,
            "end_time": end_time,
            "duration": duration
        }


class MediaDisplayWindow(QWidget):
    def __init__(self, media_list, is_muted_at_start=True):
        super().__init__()
        self.media_list = media_list
        self.current_media_index = 0
        
        self.setCursor(Qt.BlankCursor)
        self.setStyleSheet("background-color: black;")
        
        # Adiciona a bandeira para remover a moldura da janela
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Para imagens
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.image_label.hide()

        # Para vídeos
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
        self.showFullScreen()
        self.play_next_media()

    def stop_playback(self):
        self.media_player.stop()
        self.image_timer.stop()
        self.close()

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
            scaled_pixmap = pixmap.scaled(
                self.screen().size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.show()
            self.image_timer.start(duration_seconds * 1000)
            self.current_media_index += 1

    def play_video(self, file_path):
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.video_widget.show()
        self.media_player.play()

    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.current_media_index += 1
            self.play_next_media()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.stop_playback()
        super().keyPressEvent(event)

    def set_muted(self, is_muted):
        """Define o estado do áudio."""
        self.audio_output.setMuted(is_muted)


# Classe Principal
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Signage")
        self.setGeometry(100, 100, 800, 600)
        self.db_manager = DatabaseManager()
        self.player_window = None 
        self.is_muted = True # Áudio mudo por padrão
        self.setup_ui()
        self.load_media_from_db()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # ------- 1. Menu Superior ---------
        toolbar_layout = QHBoxLayout()
        logo_label = QLabel("Digital Signage")
        logo_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.upload_button = QPushButton("Upload de Mídia")
        self.upload_button.setFixedSize(150, 40)

        toolbar_layout.addWidget(logo_label)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.upload_button)
        main_layout.addLayout(toolbar_layout)

        # --- 2. Área de Controle Principal ---
        control_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.delete_button = QPushButton("Delete")
        self.delete_button.setDisabled(True)
        
        self.audio_button = QPushButton()
        self.audio_button.setFixedSize(30, 30)
        self.audio_button.clicked.connect(self.toggle_audio)
        self.toggle_audio(initial=True) 

        # --- Seleção de Tela (Novo) ---
        self.screen_selector_layout = QHBoxLayout()
        screen_label = QLabel("Selecionar Tela:")
        self.screen_selector_layout.addWidget(screen_label)
        
        self.screen_button_group = QButtonGroup(self)
        self.populate_screen_selector()
        
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.delete_button)
        control_layout.addWidget(self.audio_button)
        
        control_layout.addStretch()
        control_layout.addLayout(self.screen_selector_layout) # Adiciona o layout de seleção

        main_layout.addLayout(control_layout)

        # --- 3. Área de Exibição de Mídias ---
        self.media_list_widget = QListWidget()
        self.media_list_widget.setViewMode(QListWidget.IconMode)
        self.media_list_widget.setResizeMode(QListWidget.Adjust)
        self.media_list_widget.setGridSize(QSize(THUMBNAIL_WIDTH + 180, THUMBNAIL_HEIGHT + 50))
        self.media_list_widget.setIconSize(QSize(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
        
        self.media_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.media_list_widget.itemSelectionChanged.connect(self.update_delete_button)
        
        main_layout.addWidget(self.media_list_widget)

        self.upload_button.clicked.connect(self.upload_media)
        self.delete_button.clicked.connect(self.delete_selected_items)
        self.play_button.clicked.connect(self.play_media)
        self.stop_button.clicked.connect(self.stop_media)

    def populate_screen_selector(self):
        """Detecta e adiciona botões para cada tela conectada."""
        screens = QApplication.screens()
        for i, screen in enumerate(screens):
            radio_button = QRadioButton(f"Tela {i+1}")
            self.screen_button_group.addButton(radio_button, i)
            self.screen_selector_layout.addWidget(radio_button)
        
        if screens:
            self.screen_button_group.buttons()[0].setChecked(True)

    def get_selected_screen(self):
        """Retorna o objeto QScreen correspondente à tela selecionada."""
        checked_id = self.screen_button_group.checkedId()
        # Busque a tela no momento da execução para garantir que a referência seja válida
        screens = QApplication.screens()
        if checked_id != -1 and checked_id < len(screens):
            return screens[checked_id]
        # Retorna a tela principal como fallback
        return QApplication.primaryScreen()
    
    def load_media_from_db(self):
        """Carrega todas as mídias salvas no banco de dados e as exibe na interface."""
        self.media_list_widget.clear()
        medias = self.db_manager.get_all_medias()
        for media in medias:
            media_id, name, media_type, file_path, duration_seconds, start_date, start_time, end_date, end_time = media
            
            scheduled_data = {
                'start_date': start_date,
                'start_time': start_time,
                'end_date': end_date,
                'end_time': end_time
            }
            
            self.add_media_item(media_id, name, media_type, file_path, duration_seconds, scheduled_data)

    def add_media_item(self, media_id, name, type, file_path, duration, scheduled_data):
        item_widget = MediaItemWidget(media_id, name, type, file_path, duration, scheduled_data)
        
        item_widget.edit_requested.connect(lambda widget: self.open_schedule_dialog(widget))
        item_widget.checkbox_state_changed.connect(lambda widget: self.update_delete_button())

        list_item = QListWidgetItem(self.media_list_widget)
        list_item.setSizeHint(item_widget.sizeHint())
        self.media_list_widget.addItem(list_item)
        self.media_list_widget.setItemWidget(list_item, item_widget)

    def upload_media(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilters(["Mídias Suportadas (*.jpg *.jpeg *.png *.gif *.mp4 *.avi *.mov)"])
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            
            for file_path in selected_files:
                file_name = os.path.basename(file_path)
                file_extension = os.path.splitext(file_name)[1].lower()
                
                duration_seconds = None
                
                if file_extension in [".jpg", ".jpeg", ".png", ".gif"]:
                    file_type = "Imagem"
                    duration_seconds = 5
                elif file_extension in [".mp4", ".avi", ".mov"]:
                    file_type = "Vídeo"
                    cap = cv2.VideoCapture(file_path)
                    if cap.isOpened():
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        duration_seconds = int(frame_count / fps) if fps > 0 else 0
                        cap.release()
                else:
                    file_type = "Outro"
                
                media_id = self.db_manager.add_media(file_name, file_type, file_path, duration_seconds)
                scheduled_data = {'start_date': None, 'start_time': None, 'end_date': None, 'end_time': None}
                self.add_media_item(media_id, file_name, file_type, file_path, duration_seconds, scheduled_data)

    def open_schedule_dialog(self, media_item_widget):
        scheduled_data = {
            'start_date': media_item_widget.schedule_start_date,
            'start_time': media_item_widget.schedule_start_time,
            'end_date': media_item_widget.schedule_end_date,
            'end_time': media_item_widget.schedule_end_time
        }
        
        dialog = MediaEditDialog(media_item_widget.media_type, media_item_widget.duration_seconds, scheduled_data, self)
        
        if dialog.exec():
            new_data = dialog.get_schedule_data()
            
            self.db_manager.update_media_schedule(
                media_item_widget.media_id,
                new_data['start_date'],
                new_data['start_time'],
                new_data['end_date'],
                new_data['end_time']
            )

            if media_item_widget.media_type == "Imagem":
                self.db_manager.update_media_duration(media_item_widget.media_id, new_data['duration'])
                media_item_widget.duration_seconds = new_data['duration']
            
            media_item_widget.schedule_start_date = new_data['start_date']
            media_item_widget.schedule_start_time = new_data['start_time']
            media_item_widget.schedule_end_date = new_data['end_date']
            media_item_widget.schedule_end_time = new_data['end_time']
            
            media_item_widget.update_info_labels()

    def update_delete_button(self):
        is_any_checked = False
        for i in range(self.media_list_widget.count()):
            item = self.media_list_widget.item(i)
            item_widget = self.media_list_widget.itemWidget(item)
            if item_widget and item_widget.checkbox.isChecked():
                is_any_checked = True
                break
        
        is_any_selected = len(self.media_list_widget.selectedItems()) > 0
        self.delete_button.setDisabled(not (is_any_checked or is_any_selected))

    def delete_selected_items(self):
        items_to_delete = []
        media_ids_to_delete = []
        
        for item in self.media_list_widget.selectedItems():
            item_widget = self.media_list_widget.itemWidget(item)
            if item not in items_to_delete:
                items_to_delete.append(item)
                media_ids_to_delete.append(item_widget.media_id)

        for i in range(self.media_list_widget.count()):
            item = self.media_list_widget.item(i)
            item_widget = self.media_list_widget.itemWidget(item)
            if item_widget and item_widget.checkbox.isChecked():
                if item not in items_to_delete:
                    items_to_delete.append(item)
                    media_ids_to_delete.append(item_widget.media_id)
        
        self.db_manager.delete_medias(media_ids_to_delete)

        for item in sorted(items_to_delete, key=self.media_list_widget.row, reverse=True):
            row = self.media_list_widget.row(item)
            self.media_list_widget.takeItem(row)

    def play_media(self):
        media_list = self.db_manager.get_all_medias()
        if not media_list:
            return

        # Obtenha a tela selecionada diretamente do botão
        selected_screen = self.get_selected_screen()
        
        self.player_window = MediaDisplayWindow(media_list, is_muted_at_start=self.is_muted)
        
        # Mova a janela para a tela selecionada antes de exibi-la
        if selected_screen:
            self.player_window.move(selected_screen.geometry().topLeft())
        
        self.player_window.show()
        self.player_window.showFullScreen()
        self.player_window.start_playback()

    def stop_media(self):
        if self.player_window:
            self.player_window.stop_playback()
            self.player_window = None

    def toggle_audio(self, initial=False):
        if not initial:
            self.is_muted = not self.is_muted
        
        if self.is_muted:
            icon = self.style().standardIcon(QStyle.SP_MediaVolumeMuted)
        else:
            icon = self.style().standardIcon(QStyle.SP_MediaVolume)
        self.audio_button.setIcon(icon)

        if self.player_window:
            self.player_window.set_muted(self.is_muted)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
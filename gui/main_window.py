import os
import platform
import cv2
from PySide6 import Shiboken
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QListWidget, QListWidgetItem, 
                               QStyle, QFileDialog, QButtonGroup, QRadioButton, QApplication)
from PySide6.QtCore import Qt, QSize, QTimer
from gui.media_item import MediaItemWidget, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT
from gui.media_edit_dialog import MediaEditDialog
from gui.media_display import MediaDisplayWindow
from utils.database import DatabaseManager

class MainWindow(QMainWindow):

    def __init__(self):
        
        self.media_dir = os.path.join(os.getcwd(), "media_files")
        if not os.path.exists(self.media_dir):
            os.makedirs(self.media_dir)

        super().__init__()
        self.setWindowTitle("Digital Signage")
        self.setGeometry(100, 100, 800, 600)
        self.db_manager = DatabaseManager()
        self.player_window = None 
        self.is_muted = True
        self.setup_ui()
        self.load_media_from_db()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        toolbar_layout = QHBoxLayout()
        logo_label = QLabel("Digital Signage")
        logo_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.upload_button = QPushButton("Upload de Mídia")
        self.upload_button.setFixedSize(150, 40)

        toolbar_layout.addWidget(logo_label)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.upload_button)
        main_layout.addLayout(toolbar_layout)

        control_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.delete_button = QPushButton("Delete")
        self.stop_button.setDisabled(True)
        self.delete_button.setDisabled(True)
        
        self.audio_button = QPushButton()
        self.audio_button.setFixedSize(30, 30)
        self.audio_button.clicked.connect(self.toggle_audio)
        self.toggle_audio(initial=True) 

        self.mode_group = QButtonGroup(self)
        self.full_screen_radio = QRadioButton("FullScreen")
        self.original_radio = QRadioButton("Keep Aspect")
        
        self.mode_group.addButton(self.full_screen_radio)
        self.mode_group.addButton(self.original_radio)
        self.full_screen_radio.setChecked(True) # Padrão é FullScreen
        
        control_layout.addWidget(self.full_screen_radio)
        control_layout.addWidget(self.original_radio)

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
        control_layout.addLayout(self.screen_selector_layout)

        main_layout.addLayout(control_layout)

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
        screens = QApplication.screens()
        for i, screen in enumerate(screens):
            radio_button = QRadioButton(f"Tela {i+1}")
            self.screen_button_group.addButton(radio_button, i)
            self.screen_selector_layout.addWidget(radio_button)
        
        if screens:
            self.screen_button_group.buttons()[0].setChecked(True)

    def get_selected_screen(self):
        screens = QApplication.screens()
        checked_id = self.screen_button_group.checkedId()
        if checked_id != -1 and checked_id < len(screens):
            return screens[checked_id]
        return QApplication.primaryScreen()
    
    def load_media_from_db(self):
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
        # 1. Busca mídias ativas no banco (Filtro de agendamento)
        media_list = self.db_manager.get_active_medias()

        if not media_list:
            print("Nenhuma mídia ativa para exibir.")
            return
        
        # 2. Limpeza de segurança: Garante que não existam dois players rodando
        if self.player_window:
            try:
                if Shiboken.isValid(self.player_window): 
                    self.player_window.stop_playback()
                    self.player_window.deleteLater()
            except Exception as e:
                print(f"Erro ao limpar player anterior: {e}")
            self.player_window = None

        # 3. Captura configurações da interface
        display_mode = "Fullscreen" if self.full_screen_radio.isChecked() else "Original"
        selected_screen = self.get_selected_screen()
        screen_geometry = selected_screen.geometry()

        # 4. Instancia o player (sem mostrar ainda)
        self.player_window = MediaDisplayWindow(
            media_list, 
            is_muted_at_start=self.is_muted,
            display_mode=display_mode
        )
        
        # Conecta o sinal para reativar os botões quando o player fechar
        self.player_window.closed.connect(lambda: self.update_playback_buttons(False))

        # 5. Lógica de Posicionamento por Sistema Operacional
        if platform.system() == "Windows":
            # No Windows, vinculamos a tela e movemos para a coordenada absoluta.
            # Se a Tela 2 começa em X=1920, move(1920, 0) coloca ela lá instantaneamente.
            self.player_window.setScreen(selected_screen)
            self.player_window.move(screen_geometry.topLeft())
            
            if display_mode == "Fullscreen":
                self.player_window.showFullScreen()
            else:
                self.player_window.show()
        else:
            # No Linux (Wayland/COSMIC), o SO ignora o move().
            # Tentamos o setScreen, mas o Linux geralmente decide a tela sozinho.
            self.player_window.setScreen(selected_screen)
            self.player_window.setGeometry(screen_geometry)
            
            if display_mode == "Fullscreen":
                self.player_window.showFullScreen()
            else:
                self.player_window.show()
            
            # Força o foco no Linux
            self.player_window.raise_()
            self.player_window.activateWindow()

        # 6. Inicia o ciclo de reprodução e atualiza botões
        self.player_window.start_playback()
        self.update_playback_buttons(True)

    def stop_media(self):
        if self.player_window:
            self.player_window.stop_playback()
            self.player_window = None
        self.update_playback_buttons(False)

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

    def update_playback_buttons(self, is_playing):
        """Ativa/Desativa botões baseado no estado do player."""
        self.play_button.setDisabled(is_playing)
        self.stop_button.setEnabled(is_playing)
        self.upload_button.setDisabled(is_playing)
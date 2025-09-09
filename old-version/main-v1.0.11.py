# ================ Início das Importações ======================
import sys
import os
import sqlite3
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QListWidget,
                               QListWidgetItem, QCheckBox, QGridLayout, QStyle, 
                               QFileDialog, QDialog, QCalendarWidget, QTimeEdit, QDialogButtonBox)
from PySide6.QtGui import QPixmap, QColor, QFont
from PySide6.QtCore import Qt, QSize, Signal
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
        """Cria a tabela de mídias se ela não existir."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medias (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                schedule_start_date TEXT,
                schedule_start_time TEXT,
                schedule_end_date TEXT,
                schedule_end_time TEXT
            )
        ''')
        self.conn.commit()

    def add_media(self, name, media_type, file_path):
        """Adiciona uma nova mídia ao banco de dados."""
        self.cursor.execute('''
            INSERT INTO medias (name, type, file_path, schedule_start_date, schedule_start_time, schedule_end_date, schedule_end_time)
            VALUES (?, ?, ?, NULL, NULL, NULL, NULL)
        ''', (name, media_type, file_path))
        self.conn.commit()
        return self.cursor.lastrowid # Retorna o ID do novo item

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
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        self.conn.close()


# Esta classe representa um único item na nossa lista de mídias.
class MediaItemWidget(QWidget):
    edit_requested = Signal(object)
    checkbox_state_changed = Signal(object)

    def __init__(self, media_id, media_name, media_type, scheduled_date, parent=None):
        super().__init__(parent)
        self.media_id = media_id # Armazena o ID do banco de dados no widget
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # --- Área da Miniatura com os botões sobrepostos ---
        self.thumbnail_container = QWidget()
        self.thumbnail_container.setFixedSize(200, 150)
        self.thumbnail_container.setStyleSheet("border: 1px solid #ccc; border-radius: 5px;")
        
        overlay_grid_layout = QGridLayout(self.thumbnail_container)
        overlay_grid_layout.setContentsMargins(0, 0, 0, 0)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        
        placeholder_pixmap = QPixmap(200, 150)
        placeholder_pixmap.fill(QColor(230, 230, 230))
        self.thumbnail_label.setPixmap(placeholder_pixmap)
        
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
        
        self.schedule_label = QLabel(f"<b>Agendamento:</b> {scheduled_date}")
        self.schedule_label.setWordWrap(True)
        
        details_layout.addWidget(name_label)
        details_layout.addWidget(type_label)
        details_layout.addWidget(self.schedule_label)
        details_layout.addStretch()
        
        main_layout.addWidget(self.thumbnail_container)
        main_layout.addLayout(details_layout)
        main_layout.addStretch()
    
    def set_schedule_text(self, text):
        self.schedule_label.setText(f"<b>Agendamento:</b> {text}")


# Janela de Agendamento
class ScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Agendamento")
        self.setGeometry(200, 200, 400, 600)
        
        dialog_layout = QVBoxLayout(self)

        start_label = QLabel("<b>Agendamento de Início:</b>")
        dialog_layout.addWidget(start_label)
        
        self.start_date_calendar = QCalendarWidget()
        dialog_layout.addWidget(self.start_date_calendar)
        
        start_time_label = QLabel("Selecione a Hora de Início:")
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        dialog_layout.addWidget(start_time_label)
        dialog_layout.addWidget(self.start_time_edit)

        end_label = QLabel("<b>Agendamento de Fim:</b>")
        dialog_layout.addWidget(end_label)

        self.end_date_calendar = QCalendarWidget()
        dialog_layout.addWidget(self.end_date_calendar)

        end_time_label = QLabel("Selecione a Hora de Fim:")
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        dialog_layout.addWidget(end_time_label)
        dialog_layout.addWidget(self.end_time_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        dialog_layout.addWidget(button_box)

    def get_schedule_data(self):
        start_date = self.start_date_calendar.selectedDate().toString("dd/MM/yyyy")
        start_time = self.start_time_edit.time().toString("HH:mm")
        end_date = self.end_date_calendar.selectedDate().toString("dd/MM/yyyy")
        end_time = self.end_time_edit.time().toString("HH:mm")
        
        return {
            "start_date": start_date,
            "start_time": start_time,
            "end_date": end_date,
            "end_time": end_time
        }


# Classe Principal
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Signage")
        self.setGeometry(100, 100, 800, 600)
        self.db_manager = DatabaseManager()
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
        play_button = QPushButton("Play")
        stop_button = QPushButton("Stop")
        self.delete_button = QPushButton("Delete")
        self.delete_button.setDisabled(True)

        control_layout.addWidget(play_button)
        control_layout.addWidget(stop_button)
        control_layout.addWidget(self.delete_button)
        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        # --- 3. Área de Exibição de Mídias ---
        self.media_list_widget = QListWidget()
        self.media_list_widget.setViewMode(QListWidget.IconMode)
        self.media_list_widget.setResizeMode(QListWidget.Adjust)
        self.media_list_widget.setGridSize(QSize(380, 200))
        self.media_list_widget.setIconSize(QSize(200, 150))
        
        self.media_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.media_list_widget.itemSelectionChanged.connect(self.update_delete_button)
        
        main_layout.addWidget(self.media_list_widget)

        self.upload_button.clicked.connect(self.upload_media)
        self.delete_button.clicked.connect(self.delete_selected_items)
    
    def load_media_from_db(self):
        """Carrega todas as mídias salvas no banco de dados e as exibe na interface."""
        medias = self.db_manager.get_all_medias()
        for media in medias:
            # Assumimos que a ordem é: id, name, type, file_path, start_date, etc.
            media_id, name, media_type, file_path, start_date, start_time, end_date, end_time = media
            
            # Formata a label de agendamento
            if not start_date:
                schedule_text = "Não agendado"
            else:
                schedule_text = f"Início: {start_date} às {start_time} <br> Fim: {end_date} às {end_time}"
            
            self.add_media_item(media_id, name, media_type, schedule_text)

    def add_media_item(self, media_id, name, type, date):
        item_widget = MediaItemWidget(media_id, name, type, date)
        
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
                
                if file_extension in [".jpg", ".jpeg", ".png", ".gif"]:
                    file_type = "Imagem"
                elif file_extension in [".mp4", ".avi", ".mov"]:
                    file_type = "Vídeo"
                else:
                    file_type = "Outro"
                
                # Salva a nova mídia no banco de dados e obtém o ID
                media_id = self.db_manager.add_media(file_name, file_type, file_path)
                
                # Adiciona o item à interface com o ID
                self.add_media_item(media_id, file_name, file_type, "Não agendado")

    def open_schedule_dialog(self, media_item_widget):
        dialog = ScheduleDialog(self)
        if dialog.exec():
            schedule_data = dialog.get_schedule_data()
            start = f"Início: {schedule_data['start_date']} às {schedule_data['start_time']}"
            end = f"Fim: {schedule_data['end_date']} às {schedule_data['end_time']}"
            
            # Atualiza o agendamento no banco de dados
            self.db_manager.update_media_schedule(
                media_item_widget.media_id,
                schedule_data['start_date'],
                schedule_data['start_time'],
                schedule_data['end_date'],
                schedule_data['end_time']
            )
            
            # Atualiza a label na interface
            media_item_widget.set_schedule_text(f"{start} <br> {end}")

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
        
        # Coleta os itens selecionados
        for item in self.media_list_widget.selectedItems():
            item_widget = self.media_list_widget.itemWidget(item)
            if item not in items_to_delete:
                items_to_delete.append(item)
                media_ids_to_delete.append(item_widget.media_id)

        # Coleta os itens com o checkbox marcado
        for i in range(self.media_list_widget.count()):
            item = self.media_list_widget.item(i)
            item_widget = self.media_list_widget.itemWidget(item)
            if item_widget and item_widget.checkbox.isChecked():
                if item not in items_to_delete:
                    items_to_delete.append(item)
                    media_ids_to_delete.append(item_widget.media_id)
        
        # Deleta as mídias do banco de dados primeiro
        self.db_manager.delete_medias(media_ids_to_delete)

        # Deleta os itens da interface, iterando de trás para frente
        for item in sorted(items_to_delete, key=self.media_list_widget.row, reverse=True):
            row = self.media_list_widget.row(item)
            self.media_list_widget.takeItem(row)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
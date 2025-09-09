# ================ Início das Importações ======================
import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QListWidget,
                               QListWidgetItem, QCheckBox, QGridLayout, QStyle, 
                               QFileDialog, QDialog, QCalendarWidget, QTimeEdit, QDialogButtonBox)
from PySide6.QtGui import QPixmap, QColor, QFont
from PySide6.QtCore import Qt, QSize, Signal
# ================ Fim das Importações ======================


# ================ Início das Classes ======================

# Esta classe representa um único item na nossa lista de mídias.
class MediaItemWidget(QWidget):
    # O sinal agora envia uma referência para si mesmo.
    edit_requested = Signal(object)

    def __init__(self, media_name, media_type, scheduled_date, parent=None):
        super().__init__(parent)
        
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
        
        self.edit_button = QPushButton()
        self.edit_button.setFixedSize(30, 30)
        self.edit_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.edit_button.setStyleSheet("background-color: rgba(255, 255, 255, 100); border: none;")
        
        # Conecta o botão ao nosso sinal, emitindo 'self'
        self.edit_button.clicked.connect(lambda: self.edit_requested.emit(self))

        overlay_layout.addWidget(self.checkbox, alignment=Qt.AlignTop | Qt.AlignLeft)
        overlay_layout.addStretch()
        overlay_layout.addWidget(self.edit_button, alignment=Qt.AlignTop | Qt.AlignRight)

        overlay_grid_layout.addWidget(overlay_buttons_widget, 0, 0)

        # --- Área de Detalhes do Arquivo ---
        details_layout = QVBoxLayout()
        name_label = QLabel(f"<b>Nome:</b> {media_name}")
        type_label = QLabel(f"<b>Tipo:</b> {media_type}")
        
        # Guardamos a referência da label para poder atualizá-la
        self.schedule_label = QLabel(f"<b>Agendamento:</b> {scheduled_date}")
        
        details_layout.addWidget(name_label)
        details_layout.addWidget(type_label)
        details_layout.addWidget(self.schedule_label)
        details_layout.addStretch()
        
        main_layout.addWidget(self.thumbnail_container)
        main_layout.addLayout(details_layout)
        main_layout.addStretch()
    
    # Método para atualizar a label de agendamento
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
        
        self.setup_ui()

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
        delete_button = QPushButton("Delete")

        control_layout.addWidget(play_button)
        control_layout.addWidget(stop_button)
        control_layout.addWidget(delete_button)
        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        # --- 3. Área de Exibição de Mídias ---
        self.media_list_widget = QListWidget()
        self.media_list_widget.setViewMode(QListWidget.IconMode)
        self.media_list_widget.setResizeMode(QListWidget.Adjust)
        self.media_list_widget.setGridSize(QSize(380, 200))
        self.media_list_widget.setIconSize(QSize(200, 150))
        
        main_layout.addWidget(self.media_list_widget)

        self.upload_button.clicked.connect(self.upload_media)

        self.add_media_item("Video Promo.mp4", "Vídeo", "Não agendado")
        self.add_media_item("Anuncio Loja.jpg", "Imagem", "Não agendado")
    
    def add_media_item(self, name, type, date):
        item_widget = MediaItemWidget(name, type, date)
        
        # Conecta o sinal do widget ao método, passando o próprio widget como argumento
        item_widget.edit_requested.connect(lambda: self.open_schedule_dialog(item_widget))

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
                
                self.add_media_item(file_name, file_type, "Não agendado")

    def open_schedule_dialog(self, media_item_widget):
        dialog = ScheduleDialog(self)
        if dialog.exec():
            schedule_data = dialog.get_schedule_data()
            start = f"Início: {schedule_data['start_date']} às {schedule_data['start_time']}"
            end = f"Fim: {schedule_data['end_date']} às {schedule_data['end_time']}"
            
            # Atualiza a label do item clicado
            media_item_widget.set_schedule_text(f"{start} <br> {end}")
        else:
            print("Agendamento cancelado.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
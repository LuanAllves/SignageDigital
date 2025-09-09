# ================ Inicio das Importações ======================
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QListWidget, 
                               QListWidgetItem, QCheckBox, QStackedLayout, QStyle)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize, QUrl

# ================ Fim das Importações ======================


# ================ Inicio das classes ======================

# Esta classe representa um único item na nossa lista de mídias.
class MediaItemWidget(QWidget):
    def __init__(self, media_name, media_type, scheduled_date, parent=None):
        super().__init__(parent)
        
        # O layout principal deste widget personalizado é horizontal.
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)

        # --- Área da Miniatura com os botões sobrepostos ---
        self.thumbnail_container = QWidget()
        self.thumbnail_container.setFixedSize(200, 150)
        self.thumbnail_container.setStyleSheet("border: 1px solid #ccc; border-radius: 5px;")
        
        # QStackedLayout para sobrepor a miniatura e a camada de botões
        stacked_layout = QStackedLayout(self.thumbnail_container)
        
        # Camada 1: Miniatura
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        
        # Simulação de uma miniatura.
        placeholder_pixmap = QPixmap(200, 150)
        placeholder_pixmap.fill(Qt.lightGray)
        self.thumbnail_label.setPixmap(placeholder_pixmap)
        
        # Camada 2: Camada de botões sobreposta
        overlay_widget = QWidget()
        overlay_layout = QHBoxLayout(overlay_widget)
        overlay_layout.setContentsMargins(5, 5, 5, 5)

        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("QCheckBox::indicator { width: 25px; height: 25px; }")
        
        self.edit_button = QPushButton()
        self.edit_button.setFixedSize(30, 30)
        self.edit_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView)) # Exemplo de ícone de edição
        self.edit_button.setStyleSheet("background-color: rgba(255, 255, 255, 100); border: none;") # Estilo semi-transparente

        overlay_layout.addWidget(self.checkbox, alignment=Qt.AlignTop | Qt.AlignLeft)
        overlay_layout.addStretch()
        overlay_layout.addWidget(self.edit_button, alignment=Qt.AlignTop | Qt.AlignRight)

        # Adiciona as duas camadas ao layout empilhado
        stacked_layout.addWidget(self.thumbnail_label)
        stacked_layout.addWidget(overlay_widget)

        # --- Área de Detalhes do Arquivo ---
        details_layout = QVBoxLayout()
        name_label = QLabel(f"<b>Nome:</b> {media_name}")
        type_label = QLabel(f"<b>Tipo:</b> {media_type}")
        schedule_label = QLabel(f"<b>Agendamento:</b> {scheduled_date}")
        
        details_layout.addWidget(name_label)
        details_layout.addWidget(type_label)
        details_layout.addWidget(schedule_label)
        details_layout.addStretch()
        
        # Adiciona tudo ao layout principal do item
        main_layout.addWidget(self.thumbnail_container)
        main_layout.addLayout(details_layout)
        main_layout.addStretch()




# Clase Principal
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Signage")
        self.setGeometry(100, 100, 800, 600) # Posicionamento e tamanha inicial.
        
        self.setup_ui()

    def setup_ui(self):
        # Widget Principal que vai conter todos o nossos layout.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal que organiza os elementos verticalmente.
        main_layout = QVBoxLayout(central_widget)

        # -------  1. Menu Superior  ---------
        toolbar_layout = QHBoxLayout()

        logo_label = QLabel("Digital Signage")
        logo_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        upload_button = QPushButton("Upload de Mídia")
        upload_button.setFixedSize(150, 40)

        toolbar_layout.addWidget(logo_label)
        toolbar_layout.addStretch()  # Adiciona um espaço flexível para empurrar o botão para a direita
        toolbar_layout.addWidget(upload_button)

        main_layout.addLayout(toolbar_layout)

        # --- 2. Área de Controle Principal ---
        control_layout = QHBoxLayout()

        play_button = QPushButton("Play")
        stop_button = QPushButton("Stop")
        delete_button = QPushButton("Delete")

        control_layout.addWidget(play_button)
        control_layout.addWidget(stop_button)
        control_layout.addWidget(delete_button)
        control_layout.addStretch() # Mantém os botões juntos à esquerda

        main_layout.addLayout(control_layout)

        # --- 3. Área de Exibição de Mídias ---
        self.media_list_widget = QListWidget()
        self.media_list_widget.setViewMode(QListWidget.IconMode)
        self.media_list_widget.setResizeMode(QListWidget.Adjust)
        self.media_list_widget.setGridSize(QSize(380, 200)) # Tamanho de cada item na grade
        self.media_list_widget.setIconSize(QSize(200, 150)) # Tamanho das miniaturas
        
        main_layout.addWidget(self.media_list_widget)

        # Adicionando alguns itens de teste para visualizar
        self.add_media_item("Video Promo.mp4", "Vídeo", "20/09/2025")
        self.add_media_item("Anuncio Loja.jpg", "Imagem", "15/09/2025")
    
    def add_media_item(self, name, type, date):
        # Cria o nosso widget personalizado
        item_widget = MediaItemWidget(name, type, date)
        
        # Cria um QListWidgetItem que será o "container" do nosso widget
        list_item = QListWidgetItem(self.media_list_widget)
        
        # Define o tamanho do item na lista para acomodar o nosso widget
        list_item.setSizeHint(item_widget.sizeHint())
        
        # Adiciona o widget personalizado ao QListWidgetItem
        self.media_list_widget.addItem(list_item)
        self.media_list_widget.setItemWidget(list_item, item_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
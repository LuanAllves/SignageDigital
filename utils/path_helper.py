import os
import sys
import platform

def get_resource_path(relative_path):
    """Arquivos estáticos (ícones, logos) que vêm com o app"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        # Se estiver em dev, sobe um nível para sair de 'utils'
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_data_path(relative_path=""):
    """Arquivos dinâmicos (DB, mídias) na Home do usuário"""
    if platform.system() == "Linux":
        # Caminho: /home/usuario/.wl_signage
        base_data_path = os.path.expanduser("~/.wl_signage")
    else:
        # No Windows, mantém na pasta do executável por enquanto
        base_data_path = os.path.join(os.path.abspath("."), "data")

    # Garante que a pasta base e a pasta de mídias existam
    media_path = os.path.join(base_data_path, "media_files")
    if not os.path.exists(media_path):
        os.makedirs(media_path, exist_ok=True)

    return os.path.join(base_data_path, relative_path)
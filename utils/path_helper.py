import os
import sys

def get_resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando em dev e no executável """
    try:
        # O PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Se não estiver rodando como executável, usa o caminho do diretório atual
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
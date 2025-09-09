# Sistema de Digital Signage

## Visão Geral

Este é um projeto de um sistema de Digital Signage (Sinalização Digital) que permite gerenciar e exibir uma lista de mídias (imagens e vídeos) em uma tela dedicada. O sistema conta com uma interface de usuário para adicionar, editar, agendar e remover mídias, além de um reprodutor de mídia em tela cheia.

## Funcionalidades

- **Upload de Mídias:** Adicione imagens (`.jpg`, `.png`, `.gif`) e vídeos (`.mp4`, `.avi`, `.mov`).
- **Agendamento:** Agende mídias para serem exibidas em datas e horários específicos.
- **Reprodução:** Exiba a lista de mídias em ordem e em tela cheia em uma tela selecionada.
- **Controle de Áudio:** Opção de silenciar ou ativar o áudio durante a reprodução dos vídeos.
- **Persistência de Dados:** O sistema utiliza um banco de dados SQLite para armazenar as informações das mídias.

## Estrutura do Projeto
O projeto é modular e organizado para facilitar a manutenção e futuras expansões:

├── digital_signage.db       # Banco de dados SQLite
├── gui/                     # Pasta com a interface gráfica
│   ├── main_window.py       # Lógica da janela principal
│   ├── media_display.py     # Lógica da janela de exibição em tela cheia
│   ├── media_edit_dialog.py # Lógica da janela de edição/agendamento
│   └── media_item.py        # Widget personalizado para cada item da lista
├── utils/                   # Utilitários do projeto
│   └── database.py          # Gerenciador de conexão com o banco de dados
├── main.py                  # Ponto de entrada da aplicação
└── README.md                # Descrição do projeto

## Requisitos
Para executar este projeto, você precisará ter o Python instalado, juntamente com as seguintes bibliotecas:

- **PySide6**: Para a interface gráfica.
- **OpenCV (cv2)**: Para a manipulação de vídeos e geração de miniaturas.

Você pode instalá-las usando o `pip`:

```bash
pip install PySide6 opencv-python
```

Como Executar
Clone o repositório ou baixe os arquivos do projeto.

Navegue até a pasta raiz do projeto.

Instale as dependências: 
```bash
pip install -r requirements.txt (se você criar um arquivo requirements.txt).
```

Execute o arquivo main.py:

```bash
python main.py
```

Autores
[LuanAllves]

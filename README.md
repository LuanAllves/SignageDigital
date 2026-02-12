# Sistema de Digital Signage

## Visão Geral

Este é um projeto de um sistema de Digital Signage (Sinalização Digital) que permite gerenciar e exibir uma lista de mídias (imagens e vídeos) em uma tela dedicada. O sistema conta com uma interface de usuário para adicionar, editar, agendar e remover mídias, além de um reprodutor de mídia.

## Funcionalidades

- **Upload de Mídias:** Adicione imagens (`.jpg`, `.png`, `.gif`) e vídeos (`.mp4`, `.avi`, `.mov`).
- **Agendamento:** Agende mídias para serem exibidas em datas e horários específicos.
- **Reprodução:** Exiba a lista de mídias em ordem em uma tela selecionada.
- **Controle de Áudio:** Opção de silenciar ou ativar o áudio durante a reprodução dos vídeos.
- **Persistência de Dados:** O sistema utiliza um banco de dados SQLite para armazenar as informações das mídias.
- **Controle de Resolução** Reproduza em FullScreen ou Formato Original da mídia.
- **Controle de duração** Controle o tempo de exibição das imagens (Tempo de vídeo, depende do tamanho do mesmo!)

## Estrutura do Projeto
O projeto é modular e organizado para facilitar a manutenção e futuras expansões:

```
├── **digital_signage.db**           --->  Banco de dados SQLite
├── **gui/**                         --->  Pasta com a interface gráfica
│   ├── **assets**                   --->  Arquivos 
│   ├── **main_window.py**           --->  Lógica da janela principal
│   ├── **media_display.py**         --->  Lógica da janela de exibição em tela cheia
│   ├── **media_edit_dialog.py**     --->  Lógica da janela de edição/agendamento
│   └── **media_item.py**            --->  Widget personalizado para cada item da lista
├── **utils/**                       --->  Utilitários do projeto
│   └── **database.py**              --->  Gerenciador de conexão com o banco de dados
├── **main.py**                      --->  Ponto de entrada da aplicação
└── **README.md**                    --->  Documentação
```

## Requisitos
Para executar este projeto, você precisará ter o Python instalado, juntamente com as seguintes bibliotecas:

- **PySide6**: Para a interface gráfica.
- **OpenCV (cv2)**: Para a manipulação de vídeos e geração de miniaturas.

Você pode instalá-las usando o `pip`:

```bash
pip install PySide6 opencv-python
```

## Como Executar

1- Clone o repositório ou baixe os arquivos do projeto.

2- Navegue até a pasta raiz do projeto.

3- Instale as dependências: 
```bash
pip install -r requirements.txt
```

4- Execute o arquivo main.py:
```bash
python main.py
```

<hr>

Autor **WLServices - LuanAllves**

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

Que bom que deu certo! A organização do código é o primeiro passo para um projeto robusto e escalável.

Agora, para finalizar e deixar o projeto pronto para ser versionado com o Git e ser facilmente entendido por outras pessoas (ou por você mesmo no futuro), vamos criar o .gitignore e o README.

.gitignore
O arquivo .gitignore diz ao Git quais arquivos e pastas ignorar, ou seja, quais não devem ser enviados para o repositório. Isso é essencial para manter o projeto limpo, seguro e evitar o upload de arquivos temporários, de cache, binários ou de dados sensíveis.

Crie um arquivo chamado .gitignore na raiz do seu projeto e adicione o seguinte conteúdo:

Fragmento do código

# Ignora arquivos de cache do Python e diretórios
__pycache__/
*.pyc

# Ignora o banco de dados local
# O banco de dados SQLite é gerado em tempo de execução e não deve ser versionado
digital_signage.db

# Ignora as miniaturas de vídeo geradas (se houver)
# Se você tiver uma pasta para cache de miniaturas, adicione-a aqui
thumbnails/

# Ignora arquivos específicos de editores de código
.vscode/
.idea/

# Ignora arquivos de sistema
.DS_Store # macOS
Thumbs.db # Windows
README.md
O arquivo README.md é a "capa" do seu projeto. Ele é a primeira coisa que alguém vê ao acessar o repositório e deve explicar o que o projeto faz, como instalá-lo e como usá-lo. Um bom README é claro e direto.

Crie um arquivo chamado README.md na raiz do seu projeto com o seguinte conteúdo. Você pode ajustar as informações conforme a sua necessidade.

Markdown

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

.
├── digital_signage.db       # Banco de dados SQLite
├── old-version/             # Pasta com arquivos de versões anteriores
│   ├── main-v**.py          # Arquivo único de cada versão anterior
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

Instale as dependências: pip install -r requirements.txt (se você criar um arquivo requirements.txt).

Execute o arquivo main.py:

Bash

python main.py
Autores
[LuanAllves]
# Extrator de Frames de Vídeo

Uma ferramenta simples para extrair frames de um arquivo de vídeo e convertê-los em desenhos de linha para auxiliar em animações.

## Instalação e Setup

Siga estes passos no seu terminal, dentro da pasta do projeto.

1.  **Crie o Ambiente Virtual:**
    *   Este comando cria uma pasta `venv` que conterá as dependências isoladas para este projeto.
    ```bash
    python -m venv venv
    ```

2.  **Ative o Ambiente Virtual:**
    *   Você precisa ativar o ambiente em cada nova sessão do terminal.
    ```powershell
    .\venv\Scripts\activate
    ```
    *   Após a ativação, você verá `(venv)` no início da linha do seu terminal.

3.  **Instale as Dependências:**
    *   Este comando instalará o `opencv-python` e o `numpy` nas versões corretas dentro do seu ambiente virtual.
    ```bash
    pip install -r requirements.txt
    ```

## Como Usar o Pipeline

Com o ambiente virtual ativo (`(venv)` aparecendo no terminal), siga os passos:

**Passo 1: Extrair Frames do Vídeo**

*   Execute o extrator:
    ```bash
    python video_frame_extractor.py
    ```
*   Na janela que abrir, selecione o arquivo de vídeo.
*   **Importante:** Forneça o caminho para o seu `ffmpeg.exe` se ele não estiver no PATH do sistema.
*   Os frames do vídeo serão salvos na pasta `output`.

**Passo 2: Converter Frames em Desenho de Linha**

*   Depois que os frames estiverem na pasta `output`, execute o conversor:
    ```bash
    python silhouette_converter.py
    ```
*   O script irá processar essas imagens e salvará os desenhos de contorno em uma nova pasta chamada `output_linhas`.

---

O projeto agora está configurado com um pipeline claro: extrair e depois converter, pronto para a próxima etapa da sua animação.

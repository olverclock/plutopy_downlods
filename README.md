## PlutoTV Downloader Profissional

**PlutoTV Downloader Profissional** é uma ferramenta avançada desenvolvida em Python com interface gráfica para baixar episódios e transmissões diretamente da plataforma Pluto TV.

### 🖥️ Interface Moderna e Intuitiva

A interface do aplicativo foi projetada com um tema escuro moderno, oferecendo uma experiência clara e agradável para o usuário:

- Campo para colar a URL da **página da série**.
- Campo separado para a **URL direta do stream (episódio)**.
- Botões funcionais para:
  - **Carregar da URL** (extrai episódios automaticamente da página da série).
  - **Atualizar Links** (recarrega os links dos episódios).
  - **Salvar Links** (exporta lista de episódios).
  - **Limpar Lista** (remove todos os links carregados).
  - **Baixar da URL Direta** (inicia download direto do stream inserido).
- Lista de episódios (com título e link) carregada dinamicamente.
- Opção de **selecionar método de download**, com suporte a:
  - `ffmpeg`
  - `yt-dlp`
  - `streamlink`
- Botão para **baixar episódios em fila**.

### ⚙️ Funcionalidades Principais

- 🔗 **Leitura automática de URLs** da página de séries da Pluto TV.
- 📺 **Suporte a múltiplos episódios** com detecção automática.
- 🎬 **Download com streamlink, yt-dlp ou ffmpeg** diretamente do servidor da Pluto TV.
- 📂 **Sistema de fila** para baixar múltiplos episódios automaticamente.
- 💾 **Salvamento de listas** para reutilização futura.
- 🔄 **Atualização rápida dos links** antes do download.
- 🌐 **Compatível com Windows** (recomendado para Windows 10+).

### 🔧 Requisitos

- Python 3.8+
- Dependências:
  - `requests`
  - `PySide6`
  - `beautifulsoup4`
  - `streamlink`, `ffmpeg`, `yt-dlp` (opcional, instalados no sistema)

### 📦 Instalação

```bash
pip install -r requirements.txt
```

Instale também as ferramentas externas desejadas (ex: `streamlink`, `yt-dlp`, `ffmpeg`) disponíveis via Chocolatey ou outros gerenciadores.

### 🚀 Como usar

```bash
python pluto_downloads8.py
```

Cole a URL da página da série ou de um stream e inicie os downloads com facilidade.

### ⚠️ Aviso Legal

> Este projeto é apenas para fins educacionais. Certifique-se de ter os direitos para baixar qualquer conteúdo da Pluto TV. Respeite os termos de uso da plataforma.

"""
PlutoTV Downloader Profissional

PlutoTV Downloader Profissional é uma ferramenta avançada desenvolvida em Python com interface gráfica
para baixar episódios e transmissões diretamente da plataforma Pluto TV.

Interface Moderna e Intuitiva
-----------------------------
- Campo para colar a URL da página da série na Pluto TV
- Campo para colar a URL direta do episódio (stream)
- Botões funcionais para:
  * Carregar da URL (extrai episódios automaticamente da página da série)
  * Atualizar Links (recarrega os links dos episódios)
  * Salvar Links (exporta lista de episódios)
  * Limpar Lista (remove todos os links carregados)
  * Baixar da URL Direta (download direto do stream inserido)
- Lista dinâmica de episódios
- Opção para selecionar método de download (ex: streamlink)
- Botão para baixar episódios em fila

Funcionalidades Principais
--------------------------
- Leitura automática de URLs da página de séries da Pluto TV
- Suporte a múltiplos episódios com detecção automática
- Download com streamlink diretamente do servidor da Pluto TV
- Sistema de fila para baixar múltiplos episódios automaticamente
- Salvamento de listas para reutilização futura
- Atualização rápida dos links antes do download
- Compatível com Windows (interface otimizada para esse sistema)

Requisitos
----------
- Python 3.8+
- Dependências: requests, tkinter, streamlink
- Sistema operacional: Windows

Instalação
----------
1. Instale o Python: https://www.python.org/downloads/
2. Instale o streamlink:
   pip install streamlink
3. Execute o script:
   python pluto_downloads8.py

Aviso Legal
-----------
Este projeto é fornecido apenas para fins educacionais e uso pessoal.
Certifique-se de ter os direitos para baixar qualquer conteúdo da Pluto TV.
Respeite os termos de uso da plataforma.
"""

import sys
import os
import subprocess
import requests
from bs4 import BeautifulSoup
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QComboBox, QProgressBar,
    QMessageBox, QHBoxLayout, QLineEdit, QStyleFactory, QCheckBox
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QThread, Signal, QSize, QSettings
from urllib.parse import urljoin
import re

METODOS_DOWNLOAD = {
    "ffmpeg": lambda url, saida: ["ffmpeg", "-i", url, "-c", "copy", "-bsf:a", "aac_adtstoasc", "-movflags", "faststart", saida],
    "yt-dlp": lambda url, saida: ["yt-dlp", "--fixup", "never", "-o", saida, url],
    "streamlink": lambda url, saida: ["streamlink", "--hls-live-restart", url, "best", "-o", saida]
}

class DownloaderThread(QThread):
    progresso = Signal(str)
    finalizado = Signal(str)

    def __init__(self, fila, metodo):
        super().__init__()
        self.fila = fila
        self.metodo = metodo

    def run(self):
        for item in self.fila:
            titulo = item['titulo']
            url = item['url']
            caminho = item['caminho']

            self.progresso.emit(f"Baixando: {titulo}")
            comando = METODOS_DOWNLOAD[self.metodo](url, caminho)
            try:
                subprocess.run(comando, check=True)
                self.finalizado.emit(f"Concluído: {titulo}")
            except subprocess.CalledProcessError:
                self.finalizado.emit(f"Erro ao baixar: {titulo}")

class PlutoTVDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlutoTV Downloader Profissional")
        self.setMinimumSize(1000, 700)

        QApplication.setStyle(QStyleFactory.create("Fusion"))

        self.settings = QSettings("PlutoTVDownloader", "Config")

        self.layout = QVBoxLayout(self)

        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Cole a URL da página da série na Pluto TV")
        self.input_url.setText(self.settings.value("ultima_url", ""))

        self.btn_carregar_url = QPushButton("Carregar da URL")
        self.btn_atualizar = QPushButton("Atualizar Links")
        self.btn_salvar_links = QPushButton("Salvar Links")
        self.btn_limpar_lista = QPushButton("Limpar Lista")

        # Novo campo e botão para baixar da URL direta
        self.input_url_direta = QLineEdit()
        self.input_url_direta.setPlaceholderText("Cole a URL direta do episódio (stream)")
        self.btn_baixar_url_direta = QPushButton("Baixar da URL Direta")
        self.btn_baixar_url_direta.clicked.connect(self.baixar_url_direta)

        self.label_status = QLabel("Cole a URL e clique em carregar.")
        self.lista = QListWidget()
        self.btn_download_todos = QPushButton("Baixar Selecionados (Fila)")
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(METODOS_DOWNLOAD.keys())

        self.progress_bar = QProgressBar()

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.input_url)
        top_bar.addWidget(self.btn_carregar_url)
        top_bar.addWidget(self.btn_atualizar)
        top_bar.addWidget(self.btn_salvar_links)
        top_bar.addWidget(self.btn_limpar_lista)

        # Novo layout para URL direta
        url_direta_layout = QHBoxLayout()
        url_direta_layout.addWidget(self.input_url_direta)
        url_direta_layout.addWidget(self.btn_baixar_url_direta)

        self.layout.addLayout(top_bar)
        self.layout.addLayout(url_direta_layout)
        self.layout.addWidget(self.label_status)
        self.layout.addWidget(self.lista)
        self.layout.addWidget(QLabel("Método de Download:"))
        self.layout.addWidget(self.combo_metodo)
        self.layout.addWidget(self.btn_download_todos)
        self.layout.addWidget(self.progress_bar)

        self.btn_carregar_url.clicked.connect(self.carregar_episodios_por_url)
        self.btn_download_todos.clicked.connect(self.baixar_selecionados)
        self.btn_atualizar.clicked.connect(self.atualizar_links)
        self.btn_salvar_links.clicked.connect(self.salvar_links_txt)
        self.btn_limpar_lista.clicked.connect(self.limpar_lista)

        self.episodios = []

    def carregar_episodios_por_url(self):
        url = self.input_url.text().strip()
        if not url:
            QMessageBox.warning(self, "Aviso", "Cole uma URL válida da Pluto TV")
            return

        self.settings.setValue("ultima_url", url)

        try:
            resposta = requests.get(url)
            conteudo = resposta.text
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao acessar a URL: {e}")
            return

        soup = BeautifulSoup(conteudo, 'html.parser')
        episodios = []
        self.lista.clear()

        for card in soup.find_all('a', href=True):
            link = card['href'].strip()
            texto = card.get_text(strip=True).lower()

            ignorar = ['assista agora', 'tv ao vivo', 'sob demanda', 'suporte', 'termos', 'privacidade', 'procurar', 'go to pluto']
            if any(p in texto for p in ignorar):
                continue

            if not re.search(r'(temporada|episodio|season|ep)', link, re.IGNORECASE) and not re.search(r'(t\d+e\d+)', link, re.IGNORECASE):
                continue

            link = urljoin(url, link)
            titulo = card.get('title') or card.text.strip()
            if not titulo or len(titulo) < 3:
                continue

            descricao = card.find('p').text.strip() if card.find('p') else ''
            img_tag = card.find('img')
            thumbnail = img_tag['src'] if img_tag and img_tag.has_attr('src') else ''
            temporada, episodio = self.extrair_temporada_ep(link)

            nome_formatado = f"Temporada{temporada:02d}_Episodio{episodio:02d}_{titulo.replace(' ', '_')}.mp4"

            item = QListWidgetItem()
            item.setSizeHint(QSize(300, 100))

            widget = QWidget()
            hbox = QHBoxLayout(widget)
            hbox.setContentsMargins(5, 5, 5, 5)

            checkbox = QCheckBox()
            label_img = QLabel()
            if thumbnail:
                try:
                    img_data = requests.get(thumbnail).content
                    pixmap = QPixmap()
                    pixmap.loadFromData(img_data)
                    pixmap = pixmap.scaledToWidth(100)
                    label_img.setPixmap(pixmap)
                except:
                    pass

            label_txt = QLabel(f"<b>{titulo}</b><br>{descricao}<br><span style='color:gray; font-size:9pt'>{link}</span>")
            label_txt.setTextFormat(Qt.RichText)

            btn_baixar = QPushButton("Baixar")
            btn_baixar.clicked.connect(lambda _, ep={'titulo': titulo, 'descricao': descricao, 'url': link, 'thumbnail': thumbnail, 'temporada': temporada, 'episodio': episodio, 'arquivo': nome_formatado}: self.baixar_individual(ep))

            hbox.addWidget(checkbox)
            hbox.addWidget(label_img)
            hbox.addWidget(label_txt, 1)
            hbox.addWidget(btn_baixar)

            self.lista.addItem(item)
            self.lista.setItemWidget(item, widget)
            episodios.append({
                'titulo': titulo,
                'descricao': descricao,
                'url': link,
                'thumbnail': thumbnail,
                'temporada': temporada,
                'episodio': episodio,
                'arquivo': nome_formatado,
                'checkbox': checkbox
            })

        self.episodios = episodios
        self.label_status.setText(f"{len(episodios)} episódios encontrados.")

    def extrair_temporada_ep(self, texto):
        t, e = 1, 1
        match = re.search(r'T(\d+)[^\d]?E(\d+)', texto, re.IGNORECASE)
        if match:
            t = int(match.group(1))
            e = int(match.group(2))
        else:
            ep_match = re.findall(r'(temporada|season)[^\d]?(\d+)', texto, re.IGNORECASE)
            if ep_match:
                t = int(ep_match[0][1])
            epn_match = re.findall(r'(episodio|ep)[^\d]?(\d+)', texto, re.IGNORECASE)
            if epn_match:
                e = int(epn_match[0][1])
        return t, e

    def baixar_individual(self, ep):
        pasta = QFileDialog.getExistingDirectory(self, "Escolha a pasta para salvar")
        if not pasta:
            return

        caminho = os.path.join(pasta, ep['arquivo'])
        metodo = self.combo_metodo.currentText()

        self.thread = DownloaderThread([{
            'titulo': ep['titulo'],
            'url': ep['url'],
            'caminho': caminho
        }], metodo)
        self.thread.progresso.connect(self.atualizar_status)
        self.thread.finalizado.connect(self.atualizar_status)
        self.thread.start()

    def baixar_selecionados(self):
        pasta = QFileDialog.getExistingDirectory(self, "Escolha a pasta para salvar")
        if not pasta:
            return

        fila = []
        for ep in self.episodios:
            if ep['checkbox'].isChecked():
                caminho_completo = os.path.join(pasta, ep['arquivo'])
                fila.append({
                    'titulo': ep['titulo'],
                    'url': ep['url'],
                    'caminho': caminho_completo
                })

        if not fila:
            QMessageBox.information(self, "Nada selecionado", "Selecione pelo menos um episódio para baixar.")
            return

        metodo = self.combo_metodo.currentText()
        self.thread = DownloaderThread(fila, metodo)
        self.thread.progresso.connect(self.atualizar_status)
        self.thread.finalizado.connect(self.atualizar_status)
        self.thread.start()

    def atualizar_status(self, msg):
        self.label_status.setText(msg)

    def atualizar_links(self):
        self.carregar_episodios_por_url()

    def salvar_links_txt(self):
        if not self.episodios:
            QMessageBox.information(self, "Nenhum episódio", "Nenhum episódio carregado para salvar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar lista de links", "episodios.txt", "Text Files (*.txt)")
        if not caminho:
            return

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                for ep in self.episodios:
                    f.write(f"{ep['titulo']}\n{ep['descricao']}\n{ep['url']}\n\n")
            QMessageBox.information(self, "Salvo", "Links salvos com sucesso.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")

    def limpar_lista(self):
        self.episodios = []
        self.lista.clear()
        self.label_status.setText("Lista limpa.")

    def baixar_url_direta(self):
        url = self.input_url_direta.text().strip()
        if not url:
            QMessageBox.warning(self, "Aviso", "Cole uma URL direta válida para download.")
            return

        nome_arquivo, _ = QFileDialog.getSaveFileName(self, "Salvar Episódio", "episodio.mp4", "Vídeo (*.mp4)")
        if not nome_arquivo:
            return

        metodo = self.combo_metodo.currentText()

        self.thread = DownloaderThread([{
            'titulo': os.path.basename(nome_arquivo),
            'url': url,
            'caminho': nome_arquivo
        }], metodo)
        self.thread.progresso.connect(self.atualizar_status)
        self.thread.finalizado.connect(self.atualizar_status)
        self.thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlutoTVDownloader()
    window.show()
    sys.exit(app.exec())

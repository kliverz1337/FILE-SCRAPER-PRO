import qtawesome as qta
from pathlib import Path

from PySide6.QtCore import Qt, QPoint, QThread, Signal
from PySide6.QtGui import QColor, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QProgressBar, QFileDialog, QFrame, QScrollArea,
    QGraphicsDropShadowEffect, QDialog, QTabWidget
)

from core.config import load_services_config
from core.scraper import ScraperWorker
from .dialogs import ConfirmDialog, CustomMessageBox
from .settings_dialog import SettingsDialog

class DropZone(QTextEdit):
    """Widget QTextEdit kustom yang menerima drop folder."""
    folder_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and len(event.mimeData().urls()) == 1:
            url = event.mimeData().urls()[0]
            if url.isLocalFile() and Path(url.toLocalFile()).is_dir():
                event.acceptProposedAction()
                self.setStyleSheet("border: 2px solid #1abc9c; background-color: #40556a;")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        url = event.mimeData().urls()[0]
        folder_path = url.toLocalFile()
        self.folder_dropped.emit(folder_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("File Scraper Pro")
        self.resize(850, 600)
        self.setMinimumSize(700, 500)
        
        self.old_pos = None
        self.folder_path = None
        self.services_config = load_services_config()
        self.cards = {}
        self.scraper_thread = None
        self.scraper_worker = None

        self._setup_ui()
        self._apply_stylesheet()
        self.center_on_screen()

    def _setup_ui(self):
        self.container = QFrame()
        self.container.setObjectName("container")
        self.setCentralWidget(self.container)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.title_bar = self._create_custom_title_bar()
        container_layout.addWidget(self.title_bar)

        # --- Tab Widget Setup ---
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        container_layout.addWidget(self.tabs)

        # --- Scraper Tab ---
        scraper_tab = QWidget()
        scraper_layout = QHBoxLayout(scraper_tab)
        
        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)

        scraper_layout.addWidget(left_panel, 2)
        scraper_layout.addWidget(separator)
        scraper_layout.addWidget(right_panel, 1)

        # --- About Tab ---
        about_tab = self._create_about_tab()

        self.tabs.addTab(scraper_tab, "Scraper")
        self.tabs.addTab(about_tab, "About")

    def _create_left_panel(self):
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.folder_label = QLabel("Pilih folder untuk scrape .txt")
        
        self.log_area = DropZone()
        self.log_area.setObjectName("logAreaDropZone")
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Seret & lepas folder berisi file .txt ke sini,\natau klik 'Mulai Scraping' untuk memilih folder.")
        self.log_area.folder_dropped.connect(self._set_folder_path)

        self.progress_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.start_button = QPushButton(" Mulai Scraping")
        self.start_button.setIcon(qta.icon('fa5s.play-circle', color='#2c3e50'))
        self.start_button.clicked.connect(self.start_scraping)
        
        self.settings_button = QPushButton(" Pengaturan")
        self.settings_button.setIcon(qta.icon('fa5s.cog', color='#2c3e50'))
        self.settings_button.clicked.connect(self.open_settings)
        
        for btn in [self.start_button, self.settings_button]:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 80))
            btn.setGraphicsEffect(shadow)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.settings_button)

        left_layout.addWidget(self.folder_label)
        left_layout.addWidget(self.log_area)
        left_layout.addWidget(self.progress_label)
        left_layout.addWidget(self.progress_bar)
        left_layout.addLayout(button_layout)
        
        return left_panel

    def _create_right_panel(self):
        right_panel = QWidget()
        self.right_layout = QVBoxLayout(right_panel)
        self._create_result_display()
        return right_panel

    def _create_custom_title_bar(self):
        title_bar = QWidget()
        title_bar.setObjectName("title_bar")
        title_bar.setFixedHeight(40)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(15, 0, 5, 0)
        
        app_icon = qta.icon('fa5s.file-code', color='#1abc9c')
        icon_label = QLabel()
        icon_label.setPixmap(app_icon.pixmap(18, 18))
        
        title = QLabel(self.windowTitle())
        title.setObjectName("windowTitle")
        
        self.minimize_button = QPushButton(qta.icon('fa5s.window-minimize', color='#ecf0f1'), "")
        self.maximize_button = QPushButton(qta.icon('fa5s.window-maximize', color='#ecf0f1'), "")
        self.close_button = QPushButton(qta.icon('fa5s.times', color='#ecf0f1'), "")
        
        self.minimize_button.setObjectName("minimizeButton")
        self.maximize_button.setObjectName("maximizeButton")
        self.close_button.setObjectName("closeButton")

        for btn in [self.minimize_button, self.maximize_button, self.close_button]:
            btn.setFixedSize(35, 35)
        
        self.minimize_button.clicked.connect(self.showMinimized)
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)
        self.close_button.clicked.connect(self.close)
        
        title_bar_layout.addWidget(icon_label)
        title_bar_layout.addSpacing(10)
        title_bar_layout.addWidget(title)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(self.minimize_button)
        title_bar_layout.addWidget(self.maximize_button)
        title_bar_layout.addWidget(self.close_button)
        
        return title_bar

    def _create_result_display(self):
        while self.right_layout.count():
            child = self.right_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.cards.clear()
        self.services_config = load_services_config()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("cardScrollArea")
        
        card_container = QWidget()
        self.card_layout = QVBoxLayout(card_container)
        self.card_layout.setSpacing(10)
        self.card_layout.setContentsMargins(10, 10, 10, 10)

        for service in self.services_config:
            name = service["name"]
            card = QFrame()
            card.setObjectName("serviceCard")
            card.setProperty("found", "false")
            card_layout = QHBoxLayout(card)

            icon_name = service.get('icon', 'fa5s.question-circle')
            icon_label = QLabel()
            icon_label.setObjectName("cardIconLabel")
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setPixmap(qta.icon(icon_name, color='#ecf0f1').pixmap(18, 18))

            name_label = QLabel(name)
            name_label.setObjectName("cardNameLabel")

            count_label = QLabel("0")
            count_label.setObjectName("cardCountLabel")

            card_layout.addWidget(icon_label, 0)
            card_layout.addWidget(name_label, 1)
            card_layout.addWidget(count_label, 0, Qt.AlignRight)

            self.card_layout.addWidget(card)
            self.cards[name] = {
                "widget": card,
                "count_label": count_label,
                "icon_label": icon_label,
                "icon_name": icon_name
            }

        self.card_layout.addStretch()
        scroll_area.setWidget(card_container)
        self.right_layout.addWidget(scroll_area)

    def _set_folder_path(self, path):
        self.folder_path = Path(path)
        self.folder_label.setText(f"Folder: {self.folder_path.name}")
        self.log_area.append(f'<font color="#f1fa8c">Folder dipilih: {path}</font>')

    def start_scraping(self):
        if not self.folder_path:
            path = QFileDialog.getExistingDirectory(self, "Pilih Folder")
            if not path: return
            self._set_folder_path(path)

        self.log_area.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.set_controls_enabled(False)

        self.scraper_thread = QThread()
        self.scraper_worker = ScraperWorker(self.folder_path, self.services_config)
        self.scraper_worker.moveToThread(self.scraper_thread)

        self.scraper_thread.started.connect(self.scraper_worker.run)
        self.scraper_worker.finished.connect(self.on_scraping_finished)
        self.scraper_worker.error.connect(self.on_scraping_error)
        self.scraper_worker.log_message.connect(self.update_log)
        self.scraper_worker.progress_updated.connect(self.update_progress)
        self.scraper_worker.count_updated.connect(self.update_count)
        
        self.scraper_worker.finished.connect(self.scraper_thread.quit)
        self.scraper_worker.finished.connect(self.scraper_worker.deleteLater)
        self.scraper_thread.finished.connect(self.scraper_thread.deleteLater)
        
        self.scraper_thread.start()

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.settings_saved.connect(self._create_result_display)
        dialog.center_on_screen()
        dialog.exec()

    def set_controls_enabled(self, enabled):
        self.start_button.setEnabled(enabled)
        self.settings_button.setEnabled(enabled)

    def update_progress(self, value, total):
        self.progress_bar.setValue(int((value / total) * 100))
        self.progress_label.setText(f"Memproses file {value} dari {total}...")

    def update_count(self, name, count):
        if name in self.cards:
            card_data = self.cards[name]
            card_data["count_label"].setText(str(count))
            if count > 0 and card_data["widget"].property("found") == "false":
                card_data["widget"].setProperty("found", "true")
                
                # Update icon color
                icon_label = card_data["icon_label"]
                icon_name = card_data["icon_name"]
                icon_label.setPixmap(qta.icon(icon_name, color='#2c3e50').pixmap(18, 18))

                # Refresh style
                card_data["widget"].style().unpolish(card_data["widget"])
                card_data["widget"].style().polish(card_data["widget"])

    def update_log(self, message, level):
        color_map = {"INFO": "#8be9fd", "SUCCESS": "#50fa7b", "ERROR": "#ff5555", "ACTION": "#f1fa8c"}
        self.log_area.append(f'<font color="{color_map.get(level, "#f8f8f2")}">{message}</font>')

    def on_scraping_finished(self, message):
        dialog = CustomMessageBox(self, "Selesai", message, 'fa5s.check-circle', '#1abc9c')
        dialog.center_on_screen()
        dialog.exec()
        self.set_controls_enabled(True)
        self.progress_label.setText("Selesai!")

    def on_scraping_error(self, message):
        dialog = CustomMessageBox(self, "Error", message, 'fa5s.times-circle', '#e74c3c')
        dialog.center_on_screen()
        dialog.exec()
        self.set_controls_enabled(True)
        self.progress_label.setText("Gagal!")

    def _apply_stylesheet(self):
        try:
            with open("assets/style.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet (assets/style.qss) tidak ditemukan.")

    def center_on_screen(self):
        if self.screen():
            screen_geometry = self.screen().geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if self.title_bar.underMouse() and event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def closeEvent(self, event):
        dialog = ConfirmDialog(
            self, 'Konfirmasi Keluar',
            "Apakah Anda yakin ingin keluar dari aplikasi?",
            'fa5s.question-circle', '#f1c40f'
        )
        dialog.center_on_screen()
        # Pindahkan dialog sedikit ke atas sebelum menampilkannya
        dialog.move(dialog.x(), dialog.y() - 50)
        if dialog.exec() == QDialog.Accepted:
            event.accept()
        else:
            event.ignore()

    def _create_about_tab(self):
        about_widget = QWidget()
        layout = QVBoxLayout(about_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setAlignment(Qt.AlignTop)

        # --- Project Info ---
        project_title = QLabel("About File Scraper Pro")
        project_title.setObjectName("aboutTitle")

        project_desc = QLabel(
            "Proyek ini dibuat sebagai alat bantu untuk mempercepat proses penyortiran data "
            "dari file log atau hasil pemindaian teks. Tujuannya adalah untuk mengotomatiskan "
            "tugas manual yang berulang dalam mengkategorikan data berdasarkan kriteria "
            "tertentu (dalam hal ini, port layanan)."
        )
        project_desc.setWordWrap(True)
        project_desc.setObjectName("aboutText")

        # --- Author Info ---
        author_title = QLabel("Author")
        author_title.setObjectName("aboutTitle")
        author_title.setStyleSheet("margin-top: 20px;")

        author_name = QLabel("Dibuat dan dikelola oleh <b>kliverz</b>.")
        author_name.setObjectName("aboutText")

        # Links - make them clickable
        github_link = QLabel('<a href="https://github.com/kliverz1337/FILE-SCRAPER-PRO" style="color: #1abc9c; text-decoration: none;">GitHub: @kliverz1337</a>')
        github_link.setOpenExternalLinks(True)

        telegram_link = QLabel('<a href="https://t.me/kliverz1337" style="color: #1abc9c; text-decoration: none;">Telegram: @kliverz1337</a>')
        telegram_link.setOpenExternalLinks(True)

        email_link = QLabel('<a href="mailto:kliverz1337@gmail.com" style="color: #1abc9c; text-decoration: none;">Email: kliverz1337@gmail.com</a>')
        email_link.setOpenExternalLinks(True)

        layout.addWidget(project_title)
        layout.addWidget(project_desc)
        layout.addSpacing(20)
        layout.addWidget(author_title)
        layout.addWidget(author_name)
        layout.addWidget(github_link)
        layout.addWidget(telegram_link)
        layout.addWidget(email_link)
        
        return about_widget
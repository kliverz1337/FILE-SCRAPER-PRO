import qtawesome as qta
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)

class BaseDialog(QDialog):
    """
    Kelas dasar untuk semua dialog kustom. Menangani pembuatan frame jendela
    tanpa bingkai (frameless), title bar, dan pemusatan pada parent.
    """
    def __init__(self, parent, title, icon_name, icon_color):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(350)
        self.old_pos = None

        # Kontainer utama dengan border dan radius
        self.container = QFrame(self)
        self.container.setObjectName("customMessageBox")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.container)

        # Layout untuk konten di dalam kontainer
        self.content_layout = QVBoxLayout(self.container)
        self.content_layout.setContentsMargins(1, 1, 1, 1)
        self.content_layout.setSpacing(0)

        # Title Bar
        self.title_bar = self._create_title_bar(title, icon_name, icon_color)
        self.content_layout.addWidget(self.title_bar)

    def _create_title_bar(self, title, icon_name, icon_color):
        title_bar = QWidget()
        title_bar.setObjectName("messageBoxTitleBar")
        title_bar.setFixedHeight(35)
        
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 0, 10, 0)
        
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon(icon_name, color=icon_color).pixmap(18, 18))
        
        title_label = QLabel(title)
        title_label.setObjectName("messageBoxTitleLabel")
        
        title_bar_layout.addWidget(icon_label)
        title_bar_layout.addSpacing(10)
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        
        return title_bar

    def center_on_screen(self):
        if self.parent():
            screen = self.parent().screen()
        else:
            screen = self.screen()
        
        if screen:
            screen_geometry = screen.geometry()
            x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
            y = screen_geometry.y() + (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

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

    def exec(self):
        return super().exec()


class CustomMessageBox(BaseDialog):
    """Dialog pesan informasi atau error kustom."""
    def __init__(self, parent, title, message, icon_name='fa5s.info-circle', icon_color='#1abc9c'):
        super().__init__(parent, title, icon_name, icon_color)

        # Area Pesan
        message_frame = QFrame()
        message_layout = QVBoxLayout(message_frame)
        message_layout.setContentsMargins(20, 20, 20, 20)
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setObjectName("messageBoxTextLabel")
        message_layout.addWidget(message_label)
        
        # Area Tombol
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 20, 20)
        button_layout.addStretch()
        ok_button = QPushButton("OK")
        ok_button.setFixedWidth(100)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        self.content_layout.addWidget(message_frame)
        self.content_layout.addWidget(button_frame)


class ConfirmDialog(BaseDialog):
    """Dialog konfirmasi Ya/Tidak kustom."""
    def __init__(self, parent, title, message, icon_name='fa5s.question-circle', icon_color='#f1c40f'):
        super().__init__(parent, title, icon_name, icon_color)

        # Area Pesan
        message_frame = QFrame()
        message_layout = QVBoxLayout(message_frame)
        message_layout.setContentsMargins(20, 20, 20, 20)
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setObjectName("messageBoxTextLabel")
        message_layout.addWidget(message_label)

        # Area Tombol
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(20, 0, 20, 20)
        
        no_button = QPushButton("Tidak")
        no_button.setFixedWidth(100)
        no_button.clicked.connect(self.reject)
        
        yes_button = QPushButton("Ya")
        yes_button.setObjectName("confirmYesButton")
        yes_button.setFixedWidth(100)
        yes_button.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(no_button)
        button_layout.addSpacing(10)
        button_layout.addWidget(yes_button)
        button_layout.addStretch()
        
        self.content_layout.addWidget(message_frame)
        self.content_layout.addWidget(button_frame)
from functools import partial
import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QFrame, QHeaderView, QTableWidget, QTableWidgetItem, QAbstractItemView
)

from .dialogs import BaseDialog, CustomMessageBox
from core.config import load_services_config, save_services_config

from PySide6.QtWidgets import QScrollArea


class SettingsDialog(BaseDialog):
    """Dialog untuk mengelola daftar layanan (menambah, menghapus, menyimpan)."""
    settings_saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent, "Pengaturan Layanan", 'fa5s.cog', '#1abc9c')
        self.setMinimumSize(500, 500)
        
        self.setObjectName("settingsDialog")
        self.container.setObjectName("settingsDialogContainer")
        self.title_bar.setObjectName("settingsTitleBar")
        
        self.services = load_services_config()

        content_widget = QFrame()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 15)
        content_layout.setSpacing(15)
        self.content_layout.addWidget(content_widget)
        
        self._create_service_list(content_layout)
        self._create_add_form(content_layout)
        
        content_layout.addStretch(1)
        
        save_button = QPushButton("Simpan Tutup")
        save_button.clicked.connect(self._save_and_close)
        
        button_hbox = QHBoxLayout()
        button_hbox.addStretch()
        button_hbox.addWidget(save_button)
        button_hbox.addStretch()
        content_layout.addLayout(button_hbox)

        close_button = QPushButton(qta.icon('fa5s.times', color='#ecf0f1'), "")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(35, 35)
        close_button.clicked.connect(self.reject)
        self.title_bar.layout().addWidget(close_button)

    def _create_service_list(self, layout):
        scroll_area = QScrollArea()
        scroll_area.setObjectName("settingsScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        list_container = QWidget()
        self.service_list_layout = QVBoxLayout(list_container)
        self.service_list_layout.setContentsMargins(5, 5, 5, 5)
        self.service_list_layout.setSpacing(8)
        
        scroll_area.setWidget(list_container)
        
        layout.addWidget(scroll_area)
        self._populate_service_list()

    def _populate_service_list(self):
        while self.service_list_layout.count():
            child = self.service_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        for service in self.services:
            item_widget = self._create_service_item_widget(service)
            self.service_list_layout.addWidget(item_widget)
            
        self.service_list_layout.addStretch(1)

    def _create_service_item_widget(self, service):
        item_frame = QFrame()
        item_frame.setObjectName("serviceListItem")
        item_layout = QHBoxLayout(item_frame)
        item_layout.setContentsMargins(10, 5, 10, 5)

        name_label = QLabel(f"<b>{service['name']}</b> &nbsp; <font color='#bdc3c7'>{', '.join(service['ports'])}</font>")
        
        delete_button = QPushButton("Hapus")
        delete_button.setObjectName("deleteButton")
        delete_button.setIcon(qta.icon('fa5s.trash-alt'))
        delete_button.clicked.connect(partial(self._remove_service, service['name']))

        item_layout.addWidget(name_label)
        item_layout.addStretch()
        item_layout.addWidget(delete_button)
        
        return item_frame

    def _create_add_form(self, layout):
        add_frame = QFrame()
        add_frame.setObjectName("settingsGroupFrame")
        add_layout = QHBoxLayout(add_frame)
        add_layout.setSpacing(10)

        add_layout.addWidget(QLabel("<b>Tambah Baru:</b>"))
        
        self.name_entry = QLineEdit()
        self.name_entry.setPlaceholderText("Nama Layanan")
        add_layout.addWidget(self.name_entry, 1)
        
        self.ports_entry = QLineEdit()
        self.ports_entry.setPlaceholderText("Port, pisahkan koma")
        add_layout.addWidget(self.ports_entry, 1)

        add_button = QPushButton("Tambah")
        add_button.setIcon(qta.icon('fa5s.plus-circle'))
        add_button.clicked.connect(self._add_service)
        add_layout.addWidget(add_button, 0)
        
        layout.addWidget(add_frame)

    def _add_service(self):
        name = self.name_entry.text().strip()
        ports_str = self.ports_entry.text().strip()

        if not name or not ports_str:
            dialog = CustomMessageBox(self, "Input Tidak Lengkap", "Nama layanan dan port tidak boleh kosong.", 'fa5s.exclamation-triangle', '#f1c40f')
            dialog.center_on_screen()
            dialog.exec()
            return

        if any(s['name'].lower() == name.lower() for s in self.services):
            dialog = CustomMessageBox(self, "Nama Duplikat", f"Layanan dengan nama '{name}' sudah ada.", 'fa5s.exclamation-triangle', '#f1c40f')
            dialog.center_on_screen()
            dialog.exec()
            return

        try:
            ports_list = [p.strip() for p in ports_str.split(',') if p.strip().isdigit()]
            if not ports_list: raise ValueError("Tidak ada port valid yang dimasukkan.")
        except ValueError as e:
            dialog = CustomMessageBox(self, "Input Port Tidak Valid", f"Port harus berupa angka yang dipisahkan koma.\nDetail: {e}", 'fa5s.exclamation-triangle', '#f1c40f')
            dialog.center_on_screen()
            dialog.exec()
            return
        
        unique_ports = sorted(list(set(ports_list)))
        # Gunakan nama layanan untuk ikon default jika memungkinkan
        icon_name = f"fa5s.{name.lower()}" if ' ' not in name else 'fa5s.question-circle'
        new_service = {"name": name, "ports": unique_ports, "file": f"{name}.txt", "icon": icon_name}
        
        self.services.append(new_service)
        self._populate_service_list()
        self.name_entry.clear()
        self.ports_entry.clear()

    def _remove_service(self, service_name_to_remove):
        self.services = [s for s in self.services if s.get('name') != service_name_to_remove]
        self._populate_service_list()

    def _save_and_close(self):
        save_services_config(self.services)
        self.settings_saved.emit()
        self.accept()
"""Configure pairing with a remote (self-hosted) Storymaster sync server."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from storymaster.sync_client.client import SyncClient, SyncError
from storymaster.sync_client.config import load_config


class RemoteSyncDialog(QDialog):
    """Pair this desktop with a remote sync server using a one-shot token."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Remote Sync")
        self.setMinimumWidth(440)
        self._build_ui()
        self._load_existing()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        intro = QLabel(
            "Pair this desktop with a self-hosted sync server. Get the server URL "
            "and a one-time pairing token from the server admin (use "
            "<code>/api/pair/qr-data</code> on the server).",
            self,
        )
        intro.setWordWrap(True)
        intro.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(intro)

        form = QFormLayout()
        self.server_url_input = QLineEdit(self)
        self.server_url_input.setPlaceholderText("http://10.0.0.5:8765")
        form.addRow("Server URL:", self.server_url_input)

        self.device_name_input = QLineEdit(self)
        form.addRow("Device name:", self.device_name_input)

        self.pairing_token_input = QLineEdit(self)
        self.pairing_token_input.setPlaceholderText("Paste token from server")
        form.addRow("Pairing token:", self.pairing_token_input)

        self.status_label = QLabel(self)
        form.addRow("Status:", self.status_label)

        layout.addLayout(form)

        button_row = QHBoxLayout()
        self.pair_button = QPushButton("Pair")
        self.pair_button.clicked.connect(self._on_pair)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_row.addStretch(1)
        button_row.addWidget(self.pair_button)
        button_row.addWidget(self.close_button)
        layout.addLayout(button_row)

    def _load_existing(self) -> None:
        config = load_config()
        if config.server_url:
            self.server_url_input.setText(config.server_url)
        if config.device_name:
            self.device_name_input.setText(config.device_name)
        if config.is_paired:
            self.status_label.setText(f"Paired with {config.server_url}")
        else:
            self.status_label.setText("Not paired")

    def _on_pair(self) -> None:
        url = self.server_url_input.text().strip()
        token = self.pairing_token_input.text().strip()
        device_name = self.device_name_input.text().strip() or None
        if not url or not token:
            QMessageBox.warning(
                self, "Missing data", "Server URL and pairing token are required."
            )
            return

        client = SyncClient()
        try:
            client.pair(url, token, device_name=device_name)
        except SyncError as e:
            QMessageBox.critical(self, "Pairing failed", str(e))
            self.status_label.setText("Pairing failed")
            return

        self.status_label.setText(f"Paired with {url}")
        self.pairing_token_input.clear()
        QMessageBox.information(
            self, "Paired", "This device is now paired. Sync will run on next startup."
        )

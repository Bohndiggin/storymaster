"""Sync Management Dialog - Display QR code and manage synced devices"""

import socket
from datetime import datetime

import requests
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QMessageBox,
    QHeaderView,
)


class SyncDialog(QDialog):
    """Dialog for managing mobile device sync"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mobile Sync Settings")
        self.setMinimumSize(600, 700)

        self.server_url = "http://localhost:8765"
        self.setup_ui()
        self.load_server_info()
        self.load_devices()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()

        # Server Status Group
        status_group = QGroupBox("Sync Server Status")
        status_layout = QVBoxLayout()

        self.status_label = QLabel("Checking server status...")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        status_layout.addWidget(self.status_label)

        self.server_info_label = QLabel("")
        status_layout.addWidget(self.server_info_label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # QR Code Group
        qr_group = QGroupBox("Pair New Device")
        qr_layout = QVBoxLayout()

        instructions = QLabel(
            "Scan this QR code with your mobile app to pair a new device:"
        )
        instructions.setWordWrap(True)
        qr_layout.addWidget(instructions)

        # QR Code image
        self.qr_label = QLabel("Loading QR code...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setMinimumSize(300, 300)
        self.qr_label.setStyleSheet(
            "background-color: white; border: 2px solid #ccc; border-radius: 8px; padding: 10px;"
        )
        qr_layout.addWidget(self.qr_label)

        # Refresh QR button
        refresh_btn = QPushButton("🔄 Refresh QR Code")
        refresh_btn.clicked.connect(self.load_qr_code)
        qr_layout.addWidget(refresh_btn)

        qr_group.setLayout(qr_layout)
        layout.addWidget(qr_group)

        # Paired Devices Group
        devices_group = QGroupBox("Paired Devices")
        devices_layout = QVBoxLayout()

        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(5)
        self.devices_table.setHorizontalHeaderLabels(
            ["Device Name", "Device ID", "Last Sync", "Status", "Actions"]
        )
        # Stretch first 3 columns, fixed size for Status and Actions
        header = self.devices_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Device Name
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Device ID
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Last Sync
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Actions
        self.devices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.devices_table.setEditTriggers(QTableWidget.NoEditTriggers)
        devices_layout.addWidget(self.devices_table)

        # Refresh devices button
        refresh_devices_btn = QPushButton("🔄 Refresh Device List")
        refresh_devices_btn.clicked.connect(self.load_devices)
        devices_layout.addWidget(refresh_devices_btn)

        devices_group.setLayout(devices_layout)
        layout.addWidget(devices_group)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def get_local_ip(self) -> str:
        """Get the local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "localhost"

    def load_server_info(self):
        """Load and display server status"""
        try:
            response = requests.get(f"{self.server_url}/", timeout=2)
            if response.status_code == 200:
                data = response.json()
                local_ip = self.get_local_ip()

                self.status_label.setText("✅ Sync Server: Running")
                self.status_label.setStyleSheet(
                    "font-weight: bold; font-size: 14px; color: #4CAF50;"
                )

                info_text = f"""
Server Address: {local_ip}:8765
Version: {data.get('version', 'Unknown')}
Database: Connected

Mobile devices on the same WiFi network can connect to:
http://{local_ip}:8765
                """.strip()

                self.server_info_label.setText(info_text)

                # Auto-load QR code
                QTimer.singleShot(100, self.load_qr_code)
            else:
                self.show_server_offline()
        except Exception as e:
            self.show_server_offline()

    def show_server_offline(self):
        """Show server offline status"""
        self.status_label.setText("❌ Sync Server: Offline")
        self.status_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #f44336;"
        )
        self.server_info_label.setText(
            "The sync server is not running. Please restart Storymaster."
        )
        self.qr_label.setText("Server offline - QR code unavailable")

    def load_qr_code(self):
        """Fetch and display the QR code"""
        try:
            self.qr_label.setText("Loading QR code...")

            response = requests.get(f"{self.server_url}/api/pair/qr-image", timeout=5)

            if response.status_code == 200:
                # Load image from response
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)

                # Scale to fit while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )

                self.qr_label.setPixmap(scaled_pixmap)
            else:
                self.qr_label.setText("Failed to load QR code")
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to load QR code: HTTP {response.status_code}",
                )

        except requests.exceptions.ConnectionError:
            self.qr_label.setText("Server offline")
            QMessageBox.warning(
                self,
                "Connection Error",
                "Cannot connect to sync server. Make sure Storymaster is running.",
            )
        except Exception as e:
            self.qr_label.setText("Error loading QR code")
            QMessageBox.warning(
                self, "Error", f"Failed to load QR code: {str(e)}"
            )

    def load_devices(self):
        """Load and display paired devices"""
        try:
            response = requests.get(f"{self.server_url}/api/devices", timeout=2)

            if response.status_code == 200:
                data = response.json()
                devices = data.get("devices", [])

                self.devices_table.setRowCount(len(devices))

                for row, device in enumerate(devices):
                    # Device name
                    name_item = QTableWidgetItem(device.get("device_name", "Unknown"))
                    self.devices_table.setItem(row, 0, name_item)

                    # Device ID (shortened)
                    device_id = device.get("device_id", "")
                    short_id = device_id[:12] + "..." if len(device_id) > 15 else device_id
                    id_item = QTableWidgetItem(short_id)
                    self.devices_table.setItem(row, 1, id_item)

                    # Last sync
                    last_sync = device.get("last_sync_at")
                    if last_sync:
                        try:
                            sync_time = datetime.fromisoformat(last_sync.replace("Z", "+00:00"))
                            sync_text = sync_time.strftime("%Y-%m-%d %H:%M")
                        except:
                            sync_text = "Unknown"
                    else:
                        sync_text = "Never"
                    sync_item = QTableWidgetItem(sync_text)
                    self.devices_table.setItem(row, 2, sync_item)

                    # Status
                    status_item = QTableWidgetItem("✅ Active")
                    status_item.setForeground(Qt.darkGreen)
                    self.devices_table.setItem(row, 3, status_item)

                    # Actions - Remove button
                    remove_btn = QPushButton("🗑️ Remove")
                    remove_btn.setStyleSheet(
                        "QPushButton { background-color: #f44336; color: white; "
                        "padding: 5px 10px; border-radius: 3px; }"
                        "QPushButton:hover { background-color: #d32f2f; }"
                    )
                    # Store device_id as property for the button
                    remove_btn.setProperty("device_id", device.get("device_id"))
                    remove_btn.setProperty("device_name", device.get("device_name"))
                    remove_btn.clicked.connect(self.remove_device)
                    self.devices_table.setCellWidget(row, 4, remove_btn)

                if len(devices) == 0:
                    self.devices_table.setRowCount(1)
                    no_devices_item = QTableWidgetItem("No devices paired yet")
                    no_devices_item.setForeground(Qt.gray)
                    self.devices_table.setItem(0, 0, no_devices_item)
                    self.devices_table.setSpan(0, 0, 1, 5)

        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Failed to load devices: {str(e)}"
            )

    def remove_device(self):
        """Remove a synced device"""
        # Get the button that was clicked
        sender = self.sender()
        if not sender:
            return

        device_id = sender.property("device_id")
        device_name = sender.property("device_name")

        if not device_id:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Remove Device",
            f"Are you sure you want to remove device '{device_name}'?\n\n"
            f"This device will no longer be able to sync until it is paired again.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        # Call API to remove the device
        try:
            response = requests.delete(
                f"{self.server_url}/api/devices/{device_id}", timeout=5
            )

            if response.status_code == 200:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Device '{device_name}' has been removed successfully.",
                )
                # Reload the devices list
                self.load_devices()
            elif response.status_code == 404:
                QMessageBox.warning(
                    self, "Error", f"Device not found on server."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to remove device: HTTP {response.status_code}\n{response.text}",
                )

        except requests.exceptions.ConnectionError:
            QMessageBox.warning(
                self,
                "Connection Error",
                "Cannot connect to sync server. Make sure Storymaster is running.",
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to remove device: {str(e)}")

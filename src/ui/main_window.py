"""Main application window with tabbed interface."""

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..core.config_manager import ConfigManager
from ..core.backup_manager import BackupManager
from ..core.niri_interface import NiriInterface
from ..models.config_model import ConfigModel
from .tabs.layout_tab import LayoutTab
from .tabs.visual_tab import VisualTab
from .tabs.opacity_tab import OpacityTab
from .tabs.rules_tab import RulesTab


class MainWindow(QMainWindow):
    """Main application window."""

    config_changed = pyqtSignal()

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize main window.

        Args:
            config_path: Path to Niri config.kdl (default: ~/.config/niri/config.kdl)
        """
        super().__init__()

        self.setWindowTitle("Niri Configuration Manager")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize managers
        self.config_manager = ConfigManager(config_path)
        self.backup_manager = BackupManager(config_path)
        self.niri_interface = NiriInterface()

        # Current configuration model
        self.config_model = None
        self.config_modified = False

        # Setup UI
        self._setup_ui()
        self._load_config()

    def _setup_ui(self):
        """Setup the main UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Create tab instances
        self.layout_tab = LayoutTab()
        self.layout_tab.settings_changed.connect(self.mark_modified)
        self.tabs.addTab(self.layout_tab, "Layout")

        self.visual_tab = VisualTab()
        self.visual_tab.settings_changed.connect(self.mark_modified)
        self.tabs.addTab(self.visual_tab, "Visual")

        self.opacity_tab = OpacityTab()
        self.opacity_tab.settings_changed.connect(self.mark_modified)
        self.tabs.addTab(self.opacity_tab, "Opacity")

        self.rules_tab = RulesTab()
        self.rules_tab.settings_changed.connect(self.mark_modified)
        self.tabs.addTab(self.rules_tab, "Rules")

        # Button layout
        button_layout = QHBoxLayout()

        # Revert button
        self.revert_button = QPushButton("Revert")
        self.revert_button.clicked.connect(self.revert_settings)
        button_layout.addWidget(self.revert_button)

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        # Apply button (Save + Reload Niri)
        self.apply_button = QPushButton("Apply")
        self.apply_button.setStyleSheet("background-color: #4CAF50; color: white;")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)

        main_layout.addLayout(button_layout)
        central_widget.setLayout(main_layout)

        # Disable buttons initially
        self.save_button.setEnabled(False)
        self.apply_button.setEnabled(False)
        self.revert_button.setEnabled(False)


    @staticmethod
    def _create_placeholder_label(text: str):
        """Create a placeholder label widget."""
        from PyQt6.QtWidgets import QLabel
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _load_config(self):
        """Load configuration from file."""
        try:
            self.config_model = self.config_manager.load()
            self.statusBar().showMessage("Configuration loaded successfully")
            self._update_ui_from_model()
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", f"Could not find config file: {e}")
            sys.exit(1)
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid configuration: {e}")
            sys.exit(1)

    def _update_ui_from_model(self):
        """Update UI to reflect current config model."""
        # Load config into each tab
        self.layout_tab.load_config(self.config_model)
        self.visual_tab.load_config(self.config_model)
        self.opacity_tab.load_config(self.config_model)
        self.rules_tab.load_config(self.config_model)
        self.config_changed.emit()

    def mark_modified(self):
        """Mark that configuration has been modified."""
        self.config_modified = True
        self.save_button.setEnabled(True)
        self.apply_button.setEnabled(True)
        self.revert_button.setEnabled(True)

    def save_settings(self):
        """Save configuration to file without reloading Niri."""
        try:
            # Create backup before saving
            backup_path = self.backup_manager.create_backup()

            # Save to file
            self.config_manager.save(self.config_model)

            self.statusBar().showMessage(
                f"Configuration saved. Backup: {backup_path.name}"
            )
            self.config_modified = False
            self.save_button.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save configuration: {e}")

    def apply_settings(self):
        """Save configuration and reload Niri."""
        try:
            # First save
            self.save_settings()

            # Then reload Niri
            success, message = self.niri_interface.reload_config()

            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    "Configuration reloaded successfully!\nWindows should update immediately."
                )
                self.apply_button.setEnabled(False)
                self.statusBar().showMessage("Configuration applied successfully")
            else:
                # Reload failed - offer rollback
                reply = QMessageBox.critical(
                    self,
                    "Reload Failed",
                    f"{message}\n\nDo you want to restore the previous configuration?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    latest_backup = self.backup_manager.get_latest_backup()
                    if latest_backup:
                        self.backup_manager.restore(latest_backup)
                        self.niri_interface.reload_config()
                        self._load_config()
                        QMessageBox.information(
                            self,
                            "Restored",
                            "Previous configuration restored."
                        )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Apply Error",
                f"Failed to apply configuration: {e}"
            )

    def revert_settings(self):
        """Revert to saved configuration."""
        reply = QMessageBox.question(
            self,
            "Revert Changes",
            "Are you sure you want to discard all changes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._load_config()
            self.config_modified = False
            self.save_button.setEnabled(False)
            self.apply_button.setEnabled(False)
            self.revert_button.setEnabled(False)
            self.statusBar().showMessage("Changes reverted")

    def closeEvent(self, event):
        """Handle window close event."""
        if self.config_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_settings()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

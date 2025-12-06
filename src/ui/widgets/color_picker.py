"""Custom color picker widget for selecting colors."""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QColorDialog, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap, QIcon, QFont

from ...models.color import Color


class ColorPicker(QWidget):
    """Custom color picker widget with color swatch and text input.

    Features:
    - Click swatch to open color picker dialog
    - Type color value directly in text field
    - Live color preview
    - Supports multiple color formats
    """

    color_changed = pyqtSignal(str)  # Emits color string

    def __init__(self, initial_color: str = "#000000", parent=None):
        """Initialize color picker.

        Args:
            initial_color: Initial color value
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_color = Color(initial_color)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the widget UI."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Color swatch button
        self.swatch_button = QPushButton()
        self.swatch_button.setFixedSize(48, 32)
        self.swatch_button.clicked.connect(self._on_swatch_clicked)
        self._update_swatch()
        layout.addWidget(self.swatch_button)

        # Color value text input
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("Color (hex, rgb, or name)")
        self.color_input.setText(self.current_color.to_kdl('hex'))
        self.color_input.editingFinished.connect(self._on_text_changed)
        self.color_input.setMaximumWidth(150)
        layout.addWidget(self.color_input)

        # Format label
        self.format_label = QLabel("Hex")
        self.format_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.format_label)

        # Add stretch
        layout.addStretch()

        self.setLayout(layout)

    def _update_swatch(self):
        """Update the color swatch button to show current color."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(self.current_color.to_qcolor())
        self.swatch_button.setIcon(QIcon(pixmap))

    def _on_swatch_clicked(self):
        """Handle color swatch button click."""
        initial_color = self.current_color.to_qcolor()

        color = QColorDialog.getColor(
            initial_color,
            self,
            "Choose Color",
            QColorDialog.ColorDialogOption.ShowAlphaChannel
        )

        if color.isValid():
            # Create color string
            if color.alpha() < 255:
                color_str = color.name(QColor.NameFormat.HexArgb)
            else:
                color_str = color.name(QColor.NameFormat.HexRgb)

            self.set_color(color_str)

    def _on_text_changed(self):
        """Handle color text input change."""
        text = self.color_input.text().strip()
        if text:
            self.set_color(text)

    def set_color(self, color_value: str) -> bool:
        """Set the current color.

        Args:
            color_value: Color string

        Returns:
            True if color is valid
        """
        new_color = Color(color_value)

        if not new_color.to_qcolor().isValid():
            # Invalid color - revert to previous
            self.color_input.setText(self.current_color.to_kdl('hex'))
            return False

        self.current_color = new_color
        self._update_swatch()

        # Update text field (block signals to avoid recursion)
        self.color_input.blockSignals(True)
        self.color_input.setText(new_color.to_kdl('hex'))
        self.color_input.blockSignals(False)

        # Detect format
        if color_value.startswith('rgb'):
            self.format_label.setText("RGB" if 'rgba' not in color_value else "RGBA")
        elif color_value.startswith('hsl'):
            self.format_label.setText("HSL" if 'hsla' not in color_value else "HSLA")
        else:
            self.format_label.setText("Hex")

        self.color_changed.emit(self.current_color.to_kdl('hex'))
        return True

    def get_color(self) -> str:
        """Get current color as hex string.

        Returns:
            Color hex string
        """
        return self.current_color.to_kdl('hex')

    def get_color_object(self) -> Color:
        """Get current color as Color object.

        Returns:
            Color instance
        """
        return self.current_color

    def get_qcolor(self):
        """Get current color as QColor.

        Returns:
            QColor instance
        """
        return self.current_color.to_qcolor()

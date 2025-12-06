"""Color handling utilities supporting multiple KDL color formats."""

import re
from PyQt6.QtGui import QColor
from typing import Tuple, Optional


class Color:
    """Unified color representation supporting KDL color formats.

    Supports:
    - Hex colors: #rgb, #rgba, #rrggbb, #rrggbbaa
    - Named colors: "red", "blue", etc. (CSS standard names)
    - RGB notation: rgb(255, 127, 0)
    - RGBA notation: rgba(255, 127, 0, 0.5)
    - HSL notation: hsl(180, 100%, 50%)
    """

    def __init__(self, value: str):
        """Initialize Color from string value.

        Args:
            value: Color string in any supported format
        """
        self.original = value
        self.qcolor = self._parse(value)

    def _parse(self, value: str) -> QColor:
        """Parse color string to QColor.

        Args:
            value: Color string

        Returns:
            QColor instance
        """
        if not value:
            return QColor("black")

        value = value.strip().strip('"').strip()

        # CSS named colors
        if value.isalpha() or value.replace('-', '').replace('_', '').isalpha():
            qc = QColor(value)
            if qc.isValid():
                return qc

        # Hex colors: #rgb, #rgba, #rrggbb, #rrggbbaa
        if value.startswith('#'):
            qc = QColor(value)
            if qc.isValid():
                return qc

        # rgb() or rgba() format: rgb(255, 127, 0) or rgba(255, 127, 0, 0.5)
        rgb_match = re.match(
            r'rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*([\d.]+))?\s*\)',
            value
        )
        if rgb_match:
            r = int(rgb_match.group(1))
            g = int(rgb_match.group(2))
            b = int(rgb_match.group(3))
            a = int(float(rgb_match.group(4)) * 255) if rgb_match.group(4) else 255

            # Clamp values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            a = max(0, min(255, a))

            return QColor(r, g, b, a)

        # hsl() or hsla() format
        hsl_match = re.match(
            r'hsla?\(\s*(\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%\s*(?:,\s*([\d.]+))?\s*\)',
            value
        )
        if hsl_match:
            h = int(hsl_match.group(1))
            s = int(hsl_match.group(2))
            l = int(hsl_match.group(3))
            a = int(float(hsl_match.group(4)) * 255) if hsl_match.group(4) else 255

            qc = QColor.fromHsl(h, s, l, a)
            if qc.isValid():
                return qc

        # Fallback to black
        return QColor("black")

    def to_kdl(self, format_type: str = 'hex') -> str:
        """Convert to KDL color string.

        Args:
            format_type: Output format ('hex', 'rgb', 'hsl', or 'original')

        Returns:
            Color string in KDL format (no quotes)
        """
        if format_type == 'original':
            return self.original.strip('"')

        if not self.qcolor.isValid():
            return "#000000"

        if format_type == 'hex':
            # Return hex with alpha if needed
            if self.qcolor.alpha() < 255:
                return self.qcolor.name(QColor.NameFormat.HexArgb)
            return self.qcolor.name(QColor.NameFormat.HexRgb)

        elif format_type == 'rgb':
            if self.qcolor.alpha() < 255:
                alpha = self.qcolor.alphaF()
                return f'rgba({self.qcolor.red()}, {self.qcolor.green()}, {self.qcolor.blue()}, {alpha:.2f})'
            return f'rgb({self.qcolor.red()}, {self.qcolor.green()}, {self.qcolor.blue()})'

        elif format_type == 'hsl':
            h = self.qcolor.hue()
            s = self.qcolor.saturation()
            l = self.qcolor.lightness()
            if self.qcolor.alpha() < 255:
                alpha = self.qcolor.alphaF()
                return f'hsla({h}, {s}%, {l}%, {alpha:.2f})'
            return f'hsl({h}, {s}%, {l}%)'

        # Default to hex
        return self.qcolor.name(QColor.NameFormat.HexRgb)

    def to_qcolor(self) -> QColor:
        """Get as QColor for use in Qt widgets.

        Returns:
            QColor instance
        """
        return QColor(self.qcolor)

    def get_rgb(self) -> Tuple[int, int, int]:
        """Get RGB components.

        Returns:
            Tuple of (red, green, blue)
        """
        return (self.qcolor.red(), self.qcolor.green(), self.qcolor.blue())

    def get_rgba(self) -> Tuple[int, int, int, int]:
        """Get RGBA components.

        Returns:
            Tuple of (red, green, blue, alpha)
        """
        return (self.qcolor.red(), self.qcolor.green(), self.qcolor.blue(), self.qcolor.alpha())

    def get_hsl(self) -> Tuple[int, int, int]:
        """Get HSL components.

        Returns:
            Tuple of (hue, saturation, lightness) where saturation and lightness are 0-100
        """
        return (self.qcolor.hue(), self.qcolor.saturation(), self.qcolor.lightness())

    def with_alpha(self, alpha: float) -> 'Color':
        """Return new Color with different alpha.

        Args:
            alpha: Alpha value 0.0-1.0

        Returns:
            New Color instance
        """
        new_color = QColor(self.qcolor)
        new_color.setAlphaF(alpha)

        # Convert to string representation
        if new_color.alpha() < 255:
            color_str = new_color.name(QColor.NameFormat.HexArgb)
        else:
            color_str = new_color.name(QColor.NameFormat.HexRgb)

        return Color(color_str)

    def __repr__(self) -> str:
        """String representation."""
        return f"Color({self.original})"

    def __eq__(self, other) -> bool:
        """Compare colors."""
        if isinstance(other, Color):
            return self.qcolor.getRgb() == other.qcolor.getRgb()
        elif isinstance(other, str):
            return self.original == other
        return False

    @staticmethod
    def is_valid_color(value: str) -> bool:
        """Check if string is a valid color.

        Args:
            value: Color string to validate

        Returns:
            True if valid color format
        """
        try:
            color = Color(value)
            return color.qcolor.isValid()
        except Exception:
            return False

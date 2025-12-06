"""Input validation logic for Niri configuration values."""

import re
from typing import Tuple


class Validators:
    """Validation functions for configuration values."""

    @staticmethod
    def validate_gaps(value: int) -> Tuple[bool, str]:
        """Validate window gaps value."""
        if not isinstance(value, int):
            return False, "Gaps must be an integer"
        if value < 0:
            return False, "Gaps cannot be negative"
        if value > 256:
            return False, "Gaps too large (max 256px)"
        return True, ""

    @staticmethod
    def validate_corner_radius(value: int) -> Tuple[bool, str]:
        """Validate corner radius value."""
        if not isinstance(value, int):
            return False, "Corner radius must be an integer"
        if value < 0:
            return False, "Corner radius cannot be negative"
        if value > 256:
            return False, "Corner radius too large (max 256px)"
        return True, ""

    @staticmethod
    def validate_opacity(value: float) -> Tuple[bool, str]:
        """Validate opacity value (0.0-1.0)."""
        try:
            opacity = float(value)
        except (ValueError, TypeError):
            return False, "Opacity must be a number"

        if not 0.0 <= opacity <= 1.0:
            return False, "Opacity must be between 0.0 and 1.0"
        return True, ""

    @staticmethod
    def validate_regex(pattern: str) -> Tuple[bool, str]:
        """Validate regular expression pattern."""
        try:
            re.compile(pattern)
            return True, ""
        except re.error as e:
            return False, f"Invalid regex: {str(e)}"

    @staticmethod
    def validate_center_mode(value: str) -> Tuple[bool, str]:
        """Validate center-focused-column mode."""
        valid_modes = ["never", "always", "on-overflow"]
        if value not in valid_modes:
            return False, f"Must be one of: {', '.join(valid_modes)}"
        return True, ""

    @staticmethod
    def validate_color(value: str) -> Tuple[bool, str]:
        """Validate color format."""
        # CSS named colors (simple check - just see if it's alphabetic)
        if value.isalpha():
            return True, ""

        # Hex colors: #rgb, #rgba, #rrggbb, #rrggbbaa
        if re.match(r'^#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?([0-9a-fA-F]{2})?$', value):
            return True, ""

        # rgb() or rgba() format
        if re.match(
            r'^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*([0-9.]+))?\s*\)$',
            value
        ):
            return True, ""

        return False, "Invalid color format (use hex #rrggbb, rgb(r,g,b), or named color)"

    @staticmethod
    def validate_ring_width(value: int) -> Tuple[bool, str]:
        """Validate focus ring/border width."""
        if not isinstance(value, int):
            return False, "Width must be an integer"
        if value < 0:
            return False, "Width cannot be negative"
        if value > 32:
            return False, "Width too large (max 32px)"
        return True, ""

    @staticmethod
    def validate_shadow_softness(value: int) -> Tuple[bool, str]:
        """Validate shadow softness (blur radius)."""
        if not isinstance(value, int):
            return False, "Softness must be an integer"
        if value < 0:
            return False, "Softness cannot be negative"
        if value > 128:
            return False, "Softness too large (max 128px)"
        return True, ""

    @staticmethod
    def validate_shadow_spread(value: int) -> Tuple[bool, str]:
        """Validate shadow spread."""
        if not isinstance(value, int):
            return False, "Spread must be an integer"
        if value < -64:
            return False, "Spread too small (min -64px)"
        if value > 64:
            return False, "Spread too large (max 64px)"
        return True, ""

    @staticmethod
    def validate_offset(value: int) -> Tuple[bool, str]:
        """Validate shadow offset."""
        if not isinstance(value, int):
            return False, "Offset must be an integer"
        if value < -256:
            return False, "Offset too small (min -256px)"
        if value > 256:
            return False, "Offset too large (max 256px)"
        return True, ""

    @staticmethod
    def validate_strut(value: int) -> Tuple[bool, str]:
        """Validate strut value."""
        if not isinstance(value, int):
            return False, "Strut must be an integer"
        if value < 0:
            return False, "Strut cannot be negative"
        if value > 1024:
            return False, "Strut too large (max 1024px)"
        return True, ""

    @staticmethod
    def validate_slowdown(value: float) -> Tuple[bool, str]:
        """Validate animation slowdown multiplier."""
        try:
            slowdown = float(value)
        except (ValueError, TypeError):
            return False, "Slowdown must be a number"

        if slowdown <= 0:
            return False, "Slowdown must be positive"
        if slowdown > 100:
            return False, "Slowdown too large (max 100x)"
        return True, ""

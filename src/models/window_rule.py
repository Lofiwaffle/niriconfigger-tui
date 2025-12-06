"""Window rule models and utilities for Niri configuration."""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class RuleMatch:
    """A single match condition for window rules."""

    VALID_CONDITIONS = ["app-id", "title", "is-focused", "is-active", "at-startup"]

    condition_type: str  # "app-id", "title", "is-focused", etc.
    value: str
    use_regex: bool = False

    def is_valid(self) -> bool:
        """Check if this match condition is valid.

        Returns:
            True if condition type is recognized
        """
        return self.condition_type in self.VALID_CONDITIONS

    def to_kdl(self) -> str:
        """Convert to KDL syntax.

        Returns:
            KDL match line (without leading 'match ' keyword)
        """
        if self.use_regex and self.condition_type in ["app-id", "title"]:
            return f'{self.condition_type}=r#"{self.value}"#'
        else:
            # Boolean conditions don't use quotes
            if self.condition_type in ["is-focused", "is-active", "at-startup"]:
                return f'{self.condition_type}={self.value}'
            else:
                return f'{self.condition_type}="{self.value}"'

    def matches_window(self, app_id: str = "", title: str = "", is_focused: bool = False) -> bool:
        """Check if this condition matches given window properties.

        Args:
            app_id: Application ID of window
            title: Window title
            is_focused: Whether window is focused

        Returns:
            True if condition matches
        """
        if self.condition_type == "app-id":
            if self.use_regex:
                try:
                    return bool(re.match(self.value, app_id))
                except re.error:
                    return False
            else:
                return app_id == self.value

        elif self.condition_type == "title":
            if self.use_regex:
                try:
                    return bool(re.search(self.value, title))
                except re.error:
                    return False
            else:
                return self.value in title

        elif self.condition_type == "is-focused":
            return is_focused == (self.value == "true")

        return False


@dataclass
class WindowRule:
    """A window rule with match conditions and properties."""

    id: str = ""  # Internal identifier for tracking
    name: str = ""  # Human-readable name (optional)
    matches: List[RuleMatch] = field(default_factory=list)

    # Visual properties
    opacity: Optional[float] = None
    corner_radius: Optional[int] = None
    clip_to_geometry: Optional[bool] = None

    # Behavior properties
    open_floating: Optional[bool] = None
    at_startup_floating: Optional[bool] = None
    block_out_from: Optional[str] = None  # "screen-capture", "screencast", etc.

    # Layout properties
    default_column_width: Optional[str] = None  # "proportion:0.5" or "fixed:1920"
    min_width: Optional[int] = None
    max_width: Optional[int] = None

    def is_valid(self) -> bool:
        """Check if rule is valid.

        Returns:
            True if rule has at least one match and one property
        """
        has_matches = len(self.matches) > 0
        has_properties = any([
            self.opacity is not None,
            self.corner_radius is not None,
            self.clip_to_geometry is not None,
            self.open_floating is not None,
            self.at_startup_floating is not None,
            self.block_out_from is not None,
            self.default_column_width is not None,
            self.min_width is not None,
            self.max_width is not None,
        ])
        return has_matches and has_properties

    def to_kdl(self) -> str:
        """Convert rule to KDL syntax.

        Returns:
            Complete window-rule block as KDL
        """
        lines = ["window-rule {"]

        # Add match conditions
        for match in self.matches:
            lines.append(f"    match {match.to_kdl()}")

        # Add visual properties
        if self.opacity is not None:
            lines.append(f"    opacity {self.opacity}")

        if self.corner_radius is not None:
            lines.append(f"    geometry-corner-radius {self.corner_radius}")

        if self.clip_to_geometry is not None:
            value = "true" if self.clip_to_geometry else "false"
            lines.append(f"    clip-to-geometry {value}")

        # Add behavior properties
        if self.open_floating is not None:
            value = "true" if self.open_floating else "false"
            lines.append(f"    open-floating {value}")

        if self.block_out_from is not None:
            lines.append(f'    block-out-from "{self.block_out_from}"')

        # Add layout properties
        if self.default_column_width is not None:
            if self.default_column_width.startswith("proportion:"):
                prop = self.default_column_width.split(":")[1]
                lines.append(f"    default-column-width {{ proportion {prop}; }}")
            elif self.default_column_width.startswith("fixed:"):
                pixels = self.default_column_width.split(":")[1]
                lines.append(f"    default-column-width {{ fixed {pixels}; }}")

        if self.min_width is not None:
            lines.append(f"    min-width {self.min_width}")

        if self.max_width is not None:
            lines.append(f"    max-width {self.max_width}")

        lines.append("}")
        return "\n".join(lines)

    def matches_window(self, app_id: str = "", title: str = "", is_focused: bool = False) -> bool:
        """Check if this rule matches the given window.

        All match conditions must be satisfied (AND logic).

        Args:
            app_id: Application ID
            title: Window title
            is_focused: Whether window is focused

        Returns:
            True if all conditions match
        """
        if not self.matches:
            return False

        for match in self.matches:
            if not match.matches_window(app_id, title, is_focused):
                return False

        return True

    def get_description(self) -> str:
        """Get human-readable description of rule.

        Returns:
            Description string
        """
        if self.name:
            return self.name

        # Build from matches
        match_descs = []
        for match in self.matches:
            if match.condition_type == "app-id":
                match_descs.append(f"app-id: {match.value}")
            elif match.condition_type == "title":
                match_descs.append(f"title: {match.value}")
            elif match.condition_type == "is-focused":
                match_descs.append(f"focused: {match.value}")

        matches_str = ", ".join(match_descs) if match_descs else "any window"

        # Build from properties
        props = []
        if self.opacity is not None:
            props.append(f"opacity={self.opacity}")
        if self.open_floating:
            props.append("floating")
        if self.corner_radius is not None:
            props.append(f"radius={self.corner_radius}")

        props_str = ", ".join(props) if props else "rule"

        return f"{matches_str} → {props_str}"

    @staticmethod
    def parse_from_kdl(kdl_block: str) -> Optional['WindowRule']:
        """Parse a window-rule block from KDL.

        Args:
            kdl_block: KDL window-rule block text

        Returns:
            WindowRule instance or None if parsing failed
        """
        rule = WindowRule()

        # Extract match lines
        match_pattern = r'match\s+(\w+)=(?:r#"([^"]+)"#|"([^"]+)"|(\w+))'
        for match_obj in re.finditer(match_pattern, kdl_block):
            condition = match_obj.group(1)
            regex_value = match_obj.group(2)
            string_value = match_obj.group(3)
            bool_value = match_obj.group(4)

            if regex_value:
                rule.matches.append(RuleMatch(condition, regex_value, use_regex=True))
            elif string_value:
                rule.matches.append(RuleMatch(condition, string_value, use_regex=False))
            elif bool_value:
                rule.matches.append(RuleMatch(condition, bool_value, use_regex=False))

        # Extract opacity
        opacity_match = re.search(r'opacity\s+([\d.]+)', kdl_block)
        if opacity_match:
            rule.opacity = float(opacity_match.group(1))

        # Extract corner radius
        corner_match = re.search(r'geometry-corner-radius\s+(\d+)', kdl_block)
        if corner_match:
            rule.corner_radius = int(corner_match.group(1))

        # Extract clip-to-geometry
        clip_match = re.search(r'clip-to-geometry\s+(true|false)', kdl_block)
        if clip_match:
            rule.clip_to_geometry = clip_match.group(1) == "true"

        # Extract open-floating
        floating_match = re.search(r'open-floating\s+(true|false)', kdl_block)
        if floating_match:
            rule.open_floating = floating_match.group(1) == "true"

        # Extract block-out-from
        blockout_match = re.search(r'block-out-from\s+"([^"]+)"', kdl_block)
        if blockout_match:
            rule.block_out_from = blockout_match.group(1)

        return rule if rule.is_valid() else None


# Preset window rules for common applications
RULE_TEMPLATES = {
    "firefox_pip": {
        "name": "Firefox Picture-in-Picture",
        "matches": [
            RuleMatch("app-id", "firefox", use_regex=True),
            RuleMatch("title", "Picture-in-Picture", use_regex=False),
        ],
        "open_floating": True,
    },
    "steam_floating": {
        "name": "Steam floating dialogs",
        "matches": [
            RuleMatch("app-id", "steam", use_regex=True),
        ],
        "open_floating": True,
    },
    "modal_dialog": {
        "name": "Modal dialogs",
        "matches": [
            RuleMatch("title", "dialog|modal|settings", use_regex=True),
        ],
        "open_floating": True,
    },
    "terminal": {
        "name": "Terminal windows",
        "matches": [
            RuleMatch("app-id", "kitty|wezterm|ghostty|alacritty", use_regex=True),
        ],
        "default_column_width": "proportion:0.5",
    },
}


def get_rule_template(template_id: str) -> Optional[WindowRule]:
    """Get a preset rule template.

    Args:
        template_id: ID of template (e.g., "firefox_pip")

    Returns:
        WindowRule instance or None
    """
    if template_id not in RULE_TEMPLATES:
        return None

    template_data = RULE_TEMPLATES[template_id]
    rule = WindowRule(name=template_data.get("name", ""))
    rule.matches = template_data.get("matches", [])
    rule.open_floating = template_data.get("open_floating")
    rule.opacity = template_data.get("opacity")
    rule.corner_radius = template_data.get("corner_radius")
    rule.default_column_width = template_data.get("default_column_width")

    return rule


def get_template_list() -> List[Tuple[str, str]]:
    """Get list of available templates.

    Returns:
        List of (template_id, template_name) tuples
    """
    return [(key, data["name"]) for key, data in RULE_TEMPLATES.items()]

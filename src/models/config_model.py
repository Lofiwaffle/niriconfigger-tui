"""Data models for Niri configuration."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class LayoutSettings:
    """Layout-related configuration settings."""
    gaps: int = 4
    center_focused_column: str = "never"  # "never", "always", "on-overflow"
    struts_top: int = 0
    struts_bottom: int = 0
    struts_left: int = 0
    struts_right: int = 0


@dataclass
class FocusRing:
    """Focus ring configuration."""
    enabled: bool = True
    width: int = 4
    active_color: str = "#a3d7ff"
    inactive_color: str = "#101417"


@dataclass
class Border:
    """Window border configuration."""
    enabled: bool = False
    width: int = 4
    active_color: str = "#a3d7ff"
    inactive_color: str = "#101417"
    urgent_color: str = "#ffb4ab"


@dataclass
class Shadow:
    """Window shadow configuration."""
    enabled: bool = False
    softness: int = 30
    spread: int = 5
    offset_x: int = 0
    offset_y: int = 5
    color: str = "#00000070"
    draw_behind_window: bool = True


@dataclass
class VisualSettings:
    """Visual appearance settings."""
    corner_radius: int = 16
    clip_to_geometry: bool = True
    focus_ring: FocusRing = field(default_factory=FocusRing)
    border: Border = field(default_factory=Border)
    shadow: Shadow = field(default_factory=Shadow)


@dataclass
class RuleMatch:
    """A single match condition for a window rule."""
    condition_type: str  # "app-id", "title", "is-focused", "is-active"
    value: str
    use_regex: bool = False


@dataclass
class WindowRule:
    """A window rule with match conditions and properties."""
    id: str = ""  # Internal identifier for tracking
    name: str = ""  # Human-readable name
    matches: List[RuleMatch] = field(default_factory=list)

    # Properties that can be set by the rule
    opacity: Optional[float] = None
    corner_radius: Optional[int] = None
    clip_to_geometry: Optional[bool] = None
    open_floating: Optional[bool] = None
    default_column_width: Optional[str] = None  # "proportion:0.5" or "fixed:1920"
    block_out_from: Optional[str] = None  # "screen-capture", "screencast"

    def to_kdl(self) -> str:
        """Convert rule to KDL syntax."""
        lines = ["window-rule {"]

        # Add match conditions
        for match in self.matches:
            if match.use_regex:
                lines.append(f'    match {match.condition_type}=r#"{match.value}"#')
            else:
                lines.append(f'    match {match.condition_type}="{match.value}"')

        # Add properties
        if self.opacity is not None:
            lines.append(f'    opacity {self.opacity}')

        if self.corner_radius is not None:
            lines.append(f'    geometry-corner-radius {self.corner_radius}')

        if self.clip_to_geometry is not None:
            value = "true" if self.clip_to_geometry else "false"
            lines.append(f'    clip-to-geometry {value}')

        if self.open_floating is not None:
            value = "true" if self.open_floating else "false"
            lines.append(f'    open-floating {value}')

        if self.default_column_width is not None:
            if self.default_column_width.startswith("proportion:"):
                prop = self.default_column_width.split(":")[1]
                lines.append(f'    default-column-width {{ proportion {prop}; }}')
            elif self.default_column_width.startswith("fixed:"):
                pixels = self.default_column_width.split(":")[1]
                lines.append(f'    default-column-width {{ fixed {pixels}; }}')

        if self.block_out_from is not None:
            lines.append(f'    block-out-from "{self.block_out_from}"')

        lines.append("}")
        return "\n".join(lines)


@dataclass
class ConfigModel:
    """Complete Niri configuration model."""
    layout: LayoutSettings = field(default_factory=LayoutSettings)
    visual: VisualSettings = field(default_factory=VisualSettings)
    window_rules: List[WindowRule] = field(default_factory=list)
    animations_enabled: bool = True
    animations_slowdown: float = 1.0
    prefer_no_csd: bool = True

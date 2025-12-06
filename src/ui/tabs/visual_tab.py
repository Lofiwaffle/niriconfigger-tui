"""Visual settings tab for corner radius, focus ring, border, and shadows."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QSlider,
    QCheckBox, QGroupBox, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from ...core.validators import Validators
from ...models.config_model import ConfigModel
from ...ui.widgets.color_picker import ColorPicker


class VisualTab(QWidget):
    """Tab for visual settings."""

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize visual tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_model = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the tab UI."""
        main_layout = QVBoxLayout()

        # Corner Radius section
        corner_group = QGroupBox("Window Corner Radius")
        corner_layout = QGridLayout()

        corner_layout.addWidget(QLabel("Corner Radius (px):"), 0, 0)

        self.corner_spinbox = QSpinBox()
        self.corner_spinbox.setMinimum(0)
        self.corner_spinbox.setMaximum(256)
        self.corner_spinbox.setValue(16)
        self.corner_spinbox.valueChanged.connect(self._on_corner_changed)
        corner_layout.addWidget(self.corner_spinbox, 0, 1)

        self.corner_slider = QSlider(Qt.Orientation.Horizontal)
        self.corner_slider.setMinimum(0)
        self.corner_slider.setMaximum(256)
        self.corner_slider.setValue(16)
        self.corner_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.corner_slider.setTickInterval(16)
        self.corner_slider.valueChanged.connect(self._on_corner_slider_changed)
        corner_layout.addWidget(self.corner_slider, 0, 2)

        self.clip_to_geometry_check = QCheckBox("Clip window content to rounded corners")
        self.clip_to_geometry_check.setChecked(True)
        self.clip_to_geometry_check.stateChanged.connect(self._on_visual_changed)
        corner_layout.addWidget(self.clip_to_geometry_check, 1, 0, 1, 3)

        corner_group.setLayout(corner_layout)
        main_layout.addWidget(corner_group)

        # Focus Ring section
        focus_group = QGroupBox("Focus Ring")
        focus_layout = QGridLayout()

        self.focus_enabled = QCheckBox("Enable focus ring")
        self.focus_enabled.setChecked(True)
        self.focus_enabled.stateChanged.connect(self._on_visual_changed)
        focus_layout.addWidget(self.focus_enabled, 0, 0, 1, 3)

        focus_layout.addWidget(QLabel("Width (px):"), 1, 0)
        self.focus_width_spinbox = QSpinBox()
        self.focus_width_spinbox.setMinimum(0)
        self.focus_width_spinbox.setMaximum(32)
        self.focus_width_spinbox.setValue(4)
        self.focus_width_spinbox.valueChanged.connect(self._on_visual_changed)
        focus_layout.addWidget(self.focus_width_spinbox, 1, 1)

        focus_layout.addWidget(QLabel("Active color:"), 2, 0)
        self.focus_active_picker = ColorPicker("#a3d7ff")
        self.focus_active_picker.color_changed.connect(self._on_visual_changed)
        focus_layout.addWidget(self.focus_active_picker, 2, 1, 1, 2)

        focus_layout.addWidget(QLabel("Inactive color:"), 3, 0)
        self.focus_inactive_picker = ColorPicker("#101417")
        self.focus_inactive_picker.color_changed.connect(self._on_visual_changed)
        focus_layout.addWidget(self.focus_inactive_picker, 3, 1, 1, 2)

        focus_group.setLayout(focus_layout)
        main_layout.addWidget(focus_group)

        # Border section
        border_group = QGroupBox("Border")
        border_layout = QGridLayout()

        self.border_enabled = QCheckBox("Enable border")
        self.border_enabled.setChecked(False)
        self.border_enabled.stateChanged.connect(self._on_visual_changed)
        border_layout.addWidget(self.border_enabled, 0, 0, 1, 3)

        border_layout.addWidget(QLabel("Width (px):"), 1, 0)
        self.border_width_spinbox = QSpinBox()
        self.border_width_spinbox.setMinimum(0)
        self.border_width_spinbox.setMaximum(32)
        self.border_width_spinbox.setValue(4)
        self.border_width_spinbox.valueChanged.connect(self._on_visual_changed)
        border_layout.addWidget(self.border_width_spinbox, 1, 1)

        border_layout.addWidget(QLabel("Active color:"), 2, 0)
        self.border_active_picker = ColorPicker("#a3d7ff")
        self.border_active_picker.color_changed.connect(self._on_visual_changed)
        border_layout.addWidget(self.border_active_picker, 2, 1, 1, 2)

        border_layout.addWidget(QLabel("Inactive color:"), 3, 0)
        self.border_inactive_picker = ColorPicker("#101417")
        self.border_inactive_picker.color_changed.connect(self._on_visual_changed)
        border_layout.addWidget(self.border_inactive_picker, 3, 1, 1, 2)

        border_layout.addWidget(QLabel("Urgent color:"), 4, 0)
        self.border_urgent_picker = ColorPicker("#ffb4ab")
        self.border_urgent_picker.color_changed.connect(self._on_visual_changed)
        border_layout.addWidget(self.border_urgent_picker, 4, 1, 1, 2)

        border_group.setLayout(border_layout)
        main_layout.addWidget(border_group)

        # Shadow section
        shadow_group = QGroupBox("Shadow")
        shadow_layout = QGridLayout()

        self.shadow_enabled = QCheckBox("Enable shadow")
        self.shadow_enabled.setChecked(False)
        self.shadow_enabled.stateChanged.connect(self._on_visual_changed)
        shadow_layout.addWidget(self.shadow_enabled, 0, 0, 1, 3)

        shadow_layout.addWidget(QLabel("Softness (px):"), 1, 0)
        self.shadow_softness_spinbox = QSpinBox()
        self.shadow_softness_spinbox.setMinimum(0)
        self.shadow_softness_spinbox.setMaximum(128)
        self.shadow_softness_spinbox.setValue(30)
        self.shadow_softness_spinbox.valueChanged.connect(self._on_visual_changed)
        shadow_layout.addWidget(self.shadow_softness_spinbox, 1, 1)

        shadow_layout.addWidget(QLabel("Spread (px):"), 2, 0)
        self.shadow_spread_spinbox = QSpinBox()
        self.shadow_spread_spinbox.setMinimum(-64)
        self.shadow_spread_spinbox.setMaximum(64)
        self.shadow_spread_spinbox.setValue(5)
        self.shadow_spread_spinbox.valueChanged.connect(self._on_visual_changed)
        shadow_layout.addWidget(self.shadow_spread_spinbox, 2, 1)

        shadow_layout.addWidget(QLabel("Offset X (px):"), 3, 0)
        self.shadow_offset_x_spinbox = QSpinBox()
        self.shadow_offset_x_spinbox.setMinimum(-256)
        self.shadow_offset_x_spinbox.setMaximum(256)
        self.shadow_offset_x_spinbox.setValue(0)
        self.shadow_offset_x_spinbox.valueChanged.connect(self._on_visual_changed)
        shadow_layout.addWidget(self.shadow_offset_x_spinbox, 3, 1)

        shadow_layout.addWidget(QLabel("Offset Y (px):"), 4, 0)
        self.shadow_offset_y_spinbox = QSpinBox()
        self.shadow_offset_y_spinbox.setMinimum(-256)
        self.shadow_offset_y_spinbox.setMaximum(256)
        self.shadow_offset_y_spinbox.setValue(5)
        self.shadow_offset_y_spinbox.valueChanged.connect(self._on_visual_changed)
        shadow_layout.addWidget(self.shadow_offset_y_spinbox, 4, 1)

        shadow_layout.addWidget(QLabel("Color:"), 5, 0)
        self.shadow_color_picker = ColorPicker("#00000070")
        self.shadow_color_picker.color_changed.connect(self._on_visual_changed)
        shadow_layout.addWidget(self.shadow_color_picker, 5, 1, 1, 2)

        self.shadow_behind_check = QCheckBox("Draw shadow behind window")
        self.shadow_behind_check.setChecked(True)
        self.shadow_behind_check.stateChanged.connect(self._on_visual_changed)
        shadow_layout.addWidget(self.shadow_behind_check, 6, 0, 1, 3)

        shadow_group.setLayout(shadow_layout)
        main_layout.addWidget(shadow_group)

        # Add stretch to push everything to the top
        main_layout.addStretch()

        self.setLayout(main_layout)

    def load_config(self, config_model: ConfigModel):
        """Load configuration into tab.

        Args:
            config_model: ConfigModel instance
        """
        self.config_model = config_model

        # Block signals while loading
        self._block_signals(True)

        # Load corner radius
        self.corner_spinbox.setValue(config_model.visual.corner_radius)
        self.corner_slider.setValue(config_model.visual.corner_radius)
        self.clip_to_geometry_check.setChecked(config_model.visual.clip_to_geometry)

        # Load focus ring
        self.focus_enabled.setChecked(config_model.visual.focus_ring.enabled)
        self.focus_width_spinbox.setValue(config_model.visual.focus_ring.width)
        self.focus_active_picker.set_color(config_model.visual.focus_ring.active_color)
        self.focus_inactive_picker.set_color(config_model.visual.focus_ring.inactive_color)

        # Load border
        self.border_enabled.setChecked(config_model.visual.border.enabled)
        self.border_width_spinbox.setValue(config_model.visual.border.width)
        self.border_active_picker.set_color(config_model.visual.border.active_color)
        self.border_inactive_picker.set_color(config_model.visual.border.inactive_color)
        self.border_urgent_picker.set_color(config_model.visual.border.urgent_color)

        # Load shadow
        self.shadow_enabled.setChecked(config_model.visual.shadow.enabled)
        self.shadow_softness_spinbox.setValue(config_model.visual.shadow.softness)
        self.shadow_spread_spinbox.setValue(config_model.visual.shadow.spread)
        self.shadow_offset_x_spinbox.setValue(config_model.visual.shadow.offset_x)
        self.shadow_offset_y_spinbox.setValue(config_model.visual.shadow.offset_y)
        self.shadow_color_picker.set_color(config_model.visual.shadow.color)
        self.shadow_behind_check.setChecked(config_model.visual.shadow.draw_behind_window)

        self._block_signals(False)

    def _block_signals(self, block: bool):
        """Block/unblock all signals."""
        for widget in [
            self.corner_spinbox, self.corner_slider, self.clip_to_geometry_check,
            self.focus_enabled, self.focus_width_spinbox, self.focus_active_picker, self.focus_inactive_picker,
            self.border_enabled, self.border_width_spinbox, self.border_active_picker, self.border_inactive_picker, self.border_urgent_picker,
            self.shadow_enabled, self.shadow_softness_spinbox, self.shadow_spread_spinbox,
            self.shadow_offset_x_spinbox, self.shadow_offset_y_spinbox, self.shadow_color_picker, self.shadow_behind_check
        ]:
            widget.blockSignals(block)

    def _on_corner_changed(self, value: int):
        """Handle corner radius spinbox change."""
        if not self.config_model:
            return

        valid, error = Validators.validate_corner_radius(value)
        if valid:
            self.corner_slider.blockSignals(True)
            self.corner_slider.setValue(value)
            self.corner_slider.blockSignals(False)

            self.config_model.visual.corner_radius = value
            self.settings_changed.emit()

    def _on_corner_slider_changed(self, value: int):
        """Handle corner radius slider change."""
        self.corner_spinbox.blockSignals(True)
        self.corner_spinbox.setValue(value)
        self.corner_spinbox.blockSignals(False)
        self._on_corner_changed(value)

    def _on_visual_changed(self):
        """Handle any visual setting change."""
        if not self.config_model:
            return

        # Update config model
        self.config_model.visual.clip_to_geometry = self.clip_to_geometry_check.isChecked()
        self.config_model.visual.focus_ring.enabled = self.focus_enabled.isChecked()
        self.config_model.visual.focus_ring.width = self.focus_width_spinbox.value()
        self.config_model.visual.focus_ring.active_color = self.focus_active_picker.get_color()
        self.config_model.visual.focus_ring.inactive_color = self.focus_inactive_picker.get_color()

        self.config_model.visual.border.enabled = self.border_enabled.isChecked()
        self.config_model.visual.border.width = self.border_width_spinbox.value()
        self.config_model.visual.border.active_color = self.border_active_picker.get_color()
        self.config_model.visual.border.inactive_color = self.border_inactive_picker.get_color()
        self.config_model.visual.border.urgent_color = self.border_urgent_picker.get_color()

        self.config_model.visual.shadow.enabled = self.shadow_enabled.isChecked()
        self.config_model.visual.shadow.softness = self.shadow_softness_spinbox.value()
        self.config_model.visual.shadow.spread = self.shadow_spread_spinbox.value()
        self.config_model.visual.shadow.offset_x = self.shadow_offset_x_spinbox.value()
        self.config_model.visual.shadow.offset_y = self.shadow_offset_y_spinbox.value()
        self.config_model.visual.shadow.color = self.shadow_color_picker.get_color()
        self.config_model.visual.shadow.draw_behind_window = self.shadow_behind_check.isChecked()

        self.settings_changed.emit()

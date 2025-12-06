"""Layout settings tab for gaps, struts, and column centering."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QSlider, QComboBox, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from ...core.validators import Validators
from ...models.config_model import ConfigModel


class LayoutTab(QWidget):
    """Tab for layout-related settings."""

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize layout tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_model = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the tab UI."""
        main_layout = QVBoxLayout()

        # Gaps section
        gaps_group = QGroupBox("Window Gaps")
        gaps_layout = QGridLayout()

        gaps_layout.addWidget(QLabel("Gaps (px):"), 0, 0)

        self.gaps_spinbox = QSpinBox()
        self.gaps_spinbox.setMinimum(0)
        self.gaps_spinbox.setMaximum(256)
        self.gaps_spinbox.setValue(4)
        self.gaps_spinbox.valueChanged.connect(self._on_gaps_changed)
        gaps_layout.addWidget(self.gaps_spinbox, 0, 1)

        self.gaps_slider = QSlider(Qt.Orientation.Horizontal)
        self.gaps_slider.setMinimum(0)
        self.gaps_slider.setMaximum(256)
        self.gaps_slider.setValue(4)
        self.gaps_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.gaps_slider.setTickInterval(16)
        self.gaps_slider.valueChanged.connect(self._on_gaps_slider_changed)
        gaps_layout.addWidget(self.gaps_slider, 0, 2)

        self.gaps_error = QLabel("")
        self.gaps_error.setStyleSheet("color: red;")
        gaps_layout.addWidget(self.gaps_error, 1, 1, 1, 2)

        gaps_group.setLayout(gaps_layout)
        main_layout.addWidget(gaps_group)

        # Center focused column section
        center_group = QGroupBox("Center Focused Column")
        center_layout = QGridLayout()

        center_layout.addWidget(QLabel("Behavior:"), 0, 0)

        self.center_combo = QComboBox()
        self.center_combo.addItems(["never", "always", "on-overflow"])
        self.center_combo.currentTextChanged.connect(self._on_center_changed)
        center_layout.addWidget(self.center_combo, 0, 1)

        center_help = QLabel(
            '"never": Don\'t center\n'
            '"always": Always keep focused column centered\n'
            '"on-overflow": Center only when needed to fit on screen'
        )
        center_help.setStyleSheet("color: gray; font-size: 10px;")
        center_layout.addWidget(center_help, 1, 0, 1, 2)

        center_group.setLayout(center_layout)
        main_layout.addWidget(center_group)

        # Struts section
        struts_group = QGroupBox("Reserved Space (Struts)")
        struts_layout = QGridLayout()

        struts_layout.addWidget(QLabel("Top (px):"), 0, 0)
        self.struts_top_spinbox = QSpinBox()
        self.struts_top_spinbox.setMinimum(0)
        self.struts_top_spinbox.setMaximum(1024)
        self.struts_top_spinbox.valueChanged.connect(self._on_struts_changed)
        struts_layout.addWidget(self.struts_top_spinbox, 0, 1)

        struts_layout.addWidget(QLabel("Bottom (px):"), 1, 0)
        self.struts_bottom_spinbox = QSpinBox()
        self.struts_bottom_spinbox.setMinimum(0)
        self.struts_bottom_spinbox.setMaximum(1024)
        self.struts_bottom_spinbox.valueChanged.connect(self._on_struts_changed)
        struts_layout.addWidget(self.struts_bottom_spinbox, 1, 1)

        struts_layout.addWidget(QLabel("Left (px):"), 2, 0)
        self.struts_left_spinbox = QSpinBox()
        self.struts_left_spinbox.setMinimum(0)
        self.struts_left_spinbox.setMaximum(1024)
        self.struts_left_spinbox.valueChanged.connect(self._on_struts_changed)
        struts_layout.addWidget(self.struts_left_spinbox, 2, 1)

        struts_layout.addWidget(QLabel("Right (px):"), 3, 0)
        self.struts_right_spinbox = QSpinBox()
        self.struts_right_spinbox.setMinimum(0)
        self.struts_right_spinbox.setMaximum(1024)
        self.struts_right_spinbox.valueChanged.connect(self._on_struts_changed)
        struts_layout.addWidget(self.struts_right_spinbox, 3, 1)

        struts_help = QLabel(
            "Reserve screen edges for panels, taskbars, or other UI elements.\n"
            "Leave all at 0 if you don't use panels."
        )
        struts_help.setStyleSheet("color: gray; font-size: 10px;")
        struts_layout.addWidget(struts_help, 4, 0, 1, 2)

        struts_group.setLayout(struts_layout)
        main_layout.addWidget(struts_group)

        # Add stretch to push everything to the top
        main_layout.addStretch()

        self.setLayout(main_layout)

    def load_config(self, config_model: ConfigModel):
        """Load configuration into tab.

        Args:
            config_model: ConfigModel instance
        """
        self.config_model = config_model

        # Block signals while loading to avoid triggering changes
        self.gaps_spinbox.blockSignals(True)
        self.gaps_slider.blockSignals(True)
        self.center_combo.blockSignals(True)
        self.struts_top_spinbox.blockSignals(True)
        self.struts_bottom_spinbox.blockSignals(True)
        self.struts_left_spinbox.blockSignals(True)
        self.struts_right_spinbox.blockSignals(True)

        # Load values
        self.gaps_spinbox.setValue(config_model.layout.gaps)
        self.gaps_slider.setValue(config_model.layout.gaps)
        self.center_combo.setCurrentText(config_model.layout.center_focused_column)
        self.struts_top_spinbox.setValue(config_model.layout.struts_top)
        self.struts_bottom_spinbox.setValue(config_model.layout.struts_bottom)
        self.struts_left_spinbox.setValue(config_model.layout.struts_left)
        self.struts_right_spinbox.setValue(config_model.layout.struts_right)

        # Unblock signals
        self.gaps_spinbox.blockSignals(False)
        self.gaps_slider.blockSignals(False)
        self.center_combo.blockSignals(False)
        self.struts_top_spinbox.blockSignals(False)
        self.struts_bottom_spinbox.blockSignals(False)
        self.struts_left_spinbox.blockSignals(False)
        self.struts_right_spinbox.blockSignals(False)

    def _on_gaps_changed(self, value: int):
        """Handle gaps spinbox change."""
        if not self.config_model:
            return

        valid, error = Validators.validate_gaps(value)
        if valid:
            self.gaps_error.setText("")
            self.gaps_slider.blockSignals(True)
            self.gaps_slider.setValue(value)
            self.gaps_slider.blockSignals(False)

            self.config_model.layout.gaps = value
            self.settings_changed.emit()
        else:
            self.gaps_error.setText(error)

    def _on_gaps_slider_changed(self, value: int):
        """Handle gaps slider change."""
        self.gaps_spinbox.blockSignals(True)
        self.gaps_spinbox.setValue(value)
        self.gaps_spinbox.blockSignals(False)
        self._on_gaps_changed(value)

    def _on_center_changed(self, value: str):
        """Handle center-focused-column change."""
        if not self.config_model:
            return

        valid, error = Validators.validate_center_mode(value)
        if valid:
            self.config_model.layout.center_focused_column = value
            self.settings_changed.emit()

    def _on_struts_changed(self):
        """Handle struts change."""
        if not self.config_model:
            return

        # Validate all strut values
        for spinbox, attr in [
            (self.struts_top_spinbox, 'struts_top'),
            (self.struts_bottom_spinbox, 'struts_bottom'),
            (self.struts_left_spinbox, 'struts_left'),
            (self.struts_right_spinbox, 'struts_right'),
        ]:
            valid, _ = Validators.validate_strut(spinbox.value())
            if not valid:
                return

        # Update model
        self.config_model.layout.struts_top = self.struts_top_spinbox.value()
        self.config_model.layout.struts_bottom = self.struts_bottom_spinbox.value()
        self.config_model.layout.struts_left = self.struts_left_spinbox.value()
        self.config_model.layout.struts_right = self.struts_right_spinbox.value()

        self.settings_changed.emit()

"""Opacity rules tab for managing window transparency settings."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QDoubleSpinBox, QGroupBox,
    QGridLayout, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from ...models.config_model import ConfigModel
from ...models.window_rule import WindowRule, RuleMatch
from ...core.validators import Validators


class OpacityTab(QWidget):
    """Tab for managing window opacity rules."""

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize opacity tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_model = None
        self.opacity_rules = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the tab UI."""
        main_layout = QVBoxLayout()

        # Description
        desc = QLabel(
            "Define opacity (transparency) rules for windows based on their state.\n"
            "Common use case: dim unfocused windows to highlight the active window."
        )
        desc.setStyleSheet("color: gray; font-size: 10px;")
        main_layout.addWidget(desc)

        # Rules list section
        rules_group = QGroupBox("Opacity Rules")
        rules_layout = QVBoxLayout()

        self.rules_list = QListWidget()
        self.rules_list.itemSelectionChanged.connect(self._on_rule_selected)
        rules_layout.addWidget(QLabel("Configured rules:"))
        rules_layout.addWidget(self.rules_list)

        # Rule control buttons
        rule_button_layout = QHBoxLayout()

        self.add_rule_button = QPushButton("Add Rule")
        self.add_rule_button.clicked.connect(self._on_add_rule)
        rule_button_layout.addWidget(self.add_rule_button)

        self.remove_rule_button = QPushButton("Remove Rule")
        self.remove_rule_button.clicked.connect(self._on_remove_rule)
        self.remove_rule_button.setEnabled(False)
        rule_button_layout.addWidget(self.remove_rule_button)

        rule_button_layout.addStretch()
        rules_layout.addLayout(rule_button_layout)

        rules_group.setLayout(rules_layout)
        main_layout.addWidget(rules_group)

        # Quick presets section
        presets_group = QGroupBox("Quick Presets")
        presets_layout = QGridLayout()

        presets_layout.addWidget(QLabel("Unfocused windows opacity:"), 0, 0)

        self.unfocused_spinbox = QDoubleSpinBox()
        self.unfocused_spinbox.setMinimum(0.0)
        self.unfocused_spinbox.setMaximum(1.0)
        self.unfocused_spinbox.setSingleStep(0.05)
        self.unfocused_spinbox.setValue(0.85)
        presets_layout.addWidget(self.unfocused_spinbox, 0, 1)

        self.apply_unfocused_button = QPushButton("Apply")
        self.apply_unfocused_button.clicked.connect(self._on_apply_unfocused)
        presets_layout.addWidget(self.apply_unfocused_button, 0, 2)

        presets_help = QLabel(
            "This preset creates a rule that dims (reduces opacity of) unfocused windows.\n"
            "1.0 = fully opaque (normal), 0.5 = 50% transparent (dimmed)"
        )
        presets_help.setStyleSheet("color: gray; font-size: 10px;")
        presets_layout.addWidget(presets_help, 1, 0, 1, 3)

        presets_group.setLayout(presets_layout)
        main_layout.addWidget(presets_group)

        # Add stretch
        main_layout.addStretch()

        self.setLayout(main_layout)

    def load_config(self, config_model: ConfigModel):
        """Load configuration into tab.

        Args:
            config_model: ConfigModel instance
        """
        self.config_model = config_model
        self._refresh_rules_list()

    def _refresh_rules_list(self):
        """Refresh the opacity rules list display."""
        self.rules_list.clear()
        self.opacity_rules = []

        if not self.config_model:
            return

        # Find opacity-related rules
        for rule in self.config_model.window_rules:
            if rule.opacity is not None and len(rule.matches) > 0:
                self.opacity_rules.append(rule)

                # Display rule
                desc = self._get_rule_description(rule)
                item = QListWidgetItem(desc)
                item.setData(Qt.ItemDataRole.UserRole, len(self.opacity_rules) - 1)
                self.rules_list.addItem(item)

    def _get_rule_description(self, rule: WindowRule) -> str:
        """Get human-readable description of opacity rule.

        Args:
            rule: WindowRule instance

        Returns:
            Description string
        """
        # Build match description
        match_parts = []
        for match in rule.matches:
            if match.condition_type == "is-focused":
                match_parts.append(f"Focused={match.value}")
            elif match.condition_type == "app-id":
                match_parts.append(f"App: {match.value}")
            elif match.condition_type == "title":
                match_parts.append(f"Title: {match.value}")

        match_str = ", ".join(match_parts) if match_parts else "Any window"

        # Opacity
        opacity_str = f"Opacity: {rule.opacity:.2f}"

        return f"{match_str} → {opacity_str}"

    def _on_rule_selected(self):
        """Handle rule list selection."""
        self.remove_rule_button.setEnabled(self.rules_list.currentRow() >= 0)

    def _on_add_rule(self):
        """Handle add rule button click."""
        # Create a simple unfocused rule
        rule = WindowRule()
        rule.matches.append(RuleMatch("is-focused", "false"))
        rule.opacity = 0.85

        if self.config_model:
            self.config_model.window_rules.append(rule)
            self._refresh_rules_list()
            self.settings_changed.emit()

    def _on_remove_rule(self):
        """Handle remove rule button click."""
        current_row = self.rules_list.currentRow()
        if current_row < 0:
            return

        rule_index = self.rules_list.item(current_row).data(Qt.ItemDataRole.UserRole)

        if self.config_model:
            # Find and remove the rule
            opacity_rule_count = 0
            for i, rule in enumerate(self.config_model.window_rules):
                if rule.opacity is not None and len(rule.matches) > 0:
                    if opacity_rule_count == rule_index:
                        self.config_model.window_rules.pop(i)
                        break
                    opacity_rule_count += 1

            self._refresh_rules_list()
            self.settings_changed.emit()

    def _on_apply_unfocused(self):
        """Handle apply unfocused preset button."""
        if not self.config_model:
            return

        opacity = self.unfocused_spinbox.value()

        # Validate
        valid, error = Validators.validate_opacity(opacity)
        if not valid:
            QMessageBox.warning(self, "Invalid Value", error)
            return

        # Find existing unfocused rule or create new one
        found = False
        for rule in self.config_model.window_rules:
            if (len(rule.matches) == 1 and
                rule.matches[0].condition_type == "is-focused" and
                rule.matches[0].value == "false"):
                # Found existing rule
                rule.opacity = opacity
                found = True
                break

        if not found:
            # Create new rule
            rule = WindowRule()
            rule.matches.append(RuleMatch("is-focused", "false"))
            rule.opacity = opacity
            self.config_model.window_rules.append(rule)

        self._refresh_rules_list()
        self.settings_changed.emit()

        QMessageBox.information(
            self,
            "Rule Applied",
            f"Unfocused windows will now be {opacity:.0%} opaque."
        )

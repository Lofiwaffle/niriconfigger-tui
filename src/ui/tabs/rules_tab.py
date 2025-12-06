"""Window rules tab for advanced window rule management."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QGroupBox, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from ...models.config_model import ConfigModel
from ...models.window_rule import WindowRule, RuleMatch, get_template_list, get_rule_template
from ...ui.widgets.rule_editor import RuleEditorDialog


class RulesTab(QWidget):
    """Tab for managing window rules."""

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize rules tab.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_model = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the tab UI."""
        main_layout = QVBoxLayout()

        # Description
        desc = QLabel(
            "Create window rules to apply settings to specific applications.\n"
            "Rules can match by app ID, window title, and focus state, then apply properties like floating, geometry, etc."
        )
        desc.setStyleSheet("color: gray; font-size: 10px;")
        main_layout.addWidget(desc)

        # Rules list section
        rules_group = QGroupBox("Window Rules")
        rules_layout = QVBoxLayout()

        self.rules_list = QListWidget()
        self.rules_list.itemSelectionChanged.connect(self._on_rule_selected)
        self.rules_list.itemDoubleClicked.connect(self._on_edit_rule)
        rules_layout.addWidget(QLabel("Rules (double-click to edit):"))
        rules_layout.addWidget(self.rules_list)

        # Rule control buttons
        rule_button_layout = QHBoxLayout()

        self.add_rule_button = QPushButton("New Rule")
        self.add_rule_button.clicked.connect(self._on_add_rule)
        rule_button_layout.addWidget(self.add_rule_button)

        self.edit_rule_button = QPushButton("Edit")
        self.edit_rule_button.clicked.connect(self._on_edit_rule)
        self.edit_rule_button.setEnabled(False)
        rule_button_layout.addWidget(self.edit_rule_button)

        self.remove_rule_button = QPushButton("Remove")
        self.remove_rule_button.clicked.connect(self._on_remove_rule)
        self.remove_rule_button.setEnabled(False)
        rule_button_layout.addWidget(self.remove_rule_button)

        self.duplicate_rule_button = QPushButton("Duplicate")
        self.duplicate_rule_button.clicked.connect(self._on_duplicate_rule)
        self.duplicate_rule_button.setEnabled(False)
        rule_button_layout.addWidget(self.duplicate_rule_button)

        rule_button_layout.addStretch()
        rules_layout.addLayout(rule_button_layout)

        rules_group.setLayout(rules_layout)
        main_layout.addWidget(rules_group)

        # Templates section
        templates_group = QGroupBox("Rule Templates")
        templates_layout = QHBoxLayout()

        templates_layout.addWidget(QLabel("Quick add:"))

        self.template_combo = QComboBox()
        self.template_combo.addItem("Select template...", "")

        for template_id, template_name in get_template_list():
            self.template_combo.addItem(template_name, template_id)

        templates_layout.addWidget(self.template_combo)

        self.add_template_button = QPushButton("Add Template")
        self.add_template_button.clicked.connect(self._on_add_template)
        templates_layout.addWidget(self.add_template_button)

        templates_layout.addStretch()
        templates_group.setLayout(templates_layout)
        main_layout.addWidget(templates_group)

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
        """Refresh the window rules list display."""
        self.rules_list.clear()

        if not self.config_model:
            return

        # Display all window rules
        for rule in self.config_model.window_rules:
            desc = self._get_rule_description(rule)
            item = QListWidgetItem(desc)
            item.setData(Qt.ItemDataRole.UserRole, rule)
            self.rules_list.addItem(item)

    def _get_rule_description(self, rule: WindowRule) -> str:
        """Get human-readable description of rule.

        Args:
            rule: WindowRule instance

        Returns:
            Description string
        """
        if rule.name:
            return rule.name

        # Build match description
        match_parts = []
        for match in rule.matches:
            if match.condition_type == "app-id":
                match_parts.append(f"app-id={match.value}")
            elif match.condition_type == "title":
                match_parts.append(f"title={match.value}")
            elif match.condition_type == "is-focused":
                match_parts.append(f"focused={match.value}")
            elif match.condition_type == "is-active":
                match_parts.append(f"active={match.value}")

        match_str = " AND ".join(match_parts) if match_parts else "any"

        # Build property description
        props = []
        if rule.open_floating:
            props.append("floating")
        if rule.opacity is not None:
            props.append(f"opacity={rule.opacity:.2f}")
        if rule.corner_radius is not None:
            props.append(f"radius={rule.corner_radius}px")
        if rule.block_out_from:
            props.append(f"block-out={rule.block_out_from}")
        if rule.default_column_width:
            props.append(f"width={rule.default_column_width}")

        props_str = ", ".join(props) if props else "no properties"

        return f"[{match_str}] → {props_str}"

    def _on_rule_selected(self):
        """Handle rule list selection."""
        selected = self.rules_list.currentRow() >= 0
        self.edit_rule_button.setEnabled(selected)
        self.remove_rule_button.setEnabled(selected)
        self.duplicate_rule_button.setEnabled(selected)

    def _on_add_rule(self):
        """Handle add rule button click."""
        dialog = RuleEditorDialog(parent=self)
        if dialog.exec() == dialog.Accepted:
            new_rule = dialog.get_rule()

            if self.config_model:
                self.config_model.window_rules.append(new_rule)
                self._refresh_rules_list()
                self.settings_changed.emit()

    def _on_edit_rule(self):
        """Handle edit rule button click."""
        current_row = self.rules_list.currentRow()
        if current_row < 0:
            return

        item = self.rules_list.item(current_row)
        rule = item.data(Qt.ItemDataRole.UserRole)

        dialog = RuleEditorDialog(rule=rule, parent=self)
        if dialog.exec() == dialog.Accepted:
            # Update the rule in the config model
            edited_rule = dialog.get_rule()

            if self.config_model:
                for i, r in enumerate(self.config_model.window_rules):
                    if r is rule:
                        # Copy properties from edited rule
                        r.name = edited_rule.name
                        r.matches = edited_rule.matches
                        r.opacity = edited_rule.opacity
                        r.corner_radius = edited_rule.corner_radius
                        r.open_floating = edited_rule.open_floating
                        r.block_out_from = edited_rule.block_out_from
                        r.default_column_width = edited_rule.default_column_width
                        break

                self._refresh_rules_list()
                self.settings_changed.emit()

    def _on_remove_rule(self):
        """Handle remove rule button click."""
        current_row = self.rules_list.currentRow()
        if current_row < 0:
            return

        item = self.rules_list.item(current_row)
        rule = item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Remove Rule",
            f"Are you sure you want to remove this rule?\n{self._get_rule_description(rule)}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.config_model:
                self.config_model.window_rules.remove(rule)
                self._refresh_rules_list()
                self.settings_changed.emit()

    def _on_duplicate_rule(self):
        """Handle duplicate rule button click."""
        current_row = self.rules_list.currentRow()
        if current_row < 0:
            return

        item = self.rules_list.item(current_row)
        original_rule = item.data(Qt.ItemDataRole.UserRole)

        # Create a copy
        new_rule = WindowRule()
        new_rule.name = f"{original_rule.name} (copy)" if original_rule.name else "Rule (copy)"
        new_rule.matches = [
            RuleMatch(m.condition_type, m.value, m.use_regex)
            for m in original_rule.matches
        ]
        new_rule.opacity = original_rule.opacity
        new_rule.corner_radius = original_rule.corner_radius
        new_rule.open_floating = original_rule.open_floating
        new_rule.block_out_from = original_rule.block_out_from
        new_rule.default_column_width = original_rule.default_column_width

        if self.config_model:
            self.config_model.window_rules.append(new_rule)
            self._refresh_rules_list()
            self.settings_changed.emit()

    def _on_add_template(self):
        """Handle add template button click."""
        template_id = self.template_combo.currentData()
        if not template_id:
            QMessageBox.information(self, "Select Template", "Please select a template")
            return

        template_rule = get_rule_template(template_id)
        if not template_rule:
            QMessageBox.critical(self, "Error", "Could not load template")
            return

        if self.config_model:
            self.config_model.window_rules.append(template_rule)
            self._refresh_rules_list()
            self.settings_changed.emit()

            QMessageBox.information(
                self,
                "Template Added",
                f"Template '{template_rule.name}' has been added.\n"
                "You can edit it to customize the rule."
            )

        # Reset combo
        self.template_combo.setCurrentIndex(0)

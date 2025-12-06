"""Dialog widget for editing window rules."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QCheckBox, QPushButton, QGroupBox, QGridLayout, QListWidget,
    QListWidgetItem, QSpinBox, QMessageBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt

from ...models.window_rule import WindowRule, RuleMatch, get_template_list
from ...ui.widgets.color_picker import ColorPicker


class RuleEditorDialog(QDialog):
    """Dialog for editing window rules."""

    def __init__(self, rule: WindowRule = None, parent=None):
        """Initialize rule editor dialog.

        Args:
            rule: WindowRule to edit (None for new rule)
            parent: Parent widget
        """
        super().__init__(parent)
        self.rule = rule if rule else WindowRule()
        self.edited_rule = WindowRule()

        self.setWindowTitle("Edit Window Rule")
        self.setGeometry(100, 100, 700, 600)

        self._setup_ui()
        self._load_rule()

    def _setup_ui(self):
        """Setup the dialog UI."""
        main_layout = QVBoxLayout()

        # Rule name section
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Rule Name (optional):"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Firefox Picture-in-Picture")
        name_layout.addWidget(self.name_input)
        main_layout.addLayout(name_layout)

        # Match conditions section
        match_group = QGroupBox("Match Conditions (all must match)")
        match_layout = QVBoxLayout()

        # Match list
        self.match_list = QListWidget()
        self.match_list.itemSelectionChanged.connect(self._on_match_selected)
        match_layout.addWidget(QLabel("Conditions:"))
        match_layout.addWidget(self.match_list)

        # Add match controls
        add_match_layout = QHBoxLayout()

        add_match_layout.addWidget(QLabel("Add condition:"))
        self.condition_combo = QComboBox()
        self.condition_combo.addItems(["app-id", "title", "is-focused", "is-active"])
        add_match_layout.addWidget(self.condition_combo)

        self.match_value_input = QLineEdit()
        self.match_value_input.setPlaceholderText("Value (regex for app-id/title)")
        add_match_layout.addWidget(self.match_value_input)

        self.match_regex_check = QCheckBox("Regex")
        add_match_layout.addWidget(self.match_regex_check)

        self.add_match_button = QPushButton("Add")
        self.add_match_button.clicked.connect(self._on_add_match)
        add_match_layout.addWidget(self.add_match_button)

        match_layout.addLayout(add_match_layout)

        # Remove match button
        self.remove_match_button = QPushButton("Remove Selected Match")
        self.remove_match_button.clicked.connect(self._on_remove_match)
        self.remove_match_button.setEnabled(False)
        match_layout.addWidget(self.remove_match_button)

        match_group.setLayout(match_layout)
        main_layout.addWidget(match_group)

        # Properties section
        props_group = QGroupBox("Properties (at least one required)")
        props_layout = QGridLayout()

        # Opacity
        props_layout.addWidget(QLabel("Opacity:"), 0, 0)
        self.opacity_check = QCheckBox("Set opacity")
        self.opacity_check.stateChanged.connect(self._on_opacity_toggled)
        props_layout.addWidget(self.opacity_check, 0, 1)

        self.opacity_spinbox = QDoubleSpinBox()
        self.opacity_spinbox.setMinimum(0.0)
        self.opacity_spinbox.setMaximum(1.0)
        self.opacity_spinbox.setSingleStep(0.05)
        self.opacity_spinbox.setValue(0.85)
        self.opacity_spinbox.setEnabled(False)
        props_layout.addWidget(self.opacity_spinbox, 0, 2)

        # Corner radius
        props_layout.addWidget(QLabel("Corner radius:"), 1, 0)
        self.corner_check = QCheckBox("Set corner radius")
        self.corner_check.stateChanged.connect(self._on_corner_toggled)
        props_layout.addWidget(self.corner_check, 1, 1)

        self.corner_spinbox = QSpinBox()
        self.corner_spinbox.setMinimum(0)
        self.corner_spinbox.setMaximum(256)
        self.corner_spinbox.setValue(16)
        self.corner_spinbox.setEnabled(False)
        props_layout.addWidget(self.corner_spinbox, 1, 2)

        # Floating
        props_layout.addWidget(QLabel("Behavior:"), 2, 0)
        self.floating_check = QCheckBox("Open as floating window")
        props_layout.addWidget(self.floating_check, 2, 1, 1, 2)

        # Block out
        props_layout.addWidget(QLabel("Block from:"), 3, 0)
        self.blockout_check = QCheckBox("Enable block-out")
        self.blockout_check.stateChanged.connect(self._on_blockout_toggled)
        props_layout.addWidget(self.blockout_check, 3, 1)

        self.blockout_combo = QComboBox()
        self.blockout_combo.addItems(["screen-capture", "screencast"])
        self.blockout_combo.setEnabled(False)
        props_layout.addWidget(self.blockout_combo, 3, 2)

        # Column width
        props_layout.addWidget(QLabel("Column width:"), 4, 0)
        self.colwidth_check = QCheckBox("Set default width")
        self.colwidth_check.stateChanged.connect(self._on_colwidth_toggled)
        props_layout.addWidget(self.colwidth_check, 4, 1)

        self.colwidth_type = QComboBox()
        self.colwidth_type.addItems(["proportion", "fixed"])
        self.colwidth_type.setEnabled(False)
        props_layout.addWidget(self.colwidth_type, 4, 2)

        self.colwidth_value = QDoubleSpinBox()
        self.colwidth_value.setMinimum(0.0)
        self.colwidth_value.setMaximum(1.0)
        self.colwidth_value.setSingleStep(0.1)
        self.colwidth_value.setValue(0.5)
        self.colwidth_value.setEnabled(False)
        props_layout.addWidget(self.colwidth_value, 5, 2)

        props_group.setLayout(props_layout)
        main_layout.addWidget(props_group)

        # Buttons
        button_layout = QHBoxLayout()

        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _load_rule(self):
        """Load rule data into UI."""
        # Load name
        self.name_input.setText(self.rule.name)

        # Load matches
        for match in self.rule.matches:
            self._add_match_to_list(match)

        # Load properties
        if self.rule.opacity is not None:
            self.opacity_check.setChecked(True)
            self.opacity_spinbox.setValue(self.rule.opacity)

        if self.rule.corner_radius is not None:
            self.corner_check.setChecked(True)
            self.corner_spinbox.setValue(self.rule.corner_radius)

        if self.rule.open_floating:
            self.floating_check.setChecked(True)

        if self.rule.block_out_from:
            self.blockout_check.setChecked(True)
            self.blockout_combo.setCurrentText(self.rule.block_out_from)

        if self.rule.default_column_width:
            self.colwidth_check.setChecked(True)
            if self.rule.default_column_width.startswith("proportion:"):
                self.colwidth_type.setCurrentText("proportion")
                value = float(self.rule.default_column_width.split(":")[1])
                self.colwidth_value.setValue(value)
            elif self.rule.default_column_width.startswith("fixed:"):
                self.colwidth_type.setCurrentText("fixed")
                value = float(self.rule.default_column_width.split(":")[1])
                self.colwidth_value.setValue(value)

    def _add_match_to_list(self, match: RuleMatch):
        """Add a match condition to the list widget.

        Args:
            match: RuleMatch instance
        """
        item_text = match.to_kdl()
        if match.use_regex:
            item_text += " (regex)"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, match)
        self.match_list.addItem(item)

    def _on_add_match(self):
        """Handle add match button click."""
        condition = self.condition_combo.currentText()
        value = self.match_value_input.text().strip()

        if not value:
            QMessageBox.warning(self, "Input Error", "Please enter a value for the match condition")
            return

        # For boolean conditions, validate value
        if condition in ["is-focused", "is-active"]:
            if value not in ["true", "false"]:
                QMessageBox.warning(self, "Input Error", f"{condition} must be 'true' or 'false'")
                return

        use_regex = self.match_regex_check.isChecked()
        match = RuleMatch(condition, value, use_regex)

        self._add_match_to_list(match)
        self.match_value_input.clear()
        self.match_regex_check.setChecked(False)

    def _on_remove_match(self):
        """Handle remove match button click."""
        current_row = self.match_list.currentRow()
        if current_row >= 0:
            self.match_list.takeItem(current_row)

    def _on_match_selected(self):
        """Handle match list selection."""
        self.remove_match_button.setEnabled(self.match_list.currentRow() >= 0)

    def _on_opacity_toggled(self):
        """Handle opacity checkbox toggle."""
        self.opacity_spinbox.setEnabled(self.opacity_check.isChecked())

    def _on_corner_toggled(self):
        """Handle corner radius checkbox toggle."""
        self.corner_spinbox.setEnabled(self.corner_check.isChecked())

    def _on_blockout_toggled(self):
        """Handle block-out checkbox toggle."""
        self.blockout_combo.setEnabled(self.blockout_check.isChecked())

    def _on_colwidth_toggled(self):
        """Handle column width checkbox toggle."""
        enabled = self.colwidth_check.isChecked()
        self.colwidth_type.setEnabled(enabled)
        self.colwidth_value.setEnabled(enabled)

    def _on_ok(self):
        """Handle OK button click."""
        # Validate: at least one match
        if self.match_list.count() == 0:
            QMessageBox.warning(self, "Validation Error", "Please add at least one match condition")
            return

        # Validate: at least one property
        has_property = (
            self.opacity_check.isChecked() or
            self.corner_check.isChecked() or
            self.floating_check.isChecked() or
            self.blockout_check.isChecked() or
            self.colwidth_check.isChecked()
        )

        if not has_property:
            QMessageBox.warning(self, "Validation Error", "Please set at least one property")
            return

        # Build edited rule
        self.edited_rule.name = self.name_input.text()

        # Add matches
        for i in range(self.match_list.count()):
            item = self.match_list.item(i)
            match = item.data(Qt.ItemDataRole.UserRole)
            self.edited_rule.matches.append(match)

        # Add properties
        if self.opacity_check.isChecked():
            self.edited_rule.opacity = self.opacity_spinbox.value()

        if self.corner_check.isChecked():
            self.edited_rule.corner_radius = self.corner_spinbox.value()

        if self.floating_check.isChecked():
            self.edited_rule.open_floating = True

        if self.blockout_check.isChecked():
            self.edited_rule.block_out_from = self.blockout_combo.currentText()

        if self.colwidth_check.isChecked():
            col_type = self.colwidth_type.currentText()
            value = self.colwidth_value.value()
            if col_type == "proportion":
                self.edited_rule.default_column_width = f"proportion:{value}"
            else:
                self.edited_rule.default_column_width = f"fixed:{int(value)}"

        self.accept()

    def get_rule(self) -> WindowRule:
        """Get the edited rule.

        Returns:
            WindowRule instance
        """
        return self.edited_rule

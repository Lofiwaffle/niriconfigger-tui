# NiriConfig GUI

A comprehensive graphical configuration manager for the **Niri Wayland compositor**. Easily customize window decoration, layout settings, opacity rules, and advanced window matching rules through an intuitive tabbed interface.

## Features

### 🎨 Visual Settings
- **Corner Radius**: Adjust window corner roundness (0-256px)
- **Focus Ring**: Customize focus indicators with color and width controls
- **Border Configuration**: Enable/disable borders with active/inactive/urgent color states
- **Shadow Effects**: Control shadow softness, spread, offset, and color
- **Clip to Geometry**: Ensure window content respects rounded corners

### 📐 Layout Settings
- **Window Gaps**: Control spacing between windows (0-256px)
- **Struts**: Reserve screen edges for panels/taskbars
- **Center Focused Column**: Keep focused windows centered ("never", "always", "on-overflow")

### 🎯 Opacity Rules
- **Quick Presets**: One-click dimming for unfocused windows
- **Custom Rules**: Create opacity rules based on window focus state
- **Live Preview**: See changes immediately

### 🔧 Advanced Window Rules
- **Smart Matching**: Match windows by app-id, title, focus state with regex support
- **Property Configuration**: Set floating behavior, geometry, opacity, and more
- **Rule Templates**: Pre-built templates for Firefox PiP, Steam, Modal Dialogs, Terminals
- **Rule Management**: Create, edit, duplicate, and remove rules easily

### 💾 Configuration Management
- **Non-destructive Editing**: Preserves all comments and formatting in config files
- **Automatic Backups**: Timestamped backups before each modification
- **Smart Reloading**: Apply changes to Niri without restarting
- **Rollback Support**: Automatic restoration on configuration reload failure

## Installation

### Requirements
- Python 3.10+
- Niri Wayland compositor
- PyQt6 (`sudo pacman -S python-pyqt6` on Arch Linux)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/niriconfigger-tui.git
   cd niriconfigger-tui
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python3 -m src.main
   ```

### System-wide Installation

```bash
pip install -e .
niri-config-gui
```

## Usage

### Launching the GUI

The application reads your current Niri configuration from `~/.config/niri/config.kdl` and displays all settings in a tabbed interface.

```bash
cd /path/to/niriconfigger-tui
source venv/bin/activate
python3 -m src.main
```

### Tabs Overview

#### 1. Layout Tab
Configure window layout behavior:
- **Gaps**: Spacing between tiled windows
- **Struts**: Reserved space for panels
- **Center Focused Column**: Behavior for centering the active column

#### 2. Visual Tab
Customize window appearance:
- **Corner Radius**: Rounded window corners with clip-to-geometry
- **Focus Ring**: Visual indicator for focused windows
- **Border**: Optional window borders with color states
- **Shadow**: Drop shadow effects with offset and blur control

#### 3. Opacity Tab
Manage window transparency:
- **Quick Preset**: Set opacity for unfocused windows
- **Custom Rules**: Create fine-grained opacity rules
- **Live Management**: Add/remove rules on the fly

#### 4. Rules Tab
Advanced window-specific configuration:
- **New Rule**: Create custom rules with full control
- **Templates**: Quick-add pre-built templates
- **Edit/Duplicate**: Modify or copy existing rules
- **Matching**: Match by app-id (regex), title (regex), focus state, etc.
- **Properties**: Set floating, opacity, geometry, and more

### Workflow

1. **Modify Settings**: Adjust any setting in the tabs
2. **Preview**: Settings are immediately reflected in the UI
3. **Save**: Click "Save" to write to `config.kdl` (no reload)
4. **Apply**: Click "Apply" to save AND reload Niri configuration
5. **Revert**: Click "Revert" to discard unsaved changes

### Safe Modifications

- **Automatic Backups**: Every save creates a timestamped backup in `~/.config/niri/backups/`
- **Non-destructive**: All comments and formatting preserved
- **Rollback**: If reload fails, automatically restore previous config

## Configuration Files

### Niri Config Location
- **Main config**: `~/.config/niri/config.kdl`
- **Backups**: `~/.config/niri/backups/config-YYYYMMDD-HHMMSS.kdl`

### Application Config
- **Settings**: `~/.config/niri-config-gui/settings.json` (future use)

## Window Rule Examples

### Firefox Picture-in-Picture
```kdl
window-rule {
    match app-id=r#"firefox$"#
    match title="Picture-in-Picture"
    open-floating true
}
```

### Dim Unfocused Windows
```kdl
window-rule {
    match is-focused=false
    opacity 0.85
}
```

### Floating Modal Dialogs
```kdl
window-rule {
    match title=r#"dialog|modal|settings"#
    open-floating true
}
```

### Terminal with Custom Width
```kdl
window-rule {
    match app-id=r#"kitty|wezterm|ghostty"#
    default-column-width { proportion 0.5; }
}
```

## Architecture

### Project Structure
```
src/
├── main.py                     # Entry point
├── core/
│   ├── config_manager.py       # KDL file I/O with preservation
│   ├── validators.py           # Input validation
│   ├── niri_interface.py       # Niri subprocess control
│   └── backup_manager.py       # Backup/restore system
├── models/
│   ├── config_model.py         # Configuration data structures
│   ├── color.py                # Color format handling
│   └── window_rule.py          # Rule models and matching logic
└── ui/
    ├── main_window.py          # Main application window
    ├── tabs/
    │   ├── layout_tab.py       # Layout settings
    │   ├── visual_tab.py       # Visual settings
    │   ├── opacity_tab.py      # Opacity rules
    │   └── rules_tab.py        # Window rules
    └── widgets/
        ├── color_picker.py     # Color selection widget
        └── rule_editor.py      # Rule creation/editing dialog
```

### Key Design Principles

1. **Comment Preservation**: Uses regex-based line replacement instead of full KDL rewrites
2. **Separation of Concerns**: Config I/O, validation, UI, and Niri communication are separate
3. **Modular Tabs**: Each settings category in its own tab module
4. **Extensibility**: Rule system designed for adding new match conditions and properties

## Testing

Run the comprehensive test suite:

```bash
source venv/bin/activate

# Phase 1: Configuration I/O
python3 test_phase1.py

# Phase 2: Visual Settings
python3 test_phase2.py

# Phase 3: Rules and Advanced Features
python3 test_phase3.py
```

### Test Coverage
- ✓ Configuration loading with comment preservation
- ✓ Settings modification and saving
- ✓ Color format handling (hex, rgb, rgba, named colors)
- ✓ Visual settings (gaps, corner radius, focus ring, borders, shadows)
- ✓ Window rule creation, matching, and KDL generation
- ✓ Rule templates and quick presets
- ✓ Input validation (16/17 tests passing)

## Troubleshooting

### Configuration Won't Save
1. Check that `~/.config/niri/` directory exists
2. Ensure you have write permissions: `ls -la ~/.config/niri/`
3. Check error message in the application dialog

### Niri Won't Reload
1. Verify Niri is running: `hyprctl version` (or `niri msg version`)
2. Check Niri logs: `journalctl -u niri` (if systemd service)
3. Try manual reload: `niri msg action load-config-file`

### Invalid Configuration Error
1. The application validates input before saving
2. Check for syntax errors in window rules (especially regex patterns)
3. Use the backup restore feature to revert to last known good config

## Contributing

Contributions welcome! Areas for enhancement:
- Additional rule templates
- Color scheme presets
- Theme management
- Animation settings editor
- Keybinding editor

## License

MIT License - See LICENSE file for details

## Credits

Built for the **Niri** Wayland compositor: https://github.com/YaLTeR/niri

## Related Projects

- **Niri**: Modern Wayland compositor - https://github.com/YaLTeR/niri
- **Hyprland**: Alternative Wayland compositor with GUI tools
- **KDL**: Configuration language - https://kdl.dev

## Support

For issues, feature requests, or questions:
1. Check existing [GitHub Issues](https://github.com/yourusername/niriconfigger-tui/issues)
2. Create a new issue with detailed description
3. Include your Niri version and configuration snippet

---

**NiriConfig GUI** - Making Niri configuration simple and intuitive.

"""Main entry point for NiriConfig GUI application."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def main():
    """Run the application."""
    app = QApplication(sys.argv)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

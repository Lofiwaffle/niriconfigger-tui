"""Interface to Niri compositor via subprocess commands."""

import subprocess
from typing import Tuple


class NiriInterface:
    """Interface to Niri compositor."""

    def __init__(self):
        """Initialize Niri interface."""
        self.niri_command = "niri"

    def reload_config(self) -> Tuple[bool, str]:
        """Reload Niri configuration.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            result = subprocess.run(
                [self.niri_command, "msg", "action", "load-config-file"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return True, "Configuration reloaded successfully"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                return False, f"Niri reload failed: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Reload timed out after 5 seconds (Niri may be unresponsive)"
        except FileNotFoundError:
            return False, "Niri not found - is it installed and running?"
        except Exception as e:
            return False, f"Unexpected error during reload: {str(e)}"

    def get_version(self) -> Tuple[bool, str]:
        """Get Niri version.

        Returns:
            Tuple of (success: bool, version: str)
        """
        try:
            result = subprocess.run(
                [self.niri_command, "msg", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, "Failed to get version"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_monitors(self) -> Tuple[bool, str]:
        """Get list of connected monitors.

        Returns:
            Tuple of (success: bool, output: str)
        """
        try:
            result = subprocess.run(
                [self.niri_command, "msg", "monitor-layout"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, "Failed to get monitor layout"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def is_running(self) -> bool:
        """Check if Niri is currently running.

        Returns:
            True if Niri is running
        """
        try:
            result = subprocess.run(
                [self.niri_command, "msg", "version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

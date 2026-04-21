"""Windows startup integration."""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

from core.constants import ROOT_DIR

try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    winreg = None
    WINREG_AVAILABLE = False

RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE_NAME = "AtlasXCursorStudio"


class StartupManager:
    """Controls Windows startup registration."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def get_registered_command(self) -> str | None:
        if not WINREG_AVAILABLE or winreg is None:
            return None
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, RUN_VALUE_NAME)
        except (FileNotFoundError, OSError):
            return None
        if not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None

    def is_enabled(self) -> bool:
        return self.get_registered_command() is not None

    def is_registered_for_current_install(self) -> bool:
        registered = self.get_registered_command()
        if registered is None:
            return False
        return self._normalize_command(registered) == self._normalize_command(self._build_launch_command())

    def set_enabled(self, enabled: bool) -> bool:
        if not WINREG_AVAILABLE or winreg is None:
            self.logger.warning("winreg is unavailable, startup registration is unsupported")
            return False
        try:
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    winreg.SetValueEx(key, RUN_VALUE_NAME, 0, winreg.REG_SZ, self._build_launch_command())
                else:
                    try:
                        winreg.DeleteValue(key, RUN_VALUE_NAME)
                    except FileNotFoundError:
                        pass
            self.logger.info("Startup registration updated: %s", enabled)
            return True
        except OSError as exc:
            self.logger.exception("Failed to update startup registration: %s", exc)
            return False

    def repair_if_needed(self, desired_enabled: bool) -> bool:
        """Keep startup registration aligned with the current install and user config."""
        if desired_enabled:
            if self.is_registered_for_current_install():
                return True
            return self.set_enabled(True)
        if self.get_registered_command() is None:
            return True
        return self.set_enabled(False)

    def _build_launch_command(self) -> str:
        if getattr(sys, "frozen", False):
            return f'"{Path(sys.executable)}" --startup'
        packaged_exe = ROOT_DIR / "dist" / "AtlasXCursorStudio" / "AtlasXCursorStudio.exe"
        if packaged_exe.exists():
            return f'"{packaged_exe}" --startup'
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        interpreter = pythonw if pythonw.exists() else Path(sys.executable)
        return f'"{interpreter}" -m app.main --startup'

    def _normalize_command(self, command: str) -> str:
        compact = re.sub(r"\s+", " ", command.strip())
        return compact.casefold()

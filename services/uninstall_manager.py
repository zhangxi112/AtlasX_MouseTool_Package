"""Installed-app uninstall integration."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path


class UninstallManager:
    """Resolves and launches the bundled uninstaller when available."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def get_uninstaller_path(self) -> Path | None:
        candidates: list[Path] = []
        if getattr(sys, "frozen", False):
            exe_dir = Path(sys.executable).resolve().parent
            candidates.extend(sorted(exe_dir.glob('unins*.exe')))
            local_appdata = os.environ.get("LOCALAPPDATA")
            if local_appdata:
                candidates.extend(sorted((Path(local_appdata) / 'Programs').glob('Atlas-X Cursor Studio/unins*.exe')))
        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate
        return None

    def is_available(self) -> bool:
        return self.get_uninstaller_path() is not None

    def launch(self) -> bool:
        uninstaller = self.get_uninstaller_path()
        if uninstaller is None:
            self.logger.warning('Uninstaller is unavailable in the current runtime layout')
            return False
        try:
            subprocess.Popen([str(uninstaller)], cwd=str(uninstaller.parent))
            self.logger.info('Launched uninstaller: %s', uninstaller)
            return True
        except OSError as exc:
            self.logger.exception('Failed to launch uninstaller: %s', exc)
            return False

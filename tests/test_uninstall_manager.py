from pathlib import Path
from unittest.mock import patch
import shutil
import uuid

from services.uninstall_manager import UninstallManager


def _make_case_dir(name: str) -> Path:
    root = Path(r"D:\AtlasX_MouseTool_Package\tests\runtime_tmp") / f"{name}_{uuid.uuid4().hex}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_uninstall_manager_detects_sibling_uninstaller() -> None:
    case_dir = _make_case_dir("installed")
    try:
        exe_dir = case_dir / "app"
        exe_dir.mkdir()
        app_exe = exe_dir / "AtlasXCursorStudio.exe"
        app_exe.write_text("stub", encoding="utf-8")
        uninstaller = exe_dir / "unins000.exe"
        uninstaller.write_text("stub", encoding="utf-8")
        manager = UninstallManager()
        with patch('services.uninstall_manager.sys', frozen=True, executable=str(app_exe)):
            assert manager.get_uninstaller_path() == uninstaller
    finally:
        shutil.rmtree(case_dir, ignore_errors=True)


def test_uninstall_manager_returns_none_when_unavailable() -> None:
    case_dir = _make_case_dir("portable")
    try:
        exe_dir = case_dir / "app"
        exe_dir.mkdir()
        app_exe = exe_dir / "AtlasXCursorStudio.exe"
        app_exe.write_text("stub", encoding="utf-8")
        manager = UninstallManager()
        with patch('services.uninstall_manager.sys', frozen=True, executable=str(app_exe)):
            assert manager.get_uninstaller_path() is None
    finally:
        shutil.rmtree(case_dir, ignore_errors=True)

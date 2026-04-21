from services.startup_manager import StartupManager


def test_startup_manager_builds_launch_command() -> None:
    manager = StartupManager()
    command = manager._build_launch_command()
    assert '--startup' in command
    assert 'app.main' in command or 'pythonw.exe' in command or 'AtlasXCursorStudio.exe' in command


def test_startup_manager_treats_blank_registry_value_as_disabled(monkeypatch) -> None:
    manager = StartupManager()
    monkeypatch.setattr(manager, 'get_registered_command', lambda: None)
    assert manager.is_enabled() is False


def test_startup_manager_detects_stale_registration(monkeypatch) -> None:
    manager = StartupManager()
    monkeypatch.setattr(manager, 'get_registered_command', lambda: '"C:/old/AtlasXCursorStudio.exe" --startup')
    monkeypatch.setattr(manager, '_build_launch_command', lambda: '"C:/new/AtlasXCursorStudio.exe" --startup')
    assert manager.is_registered_for_current_install() is False

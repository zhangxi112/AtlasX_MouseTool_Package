from services.config_manager import ConfigManager


def test_config_manager_loads_defaults() -> None:
    manager = ConfigManager()
    config = manager.load()
    assert config.highlight.duration_ms > 0
    assert config.highlight.hotkey
    assert config.click_ripple.enabled is True
    assert config.dynamic_cursor.frame_interval_ms >= 90
    assert config.game_mode.auto_disable_enhancements is True


from services.config_manager import AppConfig


def test_config_manager_sanitizes_ranges() -> None:
    manager = ConfigManager()
    config = AppConfig()
    config.pointer.cursor_size_percent = 5000
    config.pointer.shake_distance_threshold = 10
    sanitized = manager._sanitize_config(config)
    assert sanitized.pointer.cursor_size_percent == 1000
    assert sanitized.pointer.shake_distance_threshold == 80

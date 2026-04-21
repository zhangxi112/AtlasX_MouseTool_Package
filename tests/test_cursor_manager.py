from services.cursor_manager import CursorManager


def test_cursor_manager_generates_builtin_assets() -> None:
    manager = CursorManager()
    assets = manager.list_builtin_themes()
    assert len(assets) >= 10
    assert all(asset.preview_path.exists() for asset in assets)
    assert all(asset.cursor_path.exists() for asset in assets)


def test_cursor_manager_generates_animated_frames() -> None:
    manager = CursorManager()
    frame_paths = manager.get_animated_theme_frame_paths("classic_arrow")
    assert len(frame_paths) == 6
    assert all(path.exists() for path in frame_paths)


def test_cursor_manager_renders_palette_override_preview() -> None:
    manager = CursorManager()
    image = manager.get_preview_image("classic_arrow", palette_override={"primary": "#FF0000"}, scale_percent=140)
    assert image is not None
    assert image.size == (128, 128)

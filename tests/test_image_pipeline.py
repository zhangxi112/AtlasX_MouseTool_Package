from pathlib import Path

from PIL import Image

from services.cursor_manager import CursorManager
from services.image_pipeline import ImagePipeline


def test_image_pipeline_import_preview_and_cursor_generation() -> None:
    workspace = Path("configs/runtime/test_image_pipeline")
    workspace.mkdir(parents=True, exist_ok=True)
    source_path = workspace / "sample.png"
    Image.new("RGBA", (80, 60), (255, 0, 0, 255)).save(source_path)

    pipeline = ImagePipeline(storage_dir=workspace / "workspace", cursor_manager=CursorManager())
    project = pipeline.import_image(source_path)
    preview_path = pipeline.generate_preview(project, scale_percent=100, hotspot_x=32, hotspot_y=32)
    cursor_path = pipeline.generate_cursor(project, scale_percent=100, hotspot_x=32, hotspot_y=32)

    assert project.original_path.exists()
    assert preview_path.exists()
    assert cursor_path.exists()

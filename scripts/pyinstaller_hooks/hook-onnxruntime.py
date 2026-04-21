"""Custom lightweight hook for onnxruntime."""

from __future__ import annotations

import importlib.util
from pathlib import Path

spec = importlib.util.find_spec("onnxruntime")
pkg_dir = Path(spec.submodule_search_locations[0])
capi_dir = pkg_dir / "capi"

binaries = []
for file_name in (
    "onnxruntime.dll",
    "onnxruntime_providers_shared.dll",
    "onnxruntime_pybind11_state.pyd",
):
    file_path = capi_dir / file_name
    if file_path.exists():
        binaries.append((str(file_path), "onnxruntime/capi"))

excludedimports = [
    "onnxruntime.backend",
    "onnxruntime.datasets",
    "onnxruntime.experimental",
    "onnxruntime.quantization",
    "onnxruntime.tools",
    "onnxruntime.training",
    "onnxruntime.transformers",
]

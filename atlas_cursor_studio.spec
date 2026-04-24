# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path.cwd()
datas = [
    (str(project_root / "configs" / "default_config.json"), "configs"),
    (str(project_root / "assets"), "assets"),
    (str(project_root / "THIRD_PARTY_NOTICES.md"), "."),
    (str(project_root / "licenses"), "licenses"),
]

hiddenimports = [
    "onnxruntime",
    "onnxruntime.capi._pybind_state",
    "onnxruntime.capi.onnxruntime_inference_collection",
]

excludes = [
    "pytest",
    "pygame",
    "pandas",
    "matplotlib",
    "openpyxl",
    "lxml",
    "tkinter",
    "PySide6.QtWebEngineCore",
    "scipy",
    "skimage",
    "pymatting",
    "numba",
    "llvmlite",
    "rembg",
    "pooch",
    "tensorflow",
    "torch",
    "setuptools",
    "pkg_resources",
    "distutils",
    "jaraco.text",
    "jaraco.context",
    "jaraco.functools",
    "more_itertools",
    "backports.tarfile",
    "importlib_metadata",
    "wheel",
]

a = Analysis(
    ["app/main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[str(project_root / "scripts" / "pyinstaller_hooks")],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AtlasXCursorStudio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "assets" / "app_icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="AtlasXCursorStudio",
)

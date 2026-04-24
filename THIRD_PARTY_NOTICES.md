# Third-Party Notices

Software: Atlas-X Cursor Studio 鼠标指针自定义工具软件 V1.0  
Copyright holder of original project code: 张希

This file describes third-party components used by Atlas-X Cursor Studio. These components are used as runtime or build dependencies. They are not submitted as 张希's original source code for software copyright registration.

## PySide6 / Qt for Python

- Component: PySide6 / Qt for Python
- Purpose: Qt desktop user interface, windows, widgets, tray integration, dialogs, and overlay windows.
- License model: LGPLv3 / GPL / Commercial multi-license.
- Project usage: This software uses PySide6 Community Edition and follows the LGPLv3 licensing path.
- GPL path: This software does not choose the PySide6 GPL licensing path, and the project's own source code is not relicensed as GPL merely because PySide6 is used.
- Source modification: This project does not modify PySide6, Qt, Shiboken, or related component source code.
- Copyright boundary: PySide6, Qt, Shiboken, and related components are third-party components and are not part of 张希's original source code submission.

## Shiboken6

- Component: Shiboken6
- Purpose: Python binding support used with PySide6 / Qt for Python.
- License model: Follows the Qt for Python licensing model.
- Project usage: Used as a dependency of PySide6. This project does not modify Shiboken6 source code.

## Qt Runtime Libraries

- Component: Qt runtime libraries distributed with PySide6.
- Purpose: Runtime support for Qt widgets, GUI rendering, platform integration, and related desktop functions.
- License model: Follows the applicable Qt for Python / Qt component licenses.
- Project usage: Used as runtime dependencies. They are third-party components and are not original project source code.

## Other Dependencies

| Component | Purpose | License note |
|---|---|---|
| Pillow | Image loading, RGBA conversion, preview generation, and cursor image rendering | MIT-CMU/Pillow-style license; package metadata archived in `docs/dependency_metadata.txt` |
| pywin32 | Windows integration helper dependency | PSF-style license; package metadata archived in `docs/dependency_metadata.txt` |
| onnxruntime | Local ONNX inference used by the optional background removal pipeline | MIT; package metadata archived in `docs/dependency_metadata.txt` |
| numpy | Numeric dependency used by image/model processing stack | BSD-style license; binary wheels may include additional notices such as OpenBLAS/GCC runtime exception |
| PyInstaller | Build tool for Windows executable packaging | GPL with PyInstaller exception; used as a build tool, not as original application source |
| pytest | Development and test dependency | MIT-style license; package metadata archived in `docs/dependency_metadata.txt`; not required for normal end-user operation |
| Inno Setup | Windows installer build tool | Inno Setup license; used as an external packaging tool |
| Windows user32/winreg APIs | System cursor application, restore, hotkey/startup integration | Operating system APIs, not third-party source code |

## Optional U2Net Model

- Resource: `u2net.onnx`
- Purpose: Optional runtime model used only when the automatic background removal feature is triggered.
- Source in current code: `services/u2net_session.py` downloads from `https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx` and validates MD5 `60024c5c889badc19c04ad937298a77b`.
- Copyright boundary: The model file is a third-party optional runtime resource. It is not part of 张希's original source code and is not included in software copyright source identification materials.

## Project Assets

- `assets/app_icon.ico`: generated project asset for Atlas-X Cursor Studio.
- `assets/builtin_cursors/*.png` and `assets/builtin_cursors/*.cur`: treated as project-generated built-in cursor assets. The generation logic is implemented by `core/builtin_themes.py` and `services/cursor_manager.py`.
- `rendered`, `dist`, `build`, `release`, and `configs/runtime`: runtime, screenshot, test, or build output directories; they are not included in original source code identification materials.

## Release Package Notice

Release packages should include a `licenses/` directory containing LGPL/GPL license texts and Qt/PySide6 notices, plus this `THIRD_PARTY_NOTICES.md` file. If the project is later distributed under strict commercial closed-source terms, enterprise deployment, app-store distribution, or any scenario where LGPLv3 obligations cannot be satisfied, Qt for Python commercial licensing should be re-evaluated before release.

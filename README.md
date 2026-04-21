# Atlas-X Cursor Studio

Atlas-X Cursor Studio 是一个面向 Windows 的托盘常驻鼠标增强工具，用来让鼠标更容易被看见、更方便切换主题，也更适合多屏、演示和复杂桌面场景。

当前版本：`1.0`

## 它能做什么

- 一键切换和恢复系统鼠标主题
- 提供 10 套内置主题，并支持主体色、描边色、强调色、发光色分别调整
- 快捷键找回鼠标位置
- 快速晃动鼠标时显示尾迹提示
- 鼠标点击时显示波纹反馈
- 调整内置主题的全局光标大小
- 导入图片并生成可用的 `.cur` 光标
- 按前台程序自动切换主题
- 播放内置动态光标
- 全屏应用时自动暂停增强效果
- 托盘常驻、配置持久化、开机启动控制

## 下载与使用

推荐优先使用发布页中的这两种文件：

- 安装器：`AtlasXCursorStudio-Setup-1.0.exe`
- 便携版：`AtlasXCursorStudio-portable.zip`

普通用户优先下载安装器。  
如果不想安装，可以下载便携版，解压后直接运行。

## 使用前说明

- 支持系统：Windows 10 / 11
- 首次运行不需要管理员权限
- 首次使用自动抠图时，程序可能会联网下载 `u2net.onnx` 模型
- 某些全屏游戏、远程桌面或自行接管光标的程序，可能会覆盖增强效果

## 主要功能说明

### 1. 找回鼠标

可以录制一个全局快捷键，在任何时候快速高亮当前鼠标位置。

### 2. 内置主题

内置多套鼠标主题，可预览、应用、恢复默认，并且支持分别调整多种颜色层。

### 3. 自定义光标

可以导入普通图片，自动抠图、裁边、缩放并设置热点，最后生成可应用的 `.cur` 光标。

### 4. 点击与移动反馈

支持点击波纹，以及快速晃动鼠标时的尾迹提示，方便快速重新定位鼠标。

### 5. 按程序切换主题

可以根据前台进程名自动切换主题，例如：

```text
powerpnt.exe = highlight_arrow
```

### 6. 动态光标与全屏暂停

支持内置主题动态播放，并可在检测到全屏应用时自动暂停增强效果，减少干扰。

## 已知限制

- 某些程序会自行接管系统光标，可能覆盖 Atlas-X Cursor Studio 的效果
- 动态光标当前只对内置主题生效
- 自定义光标的“全局光标大小”最佳效果依赖重新生成光标文件
- 如果只分发单个 `AtlasXCursorStudio.exe`，程序无法完整运行；必须使用安装器、便携版，或整个 `dist\AtlasXCursorStudio` 目录

## 开发者说明

如果你是来查看源码、构建或二次开发，可以从这里开始。

### 环境

- Python 3.11+
- 建议使用 64 位 Python

### 安装依赖

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 源码运行

```powershell
python -m app.main
```

### 打包

```powershell
.\scripts\build.ps1
```

完整发布：

```powershell
.\scripts\build_release.ps1
```

预期产物：

- `dist\AtlasXCursorStudio\AtlasXCursorStudio.exe`
- `release\AtlasXCursorStudio-portable.zip`
- `release\AtlasXCursorStudio-Setup-1.0.exe`

### 测试

```powershell
python -m pytest tests/test_config_manager.py tests/test_cursor_manager.py tests/test_hotkey_parser.py tests/test_image_pipeline.py tests/test_startup_manager.py tests/test_enhancement_manager.py tests/test_main_window_smoke.py
python -m compileall app core services ui tests
```

### 项目结构

```text
app/
core/
services/
ui/
assets/
configs/
scripts/
tests/
docs/
```

更详细的发布检查可以看 [docs/release_guide.md](./docs/release_guide.md) 和 [docs/release_checklist.md](./docs/release_checklist.md)。

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE).

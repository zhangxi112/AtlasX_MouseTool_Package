# Atlas-X Cursor Studio

Atlas-X Cursor Studio 是一个 Windows 常驻托盘鼠标增强原型，使用 Python 3.11+、PySide6、pywin32、Pillow 和 onnxruntime 构建。它提供内置主题切换、主题分部件配色、可调分栏预览、深浅色软件主题、热键录制、全局光标大小、快速晃动鼠标尾迹提示、自定义图片转光标、点击波纹、按程序切换主题、动态光标、全屏自动暂停增强、配置持久化、托盘常驻和开机启动控制。

当前发布版本：`1.0`

## 当前完成度

已完成：
- 托盘常驻、右键菜单、双击恢复主窗口
- 10 套内置鼠标主题生成、预览、应用、恢复默认
- 内置主题主体色 / 描边色 / 强调色 / 发光色分别自定义
- 全局快捷键录制与即时应用，默认推荐 `F8`
- 快速晃动鼠标后显示尾迹式提示
- 全局点击波纹反馈
- 深色 / 浅色软件主题切换
- 主题页 / 自定义页可拖动分栏
- 数值控件默认阻止滚轮误触，需选中后才会滚轮微调
- 内置主题全局光标大小调整
- 自定义图片导入、预览、自动抠图、裁边、缩放、热点设置、`.cur` 生成与应用
- 按前台程序切换主题规则
- 内置主题动态光标播放
- 全屏应用时自动暂停增强效果
- JSON 配置保存、日志、异常保护与退出清理
- 开机启动设置代码
- PyInstaller 打包脚本、spec、发布文档

## 运行环境

- Windows 10 / 11
- Python 3.11+
- 建议使用 64 位 Python

## 安装依赖

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 启动方式

源码运行：

```powershell
python -m app.main
```

打包后运行：

```powershell
D:\AtlasX_MouseTool_Package\dist\AtlasXCursorStudio\AtlasXCursorStudio.exe
```

分享给别人时，不要只发单个 `AtlasXCursorStudio.exe`。当前发布形态是 `onedir`，必须连同整个 `dist\AtlasXCursorStudio` 目录一起分发，或者直接分发安装器 / 便携压缩包。

首次使用自动抠图时，如果本机没有 `u2net.onnx`，程序会下载到当前用户目录下的 `C:\Users\<用户名>\.u2net\u2net.onnx`。

## 发布给用户

推荐优先分发下面两类产物：

- 安装器：`release\AtlasXCursorStudio-Setup-1.0.exe`
- 便携版：`release\AtlasXCursorStudio-portable.zip`

如果用户只是正常安装使用，优先给安装器。便携版适合不想写入安装目录、只想解压即用的场景。

### 终端用户最低说明

- 首次运行不需要管理员权限。
- 首次使用自动抠图时，程序可能会联网下载 `u2net.onnx` 模型。
- 某些全屏游戏、远程桌面或自行接管光标的程序，可能会覆盖增强效果。
- 如果只发单个 `AtlasXCursorStudio.exe`，程序无法完整运行，必须改用安装器、便携压缩包，或整个 `dist\AtlasXCursorStudio` 目录。

## 目录结构

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

## 主要模块

- `services/cursor_manager.py`：系统光标应用、恢复默认、内置主题资产生成、动态帧生成
- `services/overlay_manager.py`：找回鼠标高亮、晃动尾迹、点击波纹
- `services/enhancement_manager.py`：按程序切换、动态光标、晃动检测、游戏模式与运行时协调
- `services/windows_foreground.py`：前台窗口和全屏状态检测
- `services/image_pipeline.py`：图片导入、预览、裁边、缩放、热点驱动
- `services/u2net_session.py`：本地 U2Net 抠图推理与模型下载
- `services/config_manager.py`：JSON 配置读写
- `services/tray_hotkey_manager.py`：托盘和全局快捷键
- `services/startup_manager.py`：开机启动注册表控制
- `services/logger.py`：日志初始化与运行日志目录

## 使用说明

- 首页可快速切换主题、录制快捷键并即时应用。
- 主题页可预览内置主题，拖动分隔条调整左右占比，并分别设置主体色、描边色、强调色、发光色。
- 自定义页可导入图片、自动抠图、设置热点并生成自定义光标，也支持拖动分隔条调整预览比例。
- 设置页可切换深色 / 浅色界面，调整全局光标大小、晃动尾迹开关与灵敏度、点击波纹、动态光标、按程序切换主题，以及全屏自动暂停增强。
- 按程序切换规则格式为 `进程名 = 主题ID`，例如 `powerpnt.exe = highlight_arrow`。

## 打包

默认复用 PyInstaller 缓存：

```powershell
.\scripts\build.ps1
```

强制 clean 重打包：

```powershell
.\scripts\build.ps1 -Clean
```

预期产物：

- `dist\\AtlasXCursorStudio\\AtlasXCursorStudio.exe`

完整发布：

```powershell
.\scripts\build_release.ps1
```

完整发布预期产物：

- `release\\AtlasXCursorStudio-portable.zip`
- `release\\AtlasXCursorStudio-Setup-1.0.exe`

如果只想生成便携版：

```powershell
.\scripts\build_release.ps1 -SkipInstaller
```

如果只想重新生成安装器：

```powershell
.\scripts\build_release.ps1 -SkipPortableZip
```

## 验证

```powershell
python -m pytest tests/test_config_manager.py tests/test_cursor_manager.py tests/test_hotkey_parser.py tests/test_image_pipeline.py tests/test_startup_manager.py tests/test_enhancement_manager.py tests/test_main_window_smoke.py
python -m compileall app core services ui tests
```

正式发布前建议再手工确认：

- 启动 `dist\AtlasXCursorStudio\AtlasXCursorStudio.exe`，确认托盘图标和主窗口正常。
- 安装器安装后可正常启动、卸载入口存在、桌面快捷方式可选创建。
- 便携版解压后可直接运行，不依赖仓库源码目录。
- 开机启动勾选与取消勾选都能正确写入和清除注册表项。
- 第一次自动抠图时，模型下载成功后可以继续使用。

## 已知限制

- 某些全屏应用、游戏或自行接管光标的程序可能覆盖系统光标替换结果。
- 动态光标当前对内置主题生效，自定义光标保持静态。
- 按程序切换目前基于前台进程名和内置主题 ID 规则匹配。
- 自定义光标的“全局光标大小”最佳效果依赖重新生成该光标文件。
- 当前 Codex 运行环境里，开机启动的 HKCU Run 实机写入验证会因为 `WinError 5` 失败；代码已实现，需在普通本机权限环境复测。
- PyInstaller 打包已在当前环境通过，正式发布默认采用更稳定的 onedir 目录输出。
- 如果分享给他人，必须分发整个目录、便携压缩包或安装器，单独发送 exe 会因缺少运行时 DLL 而无法启动。

## 仓库说明

- 本仓库默认提交源码、脚本、测试和必要静态资源。
- `build/`、`dist/`、`release/`、运行时日志和缓存目录默认不入库。
- 建议通过 GitHub Releases 上传安装器和便携压缩包，而不是把二进制产物直接提交进源码仓库。

## 原型为什么先用 Python，正式版为什么可转 C#

原型阶段使用 Python 的优势是界面、系统接口、图片处理和快速验证可以并行推进，适合在需求还在迭代时快速打通主链路。正式版如果追求更稳的 Windows 集成、更细的权限控制、更成熟的安装升级链路，以及更可控的发布包体积，可以转向 C# / .NET + WPF 或 WinUI 重写。


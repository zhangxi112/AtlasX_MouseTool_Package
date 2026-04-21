# Atlas-X Cursor Studio 1.0 发布指南

## 建议发布物

- 安装器：`release\AtlasXCursorStudio-Setup-1.0.exe`
- 便携版：`release\AtlasXCursorStudio-portable.zip`

源码仓库只保存代码和脚本，不把二进制发布物直接提交到 Git。

## 发布前检查

1. 运行测试：

```powershell
python -m pytest tests/test_config_manager.py tests/test_cursor_manager.py tests/test_hotkey_parser.py tests/test_image_pipeline.py tests/test_startup_manager.py tests/test_enhancement_manager.py tests/test_main_window_smoke.py
python -m compileall app core services ui tests
```

2. 构建发布包：

```powershell
.\scripts\build_release.ps1
```

3. 验证产物存在：

- `dist\AtlasXCursorStudio\AtlasXCursorStudio.exe`
- `release\AtlasXCursorStudio-portable.zip`
- `release\AtlasXCursorStudio-Setup-1.0.exe`

4. 手工冒烟检查：

- 应用可启动，托盘图标正常。
- 主窗口可打开、隐藏、退出。
- 至少一个内置主题可切换并恢复默认。
- 快捷键找回鼠标可触发。
- 便携版解压后可直接运行。
- 安装器安装完成后可启动，卸载入口正常。

## GitHub Release 建议文案

标题：

`Atlas-X Cursor Studio v1.0`

正文建议：

```text
Atlas-X Cursor Studio v1.0 发布。

本版本包含：
- 托盘常驻与主窗口恢复
- 10 套内置鼠标主题与配色自定义
- 找回鼠标高亮、晃动尾迹、点击波纹
- 自定义图片转 .cur 光标
- 按程序切换主题
- 动态光标
- 全屏自动暂停增强
- 开机启动控制

下载说明：
- 普通用户优先下载安装器：AtlasXCursorStudio-Setup-1.0.exe
- 不想安装可下载便携版：AtlasXCursorStudio-portable.zip

已知限制：
- 某些全屏游戏或自行接管光标的程序可能覆盖增强效果
- 首次使用自动抠图时可能需要联网下载模型
```

## 发布后回归

- 从 GitHub Release 下载安装器重新安装一次。
- 从 GitHub Release 下载便携版重新解压运行一次。
- 检查 README 中的版本号、发布文件名和实际产物一致。

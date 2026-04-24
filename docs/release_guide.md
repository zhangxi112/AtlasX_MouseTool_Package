# Atlas-X Cursor Studio 1.0 发布指南

## 版本与权属

- 软件正式产品名称：Atlas-X Cursor Studio
- 软著登记全称：Atlas-X Cursor Studio 鼠标指针自定义工具软件 V1.0
- 软件简称：Atlas-X Cursor Studio
- 著作权人：张希
- 开发完成日期：2026-04-21
- 首次发表日期：2026-04-21
- 首次发表地点：GitHub 网络发布

## 建议发布件

- 安装器：`release\AtlasXCursorStudio-Setup-1.0.exe`
- 便携版：`release\AtlasXCursorStudio-portable.zip`
- 发布包建议包含 `THIRD_PARTY_NOTICES.md` 和 `licenses` 目录。

## GitHub Release 建议文案

标题：`Atlas-X Cursor Studio v1.0`

```text
Atlas-X Cursor Studio v1.0 发布。

软件正式产品名称：Atlas-X Cursor Studio
软著登记全称：Atlas-X Cursor Studio 鼠标指针自定义工具软件 V1.0
著作权人：张希
首次发表日期：2026-04-21

本版本包含：托盘常驻、内置鼠标主题、配色自定义、找回鼠标高亮、晃动尾迹、点击波纹、自定义图片转 .cur 光标、按程序切换主题、动态光标、全屏自动暂停增强、开机启动控制。

第三方组件说明：本软件使用 PySide6 / Qt for Python 构建桌面界面。PySide6 Community Edition 按 LGPLv3 路径使用。第三方组件许可证见项目 THIRD_PARTY_NOTICES.md 或发布包 licenses 目录。
```

发布后保存 GitHub 仓库首页、提交记录、Release 页面和 LICENSE 页面截图，用于证明 2026-04-21 的公开发表事实。

## 第三方组件与 PySide6 合规口径

本软件使用 PySide6 Community Edition，并按 LGPLv3 路径履行许可义务。本软件未选择 PySide6 的 GPL 授权路径，项目自身代码不因使用 PySide6 而改用 GPL。本项目未修改 PySide6、Qt、Shiboken 源码。PySide6、Qt、Shiboken 及其相关组件不作为张希的原创源码提交。PySide6 用于 Qt 桌面界面、窗口控件、托盘和覆盖层窗口。第三方依赖仅作为运行依赖或构建依赖使用，不纳入软著原创源程序鉴别材料。

发布包建议新增 `licenses` 目录，放置：

- `LGPL-3.0.txt`
- `GPL-3.0.txt`
- PySide6 或 Qt for Python 许可说明
- Qt 第三方许可说明
- `THIRD_PARTY_NOTICES.md`

如后续进行严格商业闭源分发、企业部署、应用商店上架或无法满足 LGPLv3 要求，应重新评估 Qt for Python 商业授权。

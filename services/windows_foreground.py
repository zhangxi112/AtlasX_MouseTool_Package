"""Foreground window inspection helpers for Windows."""

from __future__ import annotations

import ctypes
import ctypes.wintypes
from dataclasses import dataclass
from pathlib import Path

WIN32_AVAILABLE = hasattr(ctypes, "windll")
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MONITOR_DEFAULTTONEAREST = 0x00000002


@dataclass(slots=True)
class ForegroundWindowInfo:
    """Snapshot of the currently focused top-level window."""

    process_name: str = ""
    process_path: str = ""
    window_title: str = ""
    is_fullscreen: bool = False


if WIN32_AVAILABLE:
    USER32 = ctypes.windll.user32
    KERNEL32 = ctypes.windll.kernel32

    class RECT(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("rcMonitor", RECT),
            ("rcWork", RECT),
            ("dwFlags", ctypes.c_ulong),
        ]

    USER32.GetForegroundWindow.restype = ctypes.c_void_p
    USER32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.wintypes.DWORD)]
    USER32.GetWindowTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]
    USER32.GetWindowRect.argtypes = [ctypes.c_void_p, ctypes.POINTER(RECT)]
    USER32.MonitorFromWindow.argtypes = [ctypes.c_void_p, ctypes.wintypes.DWORD]
    USER32.MonitorFromWindow.restype = ctypes.c_void_p
    USER32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFO)]
    KERNEL32.OpenProcess.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD]
    KERNEL32.OpenProcess.restype = ctypes.c_void_p
    KERNEL32.QueryFullProcessImageNameW.argtypes = [ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.c_wchar_p, ctypes.POINTER(ctypes.wintypes.DWORD)]
    KERNEL32.CloseHandle.argtypes = [ctypes.c_void_p]
else:
    USER32 = None
    KERNEL32 = None


def get_foreground_window_info() -> ForegroundWindowInfo:
    """Return process and fullscreen information for the active foreground window."""
    if not WIN32_AVAILABLE or USER32 is None or KERNEL32 is None:
        return ForegroundWindowInfo()

    hwnd = USER32.GetForegroundWindow()
    if not hwnd:
        return ForegroundWindowInfo()

    process_id = ctypes.wintypes.DWORD()
    USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    process_path = _query_process_path(process_id.value)
    title_buffer = ctypes.create_unicode_buffer(512)
    USER32.GetWindowTextW(hwnd, title_buffer, len(title_buffer))

    return ForegroundWindowInfo(
        process_name=Path(process_path).name.lower() if process_path else "",
        process_path=process_path,
        window_title=title_buffer.value,
        is_fullscreen=_is_foreground_window_fullscreen(hwnd),
    )


def _query_process_path(process_id: int) -> str:
    """Resolve a process image path with limited query rights."""
    if process_id <= 0 or KERNEL32 is None:
        return ""

    handle = KERNEL32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
    if not handle:
        return ""

    try:
        buffer_size = ctypes.wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(buffer_size.value)
        if not KERNEL32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(buffer_size)):
            return ""
        return buffer.value
    finally:
        KERNEL32.CloseHandle(handle)


def _is_foreground_window_fullscreen(hwnd: int) -> bool:
    """Return whether the foreground window currently fills its monitor."""
    if USER32 is None or not hwnd:
        return False

    rect = RECT()
    if not USER32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return False

    monitor = USER32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
    if not monitor:
        return False

    monitor_info = MONITORINFO()
    monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
    if not USER32.GetMonitorInfoW(monitor, ctypes.byref(monitor_info)):
        return False

    tolerance = 2
    return (
        abs(rect.left - monitor_info.rcMonitor.left) <= tolerance
        and abs(rect.top - monitor_info.rcMonitor.top) <= tolerance
        and abs(rect.right - monitor_info.rcMonitor.right) <= tolerance
        and abs(rect.bottom - monitor_info.rcMonitor.bottom) <= tolerance
    )

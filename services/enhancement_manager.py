"""Runtime coordinator for app switching, click ripples, dynamic cursors, shake-to-find, and game mode."""

from __future__ import annotations

import ctypes
import logging
import time
from collections import deque
from dataclasses import asdict
from pathlib import Path

from PySide6.QtCore import QObject, QPoint, QTimer, Signal
from PySide6.QtGui import QCursor

from core.builtin_themes import BUILTIN_THEMES
from core.models import AppThemeRule, CursorTheme
from services.windows_foreground import ForegroundWindowInfo, WIN32_AVAILABLE, get_foreground_window_info

VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04
USER32 = ctypes.windll.user32 if WIN32_AVAILABLE else None
VALID_RULE_THEME_IDS = {theme.theme_id for theme in BUILTIN_THEMES} | {"system_default"}


def parse_app_theme_rules(text: str) -> list[AppThemeRule]:
    """Parse process-to-theme rules from a textarea-style string."""
    rules: list[AppThemeRule] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ValueError(f"规则格式错误：{stripped}")
        process_name, theme_id = [part.strip() for part in stripped.split("=", 1)]
        theme_key = theme_id.lower()
        if not process_name:
            raise ValueError("规则中的进程名不能为空")
        if theme_key not in VALID_RULE_THEME_IDS:
            raise ValueError(f"未知主题标识：{theme_id}")
        rules.append(
            AppThemeRule(
                enabled=True,
                process_name=Path(process_name).name.lower(),
                theme=CursorTheme(
                    theme_id=theme_key,
                    theme_name=_theme_name_for_rule(theme_key),
                    source="system" if theme_key == "system_default" else "builtin",
                ),
            )
        )
    return rules


def serialize_app_theme_rules(rules: list[AppThemeRule]) -> str:
    """Serialize process-to-theme rules into textarea-friendly text."""
    return "\n".join(
        f"{rule.process_name} = {rule.theme.theme_id}"
        for rule in rules
        if rule.enabled and rule.process_name
    )


class EnhancementManager(QObject):
    """Coordinates advanced runtime enhancements without leaking logic into the UI."""

    runtime_state_changed = Signal()

    def __init__(self, cursor_manager, overlay_manager, config_provider) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.cursor_manager = cursor_manager
        self.overlay_manager = overlay_manager
        self.config_provider = config_provider
        self.app_poll_timer = QTimer(self)
        self.app_poll_timer.timeout.connect(self._poll_foreground)
        self.click_poll_timer = QTimer(self)
        self.click_poll_timer.timeout.connect(self._poll_mouse_buttons)
        self.motion_poll_timer = QTimer(self)
        self.motion_poll_timer.timeout.connect(self._poll_motion)
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._advance_animation)
        self._button_state = {"left": False, "right": False, "middle": False}
        self._foreground = ForegroundWindowInfo()
        self._game_mode_active = False
        self._active_rule: AppThemeRule | None = None
        self._target_theme = CursorTheme()
        self._animation_frames: list[Path] = []
        self._animation_index = 0
        self._recent_positions: deque[tuple[float, int, int]] = deque(maxlen=18)
        self._last_shake_trigger_at = 0.0
        self._shake_live_until = 0.0

    @property
    def foreground_process_name(self) -> str:
        return self._foreground.process_name

    @property
    def game_mode_active(self) -> bool:
        return self._game_mode_active

    @property
    def effective_theme(self) -> CursorTheme:
        return self._clone_theme(self._target_theme)

    @property
    def active_rule(self) -> AppThemeRule | None:
        if self._active_rule is None:
            return None
        return AppThemeRule(enabled=self._active_rule.enabled, process_name=self._active_rule.process_name, theme=self._clone_theme(self._active_rule.theme))

    def start(self) -> None:
        self.refresh_from_config(force_apply=True)

    def stop(self) -> None:
        self.app_poll_timer.stop()
        self.click_poll_timer.stop()
        self.motion_poll_timer.stop()
        self.animation_timer.stop()
        self._animation_frames = []

    def refresh_from_config(self, force_apply: bool = False) -> None:
        config = self.config_provider()
        if config.app_switch.enabled or config.game_mode.auto_disable_enhancements:
            self.app_poll_timer.setInterval(max(300, config.app_switch.poll_interval_ms))
            if not self.app_poll_timer.isActive():
                self.app_poll_timer.start()
        else:
            self.app_poll_timer.stop()
            self._foreground = ForegroundWindowInfo()

        if config.click_ripple.enabled and WIN32_AVAILABLE:
            self.click_poll_timer.setInterval(24)
            if not self.click_poll_timer.isActive():
                self.click_poll_timer.start()
        else:
            self.click_poll_timer.stop()
            self._button_state = {"left": False, "right": False, "middle": False}

        if config.pointer.shake_to_find_enabled:
            self.motion_poll_timer.setInterval(30)
            if not self.motion_poll_timer.isActive():
                self.motion_poll_timer.start()
        else:
            self.motion_poll_timer.stop()
            self._recent_positions.clear()

        self.animation_timer.setInterval(max(90, config.dynamic_cursor.frame_interval_ms))
        self._sync_runtime_state(force_apply=force_apply)

    def notify_base_theme_changed(self) -> None:
        self._sync_runtime_state(force_apply=True)

    def _poll_foreground(self) -> None:
        info = get_foreground_window_info()
        if info == self._foreground:
            return
        self._foreground = info
        self._sync_runtime_state(force_apply=False)

    def _poll_mouse_buttons(self) -> None:
        if USER32 is None:
            return
        for button_name, vk_code in (("left", VK_LBUTTON), ("right", VK_RBUTTON), ("middle", VK_MBUTTON)):
            pressed = bool(USER32.GetAsyncKeyState(vk_code) & 0x8000)
            if pressed and not self._button_state[button_name] and not self._game_mode_active:
                self.overlay_manager.trigger_click_ripple(QCursor.pos(), button_name)
            self._button_state[button_name] = pressed

    def _poll_motion(self) -> None:
        config = self.config_provider()
        if self._game_mode_active or not config.pointer.shake_to_find_enabled:
            self._recent_positions.clear()
            self._shake_live_until = 0.0
            return

        pos = QCursor.pos()
        now = time.perf_counter()
        self._recent_positions.append((now, pos.x(), pos.y()))
        while self._recent_positions and (now - self._recent_positions[0][0]) > 0.4:
            self._recent_positions.popleft()

        if len(self._recent_positions) < 4:
            return

        if self._is_shake_motion(config.pointer.shake_distance_threshold):
            session_active = now <= self._shake_live_until
            if session_active or (now - self._last_shake_trigger_at) * 1000 >= config.pointer.shake_cooldown_ms:
                if not session_active:
                    self._last_shake_trigger_at = now
                self._shake_live_until = now + 0.35

        if now <= self._shake_live_until:
            self.overlay_manager.trigger_motion_trail(self._build_motion_trail_points(), replace=True)

    def _build_motion_trail_points(self) -> list[QPoint]:
        sampled: list[QPoint] = []
        last_point: QPoint | None = None
        for _, x_pos, y_pos in self._recent_positions:
            point = QPoint(x_pos, y_pos)
            if last_point is None or abs(point.x() - last_point.x()) + abs(point.y() - last_point.y()) >= 14:
                sampled.append(point)
                last_point = point
        if sampled and sampled[-1] != QCursor.pos():
            sampled.append(QCursor.pos())
        return sampled[-8:]

    def _is_shake_motion(self, threshold: int) -> bool:
        total_distance = 0.0
        min_x = max_x = self._recent_positions[0][1]
        min_y = max_y = self._recent_positions[0][2]
        direction_changes = 0
        previous_dx_sign = 0

        for previous, current in zip(self._recent_positions, list(self._recent_positions)[1:]):
            dx = current[1] - previous[1]
            dy = current[2] - previous[2]
            total_distance += abs(dx) + abs(dy)
            min_x = min(min_x, current[1])
            max_x = max(max_x, current[1])
            min_y = min(min_y, current[2])
            max_y = max(max_y, current[2])
            dx_sign = 1 if dx > 0 else -1 if dx < 0 else 0
            if previous_dx_sign and dx_sign and dx_sign != previous_dx_sign:
                direction_changes += 1
            if dx_sign:
                previous_dx_sign = dx_sign

        span_x = max_x - min_x
        span_y = max_y - min_y
        compact_enough = max(span_x, span_y) <= max(260, int(threshold * 0.85))
        return total_distance >= threshold and direction_changes >= 2 and span_x >= 45 and compact_enough

    def _sync_runtime_state(self, force_apply: bool) -> None:
        config = self.config_provider()
        new_game_mode_active = bool(config.game_mode.auto_disable_enhancements and self._foreground.is_fullscreen)
        if new_game_mode_active != self._game_mode_active:
            self._game_mode_active = new_game_mode_active
            self.overlay_manager.set_effects_suspended(new_game_mode_active)

        new_rule = None
        if config.app_switch.enabled and not self._game_mode_active:
            new_rule = self._match_rule(config.app_switch.rules, self._foreground.process_name)

        target_theme = self._clone_theme(new_rule.theme if new_rule is not None else config.app_state.current_theme)
        target_changed = not self._themes_equal(target_theme, self._target_theme)
        rule_changed = self._rule_key(new_rule) != self._rule_key(self._active_rule)

        self._active_rule = new_rule
        self._target_theme = target_theme

        if force_apply or target_changed or rule_changed:
            self._apply_static_theme(self._target_theme)
        self._sync_animation(force_reset=force_apply or target_changed)
        self.overlay_manager.set_follow_pointer_mode(
            enabled=(not self._game_mode_active and config.pointer.cursor_size_percent > 500),
            size_percent=config.pointer.cursor_size_percent,
        )
        self.runtime_state_changed.emit()

    def _sync_animation(self, force_reset: bool) -> None:
        config = self.config_provider()
        size_percent = config.pointer.cursor_size_percent
        can_animate = config.dynamic_cursor.enabled and not self._game_mode_active and self._target_theme.source == "builtin" and self._target_theme.theme_id not in {"", "system_default"}

        if not can_animate:
            was_animating = self.animation_timer.isActive() or bool(self._animation_frames)
            self.animation_timer.stop()
            self._animation_frames = []
            self._animation_index = 0
            if was_animating:
                self._apply_static_theme(self._target_theme)
            return

        palette_override = self._palette_override_for_theme(self._target_theme)
        new_frames = self.cursor_manager.get_animated_theme_frame_paths(
            self._target_theme.theme_id,
            size_percent=size_percent,
            palette_override=palette_override,
        )
        if not new_frames:
            self.animation_timer.stop()
            self._animation_frames = []
            return

        if force_reset or new_frames != self._animation_frames:
            self._animation_frames = new_frames
            self._animation_index = 0
            self._apply_animation_frame(self._animation_frames[self._animation_index])
        if not self.animation_timer.isActive():
            self.animation_timer.start()

    def _advance_animation(self) -> None:
        if not self._animation_frames or self._game_mode_active:
            return
        self._animation_index = (self._animation_index + 1) % len(self._animation_frames)
        self._apply_animation_frame(self._animation_frames[self._animation_index])

    def _apply_animation_frame(self, cursor_path: Path) -> None:
        if not self.cursor_manager.apply_cursor_file(cursor_path):
            self.logger.warning("Failed to apply animated cursor frame: %s", cursor_path)

    def _apply_static_theme(self, theme: CursorTheme) -> None:
        config = self.config_provider()
        palette_override = self._palette_override_for_theme(theme)
        if not self.cursor_manager.apply_theme(theme, size_percent=config.pointer.cursor_size_percent, palette_override=palette_override):
            self.logger.warning("Failed to apply target theme: %s", theme)

    def _palette_override_for_theme(self, theme: CursorTheme) -> dict[str, str] | None:
        if theme.source != "builtin" or not theme.theme_id:
            return None
        palette = self.config_provider().app_state.builtin_theme_palettes.get(theme.theme_id, {})
        return palette or None

    def _match_rule(self, rules: list[AppThemeRule], process_name: str) -> AppThemeRule | None:
        normalized = Path(process_name).name.lower()
        for rule in rules:
            if rule.enabled and Path(rule.process_name).name.lower() == normalized and normalized:
                return rule
        return None

    def _themes_equal(self, left: CursorTheme, right: CursorTheme) -> bool:
        return asdict(left) == asdict(right)

    def _clone_theme(self, theme: CursorTheme) -> CursorTheme:
        return CursorTheme(**asdict(theme))

    def _rule_key(self, rule: AppThemeRule | None) -> tuple[str, str] | None:
        if rule is None:
            return None
        return (rule.process_name.lower(), rule.theme.theme_id)


def _theme_name_for_rule(theme_id: str) -> str:
    if theme_id == "system_default":
        return "系统默认"
    for theme in BUILTIN_THEMES:
        if theme.theme_id == theme_id:
            return theme.name
    return theme_id



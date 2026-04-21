"""Mouse-find, motion-trail, and click-ripple overlay manager."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QPoint, QRect, QTimer, Qt
from PySide6.QtGui import QColor, QCursor, QGuiApplication, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import QApplication, QWidget


@dataclass(slots=True)
class RippleState:
    center: QPoint
    started_at: float
    duration_ms: int
    size: int
    color: QColor


@dataclass(slots=True)
class TrailState:
    points: list[QPoint]
    started_at: float
    duration_ms: int
    size: int
    color: QColor
    style: str


class EffectOverlay(QWidget):
    """Transparent top-level window used for pointer emphasis animations."""

    def __init__(self, screen_geometry: QRect) -> None:
        super().__init__(None)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setGeometry(screen_geometry)
        self._find_center = QPoint(0, 0)
        self._find_duration_ms = 1500
        self._find_ring_size = 220
        self._find_started_at = 0.0
        self._find_active = False
        self._ripples: list[RippleState] = []
        self._trails: list[TrailState] = []
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._advance)
        self._follow_pointer = False
        self._follow_pointer_pos = QPoint(0, 0)
        self._follow_pointer_size = 0
        self._follow_pointer_color = QColor(34, 211, 238)

    def start_find_effect(self, global_cursor_pos: QPoint, duration_ms: int, ring_size: int) -> None:
        self._find_duration_ms = duration_ms
        self._find_ring_size = ring_size
        self._find_center = global_cursor_pos - self.geometry().topLeft()
        self._find_started_at = time.perf_counter()
        self._find_active = True
        self._ensure_running()

    def add_click_ripple(self, global_cursor_pos: QPoint, duration_ms: int, size: int, color: QColor) -> None:
        self._ripples.append(RippleState(global_cursor_pos - self.geometry().topLeft(), time.perf_counter(), duration_ms, size, color))
        self._ensure_running()

    def add_motion_trail(self, global_points: list[QPoint], duration_ms: int, size: int, color: QColor, style: str, replace: bool = False) -> None:
        if not global_points:
            return
        local_points = [point - self.geometry().topLeft() for point in global_points]
        state = TrailState(local_points, time.perf_counter(), duration_ms, size, color, style)
        if replace:
            self._trails = [state]
        else:
            self._trails.append(state)
        self._ensure_running()

    def set_follow_pointer(self, global_cursor_pos: QPoint, size: int, color: QColor) -> None:
        self._follow_pointer = True
        self._follow_pointer_pos = global_cursor_pos - self.geometry().topLeft()
        self._follow_pointer_size = size
        self._follow_pointer_color = color
        self._ensure_running()

    def clear_follow_pointer(self) -> None:
        self._follow_pointer = False
        if not self._find_active and not self._ripples and not self._trails and not self._follow_pointer:
            self.hide()

    def _ensure_running(self) -> None:
        self.show()
        self.raise_()
        if not self._timer.isActive():
            self._timer.start()
        self.update()

    def _advance(self) -> None:
        now = time.perf_counter()
        if self._find_active and (now - self._find_started_at) * 1000 >= self._find_duration_ms:
            self._find_active = False
        self._ripples = [ripple for ripple in self._ripples if (now - ripple.started_at) * 1000 < ripple.duration_ms]
        self._trails = [trail for trail in self._trails if (now - trail.started_at) * 1000 < trail.duration_ms]
        if not self._find_active and not self._ripples and not self._trails and not self._follow_pointer:
            self._timer.stop()
            self.hide()
            return
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        if not self.isVisible():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for trail in self._trails:
            self._paint_motion_trail(painter, trail)
        if self._find_active:
            self._paint_find_effect(painter)
        if self._follow_pointer:
            self._paint_follow_pointer(painter)
        for ripple in self._ripples:
            self._paint_click_ripple(painter, ripple)
        painter.end()

    def _paint_find_effect(self, painter: QPainter) -> None:
        progress = min(1.0, max(0.0, ((time.perf_counter() - self._find_started_at) * 1000) / self._find_duration_ms))
        gradient = QRadialGradient(self._find_center, self._find_ring_size * 1.1)
        gradient.setColorAt(0.0, QColor(255, 245, 157, int(175 * (1.0 - progress * 0.65))))
        gradient.setColorAt(0.45, QColor(253, 224, 71, int(90 * (1.0 - progress * 0.55))))
        gradient.setColorAt(1.0, QColor(253, 224, 71, 0))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self._find_center, int(self._find_ring_size * 1.1), int(self._find_ring_size * 1.1))
        primary_radius = int((self._find_ring_size * 0.35) + (self._find_ring_size * 0.85 * progress))
        secondary_progress = max(0.0, progress - 0.25) / 0.75
        secondary_radius = int((self._find_ring_size * 0.2) + (self._find_ring_size * 0.75 * secondary_progress))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(248, 250, 252, int(220 * (1.0 - progress))), 6))
        painter.drawEllipse(self._find_center, primary_radius, primary_radius)
        painter.setPen(QPen(QColor(14, 165, 233, int(180 * (1.0 - secondary_progress))), 4))
        painter.drawEllipse(self._find_center, secondary_radius, secondary_radius)
        painter.setPen(QPen(QColor(15, 23, 42, int(230 * (1.0 - progress * 0.8))), 3))
        painter.setBrush(QColor(250, 204, 21, int(255 * (1.0 - progress * 0.5))))
        painter.drawEllipse(self._find_center, 10, 10)

    def _paint_follow_pointer(self, painter: QPainter) -> None:
        size = max(120, self._follow_pointer_size)
        tip_x = self._follow_pointer_pos.x()
        tip_y = self._follow_pointer_pos.y()
        path = QPainterPath()
        path.moveTo(tip_x, tip_y)
        path.lineTo(tip_x + size * 0.20, tip_y + size * 0.62)
        path.lineTo(tip_x + size * 0.33, tip_y + size * 0.48)
        path.lineTo(tip_x + size * 0.47, tip_y + size * 0.90)
        path.lineTo(tip_x + size * 0.63, tip_y + size * 0.82)
        path.lineTo(tip_x + size * 0.49, tip_y + size * 0.41)
        path.lineTo(tip_x + size * 0.84, tip_y + size * 0.41)
        path.closeSubpath()

        glow_pen = QPen(QColor(self._follow_pointer_color.red(), self._follow_pointer_color.green(), self._follow_pointer_color.blue(), 110), max(10, int(size * 0.045)))
        glow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(glow_pen)
        painter.setBrush(QColor(self._follow_pointer_color.red(), self._follow_pointer_color.green(), self._follow_pointer_color.blue(), 55))
        painter.drawPath(path)

        painter.setPen(QPen(QColor(15, 23, 42, 220), max(4, int(size * 0.016))))
        painter.setBrush(QColor(248, 250, 252, 230))
        painter.drawPath(path)

        ring_radius = max(18, int(size * 0.12))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 190), max(3, int(size * 0.01))))
        painter.drawEllipse(self._follow_pointer_pos, ring_radius, ring_radius)
        painter.setPen(QPen(QColor(self._follow_pointer_color.red(), self._follow_pointer_color.green(), self._follow_pointer_color.blue(), 220), max(6, int(size * 0.014))))
        painter.drawEllipse(self._follow_pointer_pos, int(ring_radius * 1.45), int(ring_radius * 1.45))

    def _paint_motion_trail(self, painter: QPainter, trail: TrailState) -> None:
        if not trail.points:
            return
        progress = min(1.0, max(0.0, ((time.perf_counter() - trail.started_at) * 1000) / trail.duration_ms))
        fade = 1.0 - progress
        if trail.style == "dash":
            self._paint_dash_trail(painter, trail, fade)
        elif trail.style == "comet":
            self._paint_comet_trail(painter, trail, fade)
        elif trail.style == "spark":
            self._paint_spark_trail(painter, trail, fade)
        elif trail.style == "ring":
            self._paint_ring_trail(painter, trail, fade)
        else:
            self._paint_glow_trail(painter, trail, fade)

    def _path_for_points(self, points: list[QPoint]) -> QPainterPath:
        path = QPainterPath(points[0])
        for point in points[1:]:
            path.lineTo(point)
        return path

    def _paint_glow_trail(self, painter: QPainter, trail: TrailState, fade: float) -> None:
        if len(trail.points) >= 2:
            pen = QPen(QColor(trail.color.red(), trail.color.green(), trail.color.blue(), int(150 * fade)), max(4, int(trail.size * 0.08)))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self._path_for_points(trail.points))
        for index, point in enumerate(trail.points):
            point_fade = fade * ((index + 1) / len(trail.points))
            radius = max(6, int((trail.size * 0.1) + (trail.size * 0.16 * point_fade)))
            gradient = QRadialGradient(point, radius * 1.6)
            gradient.setColorAt(0.0, QColor(trail.color.red(), trail.color.green(), trail.color.blue(), int(120 * point_fade)))
            gradient.setColorAt(0.65, QColor(248, 250, 252, int(90 * point_fade)))
            gradient.setColorAt(1.0, QColor(trail.color.red(), trail.color.green(), trail.color.blue(), 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            painter.drawEllipse(point, int(radius * 1.6), int(radius * 1.6))
        self._paint_trail_endpoint(painter, trail, fade)

    def _paint_dash_trail(self, painter: QPainter, trail: TrailState, fade: float) -> None:
        if len(trail.points) >= 2:
            pen = QPen(QColor(trail.color.red(), trail.color.green(), trail.color.blue(), int(210 * fade)), max(3, int(trail.size * 0.06)))
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(self._path_for_points(trail.points))
        self._paint_trail_endpoint(painter, trail, fade)

    def _paint_comet_trail(self, painter: QPainter, trail: TrailState, fade: float) -> None:
        for index, point in enumerate(trail.points):
            local_fade = fade * ((index + 1) / len(trail.points))
            radius = max(4, int(trail.size * (0.06 + 0.02 * index)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(trail.color.red(), trail.color.green(), trail.color.blue(), int(110 * local_fade)))
            painter.drawEllipse(point, radius, radius)
        self._paint_trail_endpoint(painter, trail, fade)

    def _paint_spark_trail(self, painter: QPainter, trail: TrailState, fade: float) -> None:
        for index, point in enumerate(trail.points):
            local_fade = fade * ((index + 1) / len(trail.points))
            pen = QPen(QColor(trail.color.red(), trail.color.green(), trail.color.blue(), int(210 * local_fade)), 2)
            painter.setPen(pen)
            painter.drawLine(point.x() - 8, point.y(), point.x() + 8, point.y())
            painter.drawLine(point.x(), point.y() - 8, point.x(), point.y() + 8)
            painter.setBrush(QColor(248, 250, 252, int(120 * local_fade)))
            painter.drawEllipse(point, 3, 3)
        self._paint_trail_endpoint(painter, trail, fade)

    def _paint_ring_trail(self, painter: QPainter, trail: TrailState, fade: float) -> None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for index, point in enumerate(trail.points):
            local_fade = fade * ((index + 1) / len(trail.points))
            radius = max(6, int(trail.size * (0.08 + 0.02 * index)))
            painter.setPen(QPen(QColor(trail.color.red(), trail.color.green(), trail.color.blue(), int(180 * local_fade)), 2))
            painter.drawEllipse(point, radius, radius)
        self._paint_trail_endpoint(painter, trail, fade)

    def _paint_trail_endpoint(self, painter: QPainter, trail: TrailState, fade: float) -> None:
        end_point = trail.points[-1]
        end_radius = max(12, int(trail.size * 0.22))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, int(210 * fade)), 3))
        painter.drawEllipse(end_point, end_radius, end_radius)
        painter.setPen(QPen(QColor(trail.color.red(), trail.color.green(), trail.color.blue(), int(220 * fade)), 5))
        painter.drawEllipse(end_point, int(end_radius * 1.5), int(end_radius * 1.5))

    def _paint_click_ripple(self, painter: QPainter, ripple: RippleState) -> None:
        progress = min(1.0, max(0.0, ((time.perf_counter() - ripple.started_at) * 1000) / ripple.duration_ms))
        radius = int((ripple.size * 0.12) + (ripple.size * 0.88 * progress))
        glow_radius = int(radius * 1.35)
        gradient = QRadialGradient(ripple.center, glow_radius)
        gradient.setColorAt(0.0, QColor(ripple.color.red(), ripple.color.green(), ripple.color.blue(), int(70 * (1.0 - progress))))
        gradient.setColorAt(0.6, QColor(ripple.color.red(), ripple.color.green(), ripple.color.blue(), int(38 * (1.0 - progress))))
        gradient.setColorAt(1.0, QColor(ripple.color.red(), ripple.color.green(), ripple.color.blue(), 0))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(ripple.center, glow_radius, glow_radius)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(ripple.color.red(), ripple.color.green(), ripple.color.blue(), int(210 * (1.0 - progress))), 4))
        painter.drawEllipse(ripple.center, radius, radius)
        painter.setPen(QPen(QColor(248, 250, 252, int(160 * (1.0 - progress))), 2))
        painter.drawEllipse(ripple.center, int(radius * 0.62), int(radius * 0.62))


class OverlayManager:
    CLICK_COLORS = {
        "left": QColor(59, 130, 246),
        "right": QColor(244, 114, 182),
        "middle": QColor(16, 185, 129),
    }

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.app: QApplication | None = None
        self.config_provider: Any = None
        self.overlays: dict[str, EffectOverlay] = {}
        self.effects_suspended = False
        self.pointer_timer = QTimer()
        self.pointer_timer.setInterval(16)
        self.pointer_timer.timeout.connect(self._update_follow_pointer)
        self.follow_pointer_enabled = False
        self.follow_pointer_size_percent = 100

    def attach_application(self, app: QApplication, config_provider) -> None:
        self.app = app
        self.config_provider = config_provider

    def set_effects_suspended(self, suspended: bool) -> None:
        self.effects_suspended = suspended
        if suspended:
            for overlay in self.overlays.values():
                overlay.hide()
        elif self.follow_pointer_enabled:
            self._update_follow_pointer()

    def set_follow_pointer_mode(self, enabled: bool, size_percent: int) -> None:
        self.follow_pointer_enabled = enabled
        self.follow_pointer_size_percent = size_percent
        if enabled and not self.effects_suspended:
            if not self.pointer_timer.isActive():
                self.pointer_timer.start()
            self._update_follow_pointer()
            return
        self.pointer_timer.stop()
        for overlay in self.overlays.values():
            overlay.clear_follow_pointer()

    def trigger_find_mouse(self) -> None:
        if self.app is None or self.config_provider is None:
            self.logger.warning("OverlayManager is not attached to a QApplication")
            return
        config = self.config_provider()
        settings = config.highlight
        if self.effects_suspended or not settings.enabled:
            return
        cursor_pos = QCursor.pos()
        screen = self._resolve_screen(cursor_pos)
        if screen is None:
            return
        self._get_overlay(screen.name(), screen.geometry()).start_find_effect(cursor_pos, settings.duration_ms, settings.ring_size)

    def trigger_motion_trail(self, global_points: list[QPoint], replace: bool = False) -> None:
        if self.app is None or self.config_provider is None or not global_points:
            return
        config = self.config_provider()
        if self.effects_suspended or not config.pointer.shake_to_find_enabled:
            return
        screen = self._resolve_screen(global_points[-1])
        if screen is None:
            return
        color = QColor(config.pointer.trail_color)
        style = config.pointer.trail_style or "glow"
        self._get_overlay(screen.name(), screen.geometry()).add_motion_trail(
            global_points,
            max(380, min(1200, config.highlight.duration_ms)),
            max(60, config.highlight.ring_size),
            color,
            style,
            replace=replace,
        )

    def trigger_click_ripple(self, global_cursor_pos: QPoint | None = None, button: str = "left") -> None:
        if self.app is None or self.config_provider is None:
            return
        config = self.config_provider()
        settings = config.click_ripple
        if self.effects_suspended or not settings.enabled:
            return
        cursor_pos = global_cursor_pos or QCursor.pos()
        screen = self._resolve_screen(cursor_pos)
        if screen is None:
            return
        color = self.CLICK_COLORS.get(button, self.CLICK_COLORS["left"])
        self._get_overlay(screen.name(), screen.geometry()).add_click_ripple(cursor_pos, settings.duration_ms, settings.size, color)

    def shutdown(self) -> None:
        self.pointer_timer.stop()
        for overlay in self.overlays.values():
            overlay.hide()
            overlay.close()
        self.overlays.clear()

    def _update_follow_pointer(self) -> None:
        if self.app is None or self.config_provider is None or not self.follow_pointer_enabled or self.effects_suspended:
            return
        cursor_pos = QCursor.pos()
        screen = self._resolve_screen(cursor_pos)
        if screen is None:
            return
        screen_geometry = screen.geometry()
        max_size = int(min(screen_geometry.width(), screen_geometry.height()) * 0.6)
        visual_size = min(max_size, max(180, int(self.follow_pointer_size_percent * 0.7)))
        color = QColor(self.config_provider().pointer.trail_color)
        for name, overlay in self.overlays.items():
            if name != screen.name():
                overlay.clear_follow_pointer()
        self._get_overlay(screen.name(), screen_geometry).set_follow_pointer(cursor_pos, visual_size, color)

    def _resolve_screen(self, cursor_pos: QPoint):
        if self.app is None:
            return None
        config = self.config_provider()
        if not config.highlight.multi_monitor:
            return self.app.primaryScreen()
        return QGuiApplication.screenAt(cursor_pos) or self.app.primaryScreen()

    def _get_overlay(self, screen_name: str, screen_geometry: QRect) -> EffectOverlay:
        overlay = self.overlays.get(screen_name)
        if overlay is None:
            overlay = EffectOverlay(screen_geometry)
            self.overlays[screen_name] = overlay
        else:
            overlay.setGeometry(screen_geometry)
        return overlay

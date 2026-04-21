"""Application icon helpers."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap


def create_app_icon(size: int = 64) -> QIcon:
    """Draw a transparent multi-size icon for the window and tray."""
    icon = QIcon()
    for icon_size in sorted({16, 20, 24, 32, 48, 64, size}):
        icon.addPixmap(_draw_icon_pixmap(icon_size))
    return icon


def _draw_icon_pixmap(size: int) -> QPixmap:
    """Render one icon size with a transparent background and crisp contrast."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    ring_rect = QRectF(size * 0.10, size * 0.10, size * 0.68, size * 0.68)
    ring_pen = QPen(QColor("#0EA5E9"), max(2.0, size * 0.10))
    painter.setPen(ring_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawArc(ring_rect, 28 * 16, 286 * 16)

    inner_pen = QPen(QColor("#FACC15"), max(1.5, size * 0.05))
    painter.setPen(inner_pen)
    painter.drawEllipse(QRectF(size * 0.23, size * 0.23, size * 0.40, size * 0.40))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#F8FAFC"))
    painter.drawEllipse(QRectF(size * 0.39, size * 0.39, size * 0.08, size * 0.08))

    arrow = QPainterPath()
    arrow.moveTo(QPointF(size * 0.48, size * 0.10))
    arrow.lineTo(QPointF(size * 0.48, size * 0.76))
    arrow.lineTo(QPointF(size * 0.62, size * 0.63))
    arrow.lineTo(QPointF(size * 0.72, size * 0.90))
    arrow.lineTo(QPointF(size * 0.84, size * 0.85))
    arrow.lineTo(QPointF(size * 0.73, size * 0.58))
    arrow.lineTo(QPointF(size * 0.93, size * 0.57))
    arrow.closeSubpath()

    glow_pen = QPen(QColor("#22C55E"), max(2.0, size * 0.07), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(glow_pen)
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawPath(arrow)

    outline_pen = QPen(QColor("#0F172A"), max(1.0, size * 0.035), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(outline_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(arrow)

    painter.end()
    return pixmap

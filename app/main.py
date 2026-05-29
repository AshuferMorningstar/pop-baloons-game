from __future__ import annotations

import sys
from pathlib import Path
import random
import wave
import struct

from PyQt6.QtCore import QTimer, Qt, QRect, QPropertyAnimation, QEasingCurve, QUrl
from PyQt6.QtGui import QFont, QGuiApplication, QPixmap, QPainter, QColor, QPainterPath, QPen
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SplashScreen(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Pop Balloons")
        self.setModal(True)
        self.setFixedSize(430, 760)

        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            geometry = screen.availableGeometry()
            self.move(
                geometry.center().x() - self.width() // 2,
                geometry.center().y() - self.height() // 2,
            )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        stage = QFrame(self)
        stage.setObjectName("splashStage")
        stage_layout = QVBoxLayout(stage)
        stage_layout.setContentsMargins(28, 28, 28, 28)
        stage_layout.setSpacing(18)
        stage_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loading = QLabel("Loading", stage)
        loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading.setObjectName("loadingBadge")

        logo = QLabel(stage)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = Path(__file__).resolve().parent / "assets" / "images" / "logo.svg"
        pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        title = QLabel("Pop Balloons", stage)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("splashTitle")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("A simple balloon popping game", stage)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setObjectName("splashSubtitle")

        stage_layout.addWidget(loading)
        stage_layout.addWidget(logo)
        stage_layout.addWidget(title)
        stage_layout.addWidget(subtitle)

        root_layout.addWidget(stage, 1)

        self.setStyleSheet(
            """
            QDialog {
                background: #c9efff;
            }
            QFrame#splashStage {
                background:
                    radial-gradient(circle at 20% 18%, rgba(255, 255, 255, 0.92), transparent 14%),
                    radial-gradient(circle at 82% 20%, rgba(255, 255, 255, 0.72), transparent 12%),
                    linear-gradient(160deg, #e6f7ff, #9edcff 56%, #6ec5ff);
            }
            QLabel#loadingBadge {
                color: #0284c7;
                background: rgba(255, 255, 255, 0.75);
                border-radius: 999px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 3px;
            }
            QLabel#splashTitle {
                color: #083344;
            }
            QLabel#splashSubtitle {
                color: #0f4c81;
                font-size: 14px;
                background: rgba(255, 255, 255, 0.45);
                border-radius: 18px;
                padding: 10px 14px;
            }
            """
        )

        QTimer.singleShot(3000, self.accept)


class BalloonLabel(QLabel):
    """A balloon-shaped label that reports clicks to the window."""

    def __init__(self, size: int, color: str, parent: QWidget | None = None, is_bomb: bool = False) -> None:
        super().__init__(parent)
        self._is_bomb = is_bomb
        self._body_color = QColor(color)
        self._balloon_width = size
        self._balloon_height = int(size * 1.35)
        self.setFixedSize(self._balloon_width, self._balloon_height)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        body_h = int(h * 0.74)

        # Draw a rounded balloon body with a gently tapered bottom.
        path = QPainterPath()
        path.addEllipse(w * 0.10, h * 0.04, w * 0.80, body_h * 0.88)
        taper = QPainterPath()
        taper.moveTo(w * 0.50, body_h * 0.96)
        taper.cubicTo(w * 0.47, body_h * 1.02, w * 0.45, body_h * 1.10, w * 0.46, body_h * 1.14)
        taper.lineTo(w * 0.54, body_h * 1.14)
        taper.cubicTo(w * 0.55, body_h * 1.10, w * 0.53, body_h * 1.02, w * 0.50, body_h * 0.96)

        border_color = QColor(255, 255, 255, 200) if not self._is_bomb else QColor(210, 210, 210, 210)
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(self._body_color)
        painter.drawPath(path)
        painter.drawPath(taper)

        # small highlight to make the balloon feel glossy
        highlight = QColor(255, 255, 255, 75) if not self._is_bomb else QColor(255, 255, 255, 30)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(highlight)
        painter.drawEllipse(int(w * 0.24), int(h * 0.16), int(w * 0.18), int(h * 0.18))

        # Knot and string at the bottom
        knot = QPainterPath()
        knot.moveTo(w * 0.50, body_h + h * 0.02)
        knot.lineTo(w * 0.46, body_h + h * 0.09)
        knot.lineTo(w * 0.54, body_h + h * 0.09)
        knot.closeSubpath()
        painter.setBrush(QColor(255, 255, 255, 180))
        painter.drawPath(knot)

        string_pen = QPen(QColor(255, 255, 255, 170), 1.4)
        painter.setPen(string_pen)
        painter.drawLine(int(w * 0.50), int(body_h + h * 0.10), int(w * 0.48), h - 2)

        if self._is_bomb:
            # use a skeleton emoji marker so bomb balloons are instantly recognizable
            skeleton_font = QFont()
            skeleton_font.setPointSize(max(13, int(w * 0.30)))
            skeleton_font.setBold(True)
            painter.setFont(skeleton_font)
            painter.setPen(QColor(245, 245, 245, 135))
            center_rect = QRect(0, 0, w, int(h * 0.76))
            painter.drawText(center_rect, Qt.AlignmentFlag.AlignCenter, "💀")

    def mousePressEvent(self, event) -> None:  # pop on click
        window = self.window()
        if hasattr(window, "pop_balloon"):
            window.pop_balloon(self)


class CloudLabel(QLabel):
    """A decorative cloud made by drawing overlapping ellipses onto a pixmap."""

    def __init__(self, width: int, height: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(width, height)
        pix = QPixmap(width, height)
        pix.fill(QColor(0, 0, 0, 0))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(255, 255, 255, 220)
        p.setBrush(color)
        p.setPen(QColor(255, 255, 255, 200))
        # draw three overlapping ellipses
        p.drawEllipse(int(width * 0.15), int(height * 0.3), int(width * 0.5), int(height * 0.6))
        p.drawEllipse(int(width * 0.45), int(height * 0.1), int(width * 0.5), int(height * 0.8))
        p.drawEllipse(int(width * -0.05), int(height * 0.1), int(width * 0.5), int(height * 0.7))
        p.end()
        self.setPixmap(pix)
        # speed for drifting: negative moves left
        self._speed = random.choice([-0.6, -0.4, -0.8])


class ConfirmDialog(QDialog):
    """Simple confirmation card asking the user to confirm quitting."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(320, 140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        msg = QLabel("Do you really want to quit the game?", self)
        msg.setObjectName("confirmMsg")
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        msg.setFont(title_font)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        cancel = QPushButton("Cancel", self)
        cancel.clicked.connect(self.reject)
        cancel.setFixedSize(96, 36)
        cancel.setObjectName("confirmCancel")

        confirm = QPushButton("Quit", self)
        confirm.clicked.connect(self.accept)
        confirm.setFixedSize(96, 36)
        confirm.setObjectName("confirmQuit")

        btn_row.addWidget(cancel)
        btn_row.addSpacing(12)
        btn_row.addWidget(confirm)
        btn_row.addStretch(1)

        layout.addStretch(1)
        layout.addWidget(msg)
        layout.addStretch(1)
        layout.addLayout(btn_row)

        self.setStyleSheet(
            """
            QDialog { background: rgba(255,255,255,0.98); border-radius: 14px; }
            QLabel#confirmMsg { color: #083344; font-size: 13px; }
            QPushButton#confirmQuit { background: #e53e3e; color: white; border-radius: 8px; }
            QPushButton#confirmCancel { background: #ffffff; color: #083344; border: 1px solid rgba(4,45,69,0.12); border-radius: 8px; }
            """
        )

        # ensure visibility for child widgets
        msg.show()
        cancel.show()
        confirm.show()


class GameOverDialog(QDialog):
    """Game-over card shown when a bomb balloon is clicked."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(330, 170)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Game Over", self)
        title.setObjectName("gameOverTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tf = QFont()
        tf.setPointSize(16)
        tf.setBold(True)
        title.setFont(tf)

        msg = QLabel("Boom! You clicked a bomb balloon.", self)
        msg.setObjectName("gameOverMsg")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        play_again = QPushButton("Play Again", self)
        play_again.setObjectName("playAgainButton")
        play_again.setFixedSize(118, 38)
        play_again.clicked.connect(self.accept)

        quit_btn = QPushButton("Quit", self)
        quit_btn.setObjectName("gameOverQuitButton")
        quit_btn.setFixedSize(96, 38)
        quit_btn.clicked.connect(self.reject)

        btn_row.addWidget(play_again)
        btn_row.addSpacing(10)
        btn_row.addWidget(quit_btn)
        btn_row.addStretch(1)

        layout.addWidget(title)
        layout.addWidget(msg)
        layout.addStretch(1)
        layout.addLayout(btn_row)

        self.setStyleSheet(
            """
            QDialog { background: rgba(255,255,255,0.98); border-radius: 14px; }
            QLabel#gameOverTitle { color: #9b1c1c; }
            QLabel#gameOverMsg { color: #083344; font-size: 13px; }
            QPushButton#playAgainButton { background: #1e7e34; color: white; border-radius: 8px; }
            QPushButton#gameOverQuitButton { background: #ffffff; color: #083344; border: 1px solid rgba(4,45,69,0.2); border-radius: 8px; }
            """
        )


class IntroDialog(QDialog):
    """Startup hint card shown before the game begins."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(360, 170)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Before You Start", self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tf = QFont()
        tf.setPointSize(15)
        tf.setBold(True)
        title.setFont(tf)

        msg = QLabel("Black balloons are bombs. Click one and the game is over.", self)
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setObjectName("introMsg")

        ok_btn = QPushButton("Start", self)
        ok_btn.setFixedSize(108, 38)
        ok_btn.setObjectName("introStartButton")
        ok_btn.clicked.connect(self.accept)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(ok_btn)
        btn_row.addStretch(1)

        layout.addWidget(title)
        layout.addWidget(msg)
        layout.addStretch(1)
        layout.addLayout(btn_row)

        self.setStyleSheet(
            """
            QDialog { background: rgba(255,255,255,0.98); border-radius: 14px; }
            QLabel#introMsg { color: #083344; font-size: 13px; }
            QPushButton#introStartButton { background: #1e7e34; color: white; border-radius: 8px; }
            """
        )


class HomeWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Pop Balloons")
        self.setFixedSize(430, 760)

        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            geometry = screen.availableGeometry()
            self.move(
                geometry.center().x() - self.width() // 2,
                geometry.center().y() - self.height() // 2,
            )

        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        dashboard = QFrame(central)
        dashboard.setObjectName("dashboardBar")
        dashboard.setFixedHeight(52)
        dashboard_layout = QHBoxLayout(dashboard)
        dashboard_layout.setContentsMargins(12, 8, 12, 8)

        title = QLabel("Pop Balloon", dashboard)
        title.setObjectName("dashboardTitle")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)

        dashboard_layout.addWidget(title)
        dashboard_layout.addStretch(1)

        body = QFrame(central)
        body.setObjectName("homeBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(30, 30, 30, 30)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        home_logo = QLabel(body)
        home_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        home_logo_path = Path(__file__).resolve().parent / "assets" / "images" / "logo.svg"
        home_pixmap = QPixmap(str(home_logo_path))
        if not home_pixmap.isNull():
            home_logo.setPixmap(
                home_pixmap.scaled(
                    110,
                    110,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        start_button = QPushButton("Start Game", body)
        start_button.setObjectName("startButton")
        start_button.setFixedSize(190, 54)
        start_button.clicked.connect(self.open_game)

        body_layout.addStretch(1)
        body_layout.addWidget(home_logo, alignment=Qt.AlignmentFlag.AlignCenter)
        body_layout.addSpacing(18)
        body_layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        body_layout.addStretch(1)

        root_layout.addWidget(dashboard)
        root_layout.addWidget(body, 1)

        self.setCentralWidget(central)
        self.setStyleSheet(
            """
            QMainWindow {
                background: #c9efff;
            }
            QFrame#dashboardBar {
                background: rgba(255, 255, 255, 0.28);
                border-bottom: 1px solid rgba(255, 255, 255, 0.45);
            }
            QLabel#dashboardTitle {
                color: #0f4c81;
            }
            QFrame#homeBody {
                background:
                    radial-gradient(circle at 18% 16%, rgba(255, 255, 255, 0.92), transparent 16%),
                    radial-gradient(circle at 82% 18%, rgba(255, 255, 255, 0.78), transparent 14%),
                    linear-gradient(160deg, #e6f7ff, #9edcff 56%, #6ec5ff);
            }
            QPushButton#startButton {
                background: #1e7e34;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
                font-weight: 700;
                padding: 12px 18px;
            }
            QPushButton#startButton:hover {
                background: #2b9440;
            }
            QPushButton#startButton:pressed {
                background: #176428;
            }
            """
        )

    def open_game(self) -> None:
        self.hide()
        # Lazily create the game window and show it. Keep a reference
        # on self so it is not garbage-collected. Pass `self` so the
        # game window can return to Home when quitting.
        self.game_window = GameWindow(home=self)
        self.game_window.show()
        try:
            self.game_window.raise_()
            self.game_window.activateWindow()
            self.game_window.setFocus()
        except Exception:
            pass


class GameWindow(QMainWindow):
    """Main game screen. Uses same background as HomeWindow and a
    centered, narrower dashboard bar at the top.
    """

    def __init__(self, home: HomeWindow | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Pop Balloons — Game")
        self.setFixedSize(430, 760)
        self._home = home

        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            geometry = screen.availableGeometry()
            self.move(
                geometry.center().x() - self.width() // 2,
                geometry.center().y() - self.height() // 2,
            )

        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Top bar that contains a centered, narrower dashboard content
        top_bar = QFrame(central)
        top_bar.setObjectName("dashboardBar")
        top_bar.setFixedHeight(52)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(8, 6, 8, 6)

        # Left: compact score panel placed directly in the top bar
        score_text = QLabel("Score", top_bar)
        score_text.setObjectName("scoreText")
        score_font = QFont()
        score_font.setPointSize(12)
        score_font.setBold(False)
        score_text.setFont(score_font)

        score_panel = QFrame(top_bar)
        score_panel.setObjectName("scorePanel")
        score_panel.setFixedSize(72, 32)
        score_layout = QHBoxLayout(score_panel)
        score_layout.setContentsMargins(8, 4, 8, 4)

        self.score_label = QLabel("0", score_panel)
        self.score_label.setObjectName("scoreLabel")
        score_font = QFont()
        score_font.setPointSize(11)
        score_font.setBold(True)
        self.score_label.setFont(score_font)
        score_layout.addWidget(self.score_label, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        top_bar_layout.addWidget(score_text, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        top_bar_layout.addSpacing(6)
        top_bar_layout.addWidget(score_panel, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        # expanding spacer pushes controls to the right edge
        top_bar_layout.addStretch(1)

        # Right: controls placed directly into the top bar
        # Single toggle button: shows ⏸ when running, ▶ when paused
        toggle_btn = QPushButton("⏸", top_bar)
        toggle_btn.setObjectName("toggleButton")
        toggle_btn.setFixedSize(38, 30)
        toggle_btn.setCheckable(True)
        toggle_btn.setChecked(False)
        toggle_btn.clicked.connect(self.toggle_pause)
        self.toggle_btn = toggle_btn

        quit_btn = QPushButton("✖", top_bar)
        quit_btn.setObjectName("quitButton")
        quit_btn.setFixedSize(38, 30)
        quit_btn.clicked.connect(self.show_quit_confirm)

        mute_btn = QPushButton("🔊", top_bar)
        mute_btn.setObjectName("muteButton")
        mute_btn.setFixedSize(38, 30)
        mute_btn.clicked.connect(self.toggle_music_mute)
        self.mute_btn = mute_btn

        top_bar_layout.addWidget(toggle_btn, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        top_bar_layout.addSpacing(6)
        top_bar_layout.addWidget(mute_btn, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        top_bar_layout.addSpacing(6)
        top_bar_layout.addWidget(quit_btn, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

        # Game stage placeholder
        stage = QFrame(central)
        stage.setObjectName("gameStage")
        stage_layout = QVBoxLayout(stage)
        stage_layout.setContentsMargins(20, 20, 20, 20)
        stage_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Keep the stage visually clean; clouds and balloons are the only content.
        # The bomb hint is shown in a startup card instead of staying on the play field.

        # Keep a reference to the stage and set up balloon timers
        self.stage = stage
        self._balloons: list[BalloonLabel] = []
        self._score = 0
        self._paused = False
        self._game_started = False

        # Base pacing for the game; score-based difficulty updates this later.
        self._spawn_interval_ms = 320
        self._balloon_speed_px = 5

        self._spawn_timer = QTimer(self)
        self._spawn_timer.timeout.connect(self.spawn_balloon)

        self._move_timer = QTimer(self)
        self._move_timer.timeout.connect(self.update_balloons)

        # add decorative clouds to the stage using crisp SVG assets
        self._clouds: list[QLabel] = []
        stage_w = max(1, self.stage.width())
        # possible cloud sizes (will be picked randomly)
        cloud_sizes = [(220, 60), (180, 48), (260, 72), (140, 40), (200, 56)]
        assets_dir = Path(__file__).resolve().parent / "assets" / "images"
        # create a few more clouds for depth; reuse available SVG assets
        # create clouds per band with tailored counts, sizes and opacities
        # larger, fainter clouds near the bottom; smaller, crisper at the top
        cloud_bands = {"top": 3, "middle": 3, "bottom": 2}
        for band, count in cloud_bands.items():
            for i in range(count):
                w, h = random.choice(cloud_sizes)
                # scale sizes by band: top larger (pops out of screen),
                # middle smaller and subtle, bottom larger for depth.
                if band == "bottom":
                    if i == count - 1:
                        w = int(w * 1.15)
                        h = int(h * 1.15)
                    else:
                        w = int(w * 1.25)
                        h = int(h * 1.25)
                elif band == "top":
                    w = int(w * 1.2)
                    h = int(h * 1.2)
                else:  # middle
                    if i == count - 1:
                        w = int(w * 1.02)
                        h = int(h * 1.02)
                    else:
                        w = int(w * 0.75)
                        h = int(h * 0.75)
                # cycle through provided svg files
                svg_idx = (i % 3) + 1
                svg_path = assets_dir / f"cloud{svg_idx}.svg"
                c = QLabel(self.stage)
                pix = QPixmap(str(svg_path))
                if not pix.isNull():
                    pix = pix.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    c.setPixmap(pix)
                    c.setFixedSize(pix.size())
                else:
                    c.setFixedSize(w, h)
                    c.setStyleSheet("background: rgba(255,255,255,0.9); border-radius: 20px;")
                # Allow top clouds to start slightly off-screen to the left.
                if band == "top":
                    if i == 0:
                        x = random.randint(-int(w * 0.60), -int(w * 0.45))
                    else:
                        x = random.randint(-int(stage_w * 0.18), max(0, stage_w - w - 20))
                else:
                    x = random.randint(-20, max(0, stage_w - w + 20))
                # assign band for later placement and variation
                c._band = band
                # temporary y so it's visible before final positioning
                c.move(x, random.randint(8, 140))
                c.show()
                # set band-specific opacity ranges
                try:
                    effect = QGraphicsOpacityEffect(c)
                    if band == "bottom":
                        if i == count - 1:
                            effect.setOpacity(random.uniform(0.38, 0.58))
                        else:
                            effect.setOpacity(random.uniform(0.4, 0.7))
                    elif band == "middle":
                        if i == count - 1:
                            effect.setOpacity(random.uniform(0.48, 0.68))
                        else:
                            effect.setOpacity(random.uniform(0.6, 0.85))
                    else:
                        effect.setOpacity(random.uniform(0.78, 0.99))
                    c.setGraphicsEffect(effect)
                except Exception:
                    pass
                self._clouds.append(c)
        
        # mark clouds as not yet positioned; we'll place them when the
        # window becomes visible (showEvent) to ensure correct stage size
        self._clouds_positioned = False

        # prepare pop sound (synthesizes a small wav if missing)
        self._pop_sound = None
        try:
            self.ensure_pop_sound()
        except Exception:
            self._pop_sound = None

        # prepare looping background music for the game session
        self._music_player = None
        self._music_output = None
        self._music_muted = False
        self._music_backend = "none"
        self._music_thread = None
        self._music_stop_event = None
        self._music_proc = None
        try:
            self.ensure_background_music()
        except Exception:
            self._music_player = None
            self._music_output = None

        root_layout.addWidget(top_bar)
        root_layout.addWidget(stage, 1)

        self.setCentralWidget(central)

        # Reuse similar styling as HomeWindow, and add a rule for dashboardContent
        self.setStyleSheet(
            """
            QMainWindow {
                background: #c9efff;
            }
            QFrame#dashboardBar {
                background: rgba(255, 255, 255, 0.28);
                border-bottom: 1px solid rgba(255, 255, 255, 0.45);
            }
            /* dashboardContent removed; using flat layout */
            QFrame#scorePanel {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
            }
            QLabel#scoreLabel {
                color: #0f4c81;
                font-size: 14px;
            }
            QLabel#scoreText {
                color: #042d45;
                font-size: 13px;
                padding-left: 0px;
                font-weight: 600;
            }
            QPushButton#toggleButton, QPushButton#muteButton, QPushButton#quitButton {
                background: #ffffff;
                border: 1px solid rgba(4,45,69,0.6);
                border-radius: 8px;
                padding: 2px 6px;
                color: #042d45;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton#toggleButton:hover, QPushButton#muteButton:hover, QPushButton#quitButton:hover {
                background: #dff4ff;
            }
            QLabel#dashboardTitle {
                color: #0f4c81;
            }
            QFrame#gameStage {
                background:
                    radial-gradient(circle at 18% 16%, rgba(255, 255, 255, 0.92), transparent 16%),
                    radial-gradient(circle at 82% 18%, rgba(255, 255, 255, 0.78), transparent 14%),
                    linear-gradient(160deg, #e6f7ff, #9edcff 56%, #6ec5ff);
            }
            """
        )

    def toggle_pause(self) -> None:
        # toggle visual state and internal paused flag
        self._paused = not getattr(self, "_paused", False)
        # update button glyph
        if getattr(self, "toggle_btn", None) is not None:
            self.toggle_btn.setText("▶" if self._paused else "⏸")
        # pause or resume timers
        if self._paused:
            try:
                self._spawn_timer.stop()
                self._move_timer.stop()
            except Exception:
                pass
        else:
            try:
                self._spawn_timer.start()
                self._move_timer.start()
            except Exception:
                pass

    def spawn_balloon(self) -> None:
        if getattr(self, "_paused", False):
            return
        # Bomb balloons appear from the start and become more common so they show up early.
        bomb_unlocked = self._score >= 0
        is_bomb = bomb_unlocked and random.random() < 0.32

        size = random.randint(38, 68) if is_bomb else random.randint(42, 78)
        colors = [
            "#ff5d73",  # red pink
            "#ff9f43",  # orange
            "#ffd166",  # yellow
            "#7bd389",  # green
            "#56cfe1",  # cyan
            "#5e60ce",  # indigo
            "#9d4edd",  # purple
            "#f72585",  # hot pink
        ]
        color = "#1b1b1b" if is_bomb else random.choice(colors)
        b = BalloonLabel(size, color, parent=self.stage, is_bomb=is_bomb)
        stage_w = max(1, self.stage.width())
        y = self.stage.height() + b.height()
        # Keep balloons close but not overlapping.
        min_gap = 2

        placed_x = None
        for _ in range(24):
            x = random.randint(10, max(10, stage_w - b.width() - 10))
            new_rect = QRect(x, y, b.width(), b.height())
            touching = False
            for existing in self._balloons:
                expanded = existing.geometry().adjusted(-min_gap, -min_gap, min_gap, min_gap)
                if expanded.intersects(new_rect):
                    touching = True
                    break
            if not touching:
                placed_x = x
                break

        if placed_x is None:
            # Skip this spawn tick if we can't place without touching.
            b.deleteLater()
            return

        x = placed_x
        b.move(x, y)
        b.show()
        self._balloons.append(b)

    def update_balloons(self) -> None:
        if getattr(self, "_paused", False):
            return
        to_remove = []
        for b in list(self._balloons):
            new_y = b.y() - self._balloon_speed_px
            b.move(b.x(), new_y)
            # remove if off the top
            if new_y + b.height() < -20:
                to_remove.append(b)
        for b in to_remove:
            try:
                self._balloons.remove(b)
            except ValueError:
                pass
            b.deleteLater()

        # clouds are static now; no per-frame movement
        pass

    def _update_difficulty(self) -> None:
        # Increase balloon speed by 1 every 10 score points.
        # There is no upper cap, so the game keeps accelerating.
        self._balloon_speed_px = 5 + (self._score // 10)
        try:
            self._spawn_timer.setInterval(self._spawn_interval_ms)
        except Exception:
            pass

    def showEvent(self, event) -> None:
        super().showEvent(event)
        # position clouds once after the window is shown (so stage has final size)
        if not getattr(self, "_clouds_positioned", False):
            QTimer.singleShot(50, self.position_clouds)
            self._clouds_positioned = True

        # Start music as soon as the game window appears so the intro card
        # and gameplay both share the same looping track.
        self.start_background_music()

        if not getattr(self, "_game_started", False):
            self._game_started = True
            QTimer.singleShot(0, self.show_intro_card)

    def show_intro_card(self) -> None:
        # Show the startup hint card before any balloons begin moving.
        self._paused = True
        try:
            self._move_timer.stop()
            self._spawn_timer.stop()
        except Exception:
            pass

        dlg = IntroDialog(self)
        center_x = self.geometry().center().x() - dlg.width() // 2
        center_y = self.geometry().center().y() - dlg.height() // 2
        dlg.move(center_x, center_y)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._paused = False
            self._update_difficulty()
            self.start_background_music()
            try:
                self._spawn_timer.start(self._spawn_interval_ms)
                self._move_timer.start(40)
            except Exception:
                pass
        else:
            self.handle_quit()

    def position_clouds(self) -> None:
        # place clouds across the full width and stagger vertical positions
        try:
            stage_w = max(1, self.stage.width())
            stage_h = max(1, self.stage.height())

            # Group clouds by band so we can space them horizontally to avoid
            # vertical "ladder" arrangements. Each band's clouds are placed
            # into segments across the width with randomized jitter.
            bands: dict[str, list[QLabel]] = {"top": [], "middle": [], "bottom": []}
            for c in self._clouds:
                band = getattr(c, "_band", "top")
                bands.setdefault(band, []).append(c)

            for band_name, clouds in bands.items():
                # Bias horizontal placement by band: top=left/offscreen, middle=center, bottom=right.
                # Use stable anchor slots so clouds spread apart instead of stacking vertically.
                if band_name == "top":
                    target_positions = [0.02, 0.18, 0.84]
                elif band_name == "middle":
                    target_positions = [0.38, 0.50, 0.64]
                else:
                    target_positions = [0.58, 0.80]

                for idx, c in enumerate(clouds):
                    w = c.width()
                    target = target_positions[min(idx, len(target_positions) - 1)]

                    if band_name == "top":
                        # Keep a little more than half of the left cloud outside.
                        if idx == 0:
                            x = int(-(w * 0.58)) + random.randint(-10, 10)
                        else:
                            x = int(stage_w * target) - w // 2 + random.randint(-10, 10)
                    else:
                        # Spread clouds around their target slots with a small jitter.
                        target_x = int(stage_w * target) - w // 2
                        slot_jitter = max(12, int(stage_w * 0.03))
                        x = target_x + random.randint(-slot_jitter, slot_jitter)

                    # clamp so the cloud stays in its intended half/side of the stage
                    if band_name == "middle":
                        x = max(int(stage_w * 0.30), min(x, int(stage_w * 0.74) - w))
                    elif band_name == "bottom":
                        x = max(int(stage_w * 0.44), min(x, stage_w - w + 10))
                    else:
                        x = min(x, int(stage_w * 0.15))

                    if band_name == "middle":
                        if idx == len(clouds) - 1:
                            # One middle cloud sits a bit lower, slightly right, bigger and fainter.
                            x = int(stage_w * 0.60) - w // 2 + random.randint(-12, 12)
                            y_min = int(stage_h * 0.34)
                            y_max = int(stage_h * 0.48)
                        else:
                            y_min = int(stage_h * 0.26)
                            y_max = int(stage_h * 0.54)
                    elif band_name == "bottom":
                        if idx == len(clouds) - 1:
                            # Move one bottom cloud to the opposite corner at the lowest edge.
                            x = int(stage_w * 0.02) - w // 2 + random.randint(-8, 8)
                            y_min = int(stage_h * 0.88)
                            y_max = stage_h - c.height() + 2
                        else:
                            y_min = int(stage_h * 0.60)
                            y_max = max(int(stage_h - 50), int(stage_h * 0.90))
                    else:
                        y_min = int(stage_h * 0.02)
                        y_max = max(8, int(stage_h * 0.14))

                    # increase vertical variance so clouds don't form rows
                    y_min = max(0, min(y_min, stage_h - 1))
                    y_max = max(y_min + 1, min(y_max, stage_h - 1))
                    y = random.randint(y_min, y_max)
                    c.move(x, y)
        except Exception:
            pass

    def ensure_pop_sound(self) -> None:
        assets_dir = Path(__file__).resolve().parent / "assets" / "sounds"
        assets_dir.mkdir(parents=True, exist_ok=True)
        pop_path = assets_dir / "pop.wav"
        burst_path = assets_dir / "burst.wav"
            # Prefer a user-supplied MP3 if present (balloonpopsound.mp3), otherwise synthesize or use existing pop.wav as a fallback.
        mp3_path = assets_dir / "balloonpopsound.mp3"
        if not pop_path.exists():
            # synthesize a short noise burst WAV (mono, 22050Hz, 0.12s)
            framerate = 22050
            duration = 0.12
            nframes = int(framerate * duration)
            max_amp = 16000
            import math

            samples = []
            for i in range(nframes):
                t = i / framerate
                # white noise with exponential decay envelope
                env = math.exp(-6 * t)
                val = int((random.uniform(-1.0, 1.0) * env) * max_amp)
                samples.append(val)

            with wave.open(str(pop_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(framerate)
                frames = b"".join(struct.pack('<h', s) for s in samples)
                wf.writeframes(frames)

        if not burst_path.exists():
            # synthesize a deeper, heavier burst for bomb balloons (mono, 22050Hz, 0.20s)
            framerate = 22050
            duration = 0.20
            nframes = int(framerate * duration)
            max_amp = 18000
            import math

            samples = []
            for i in range(nframes):
                t = i / framerate
                # Heavier decay so the burst ends quickly.
                env = math.exp(-10 * t)
                noise = random.uniform(-1.0, 1.0)
                low = math.sin(2 * math.pi * (90 + 40 * math.sin(10 * t)) * t)
                val = int(((noise * 0.7) + (low * 0.9)) * env * max_amp)
                samples.append(val)

            with wave.open(str(burst_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(framerate)
                frames = b"".join(struct.pack('<h', s) for s in samples)
                wf.writeframes(frames)

        # load with QSoundEffect. If an MP3 was added by the user, try that
        # first and fall back to the WAV file if needed.
        try:
            self._pop_sound = QSoundEffect(self)
            if mp3_path.exists():
                try:
                    self._pop_sound.setSource(QUrl.fromLocalFile(str(mp3_path)))
                except Exception:
                    # fall back to WAV if setting MP3 fails
                    self._pop_sound.setSource(QUrl.fromLocalFile(str(pop_path)))
            else:
                self._pop_sound.setSource(QUrl.fromLocalFile(str(pop_path)))
            self._pop_sound.setLoopCount(1)
            # Set a sane default volume but prime the sound engine to avoid
            # a noticeable delay on the very first playback. We play the
            # effect once silently when it finishes loading, then restore
            # the desired volume.
            self._pop_sound.setVolume(0.35)
            try:
                def _prime(loaded: bool) -> None:
                    if loaded:
                        try:
                            # play silently to warm up the audio backend
                            self._pop_sound.setVolume(0.0)
                            self._pop_sound.play()
                            # restore volume shortly after priming
                            QTimer.singleShot(60, lambda: self._pop_sound.setVolume(0.35))
                        except Exception:
                            pass
                        try:
                            self._pop_sound.loadedChanged.disconnect(_prime)
                        except Exception:
                            pass

                # connect priming handler; if already loaded the handler
                # will be invoked immediately via the signal semantics.
                self._pop_sound.loadedChanged.connect(_prime)
            except Exception:
                pass
        except Exception:
            self._pop_sound = None

        try:
            self._burst_sound = QSoundEffect(self)
            self._burst_sound.setSource(QUrl.fromLocalFile(str(burst_path)))
            self._burst_sound.setLoopCount(1)
            self._burst_sound.setVolume(0.95)
        except Exception:
            self._burst_sound = None
        # Also prepare an OS-level fallback (macOS `afplay`) if available.
        try:
            import shutil
            self._afplay = shutil.which("afplay")
        except Exception:
            self._afplay = None
        # record which file to play with fallback
        if mp3_path.exists():
            self._pop_file = mp3_path
        else:
            self._pop_file = pop_path
        self._burst_file = burst_path
        # debug log to console (useful during development)
        try:
            print("Pop sound file:", str(self._pop_file), "afplay:", self._afplay)
        except Exception:
            pass

    def ensure_background_music(self) -> None:
        assets_dir = Path(__file__).resolve().parent / "assets" / "sounds"
        music_path = assets_dir / "backgroundsound.mp3"
        if not music_path.exists():
            fallback_path = assets_dir / "backgroundmusic.m4a"
            if fallback_path.exists():
                music_path = fallback_path
            else:
                fallback_path = assets_dir / "backgroundmusic.mp4"
                if fallback_path.exists():
                    music_path = fallback_path

        self._music_path = music_path
        # Choose backend based on platform and available system players.
        try:
            import shutil
            import threading

            self._music_output = None
            self._music_player = None
            self._music_stop_event = None
            self._music_proc = None

            plat = sys.platform
            # macOS: prefer afplay (reliable on dev machine)
            if plat == "darwin":
                self._afplay = getattr(self, "_afplay", None) or shutil.which("afplay")
                if self._afplay:
                    self._music_backend = "afplay"
                    self._music_stop_event = threading.Event()
                    return
                # fall through to Qt if afplay missing

            # Try Qt backend first (works well on Windows if QtMultimedia is installed)
            try:
                self._music_output = QAudioOutput(self)
                self._music_player = QMediaPlayer(self)
                self._music_player.setAudioOutput(self._music_output)
                self._music_player.setSource(QUrl.fromLocalFile(str(self._music_path)))
                # Prefer using the Qt backend when available
                self._music_backend = "qt"
                return
            except Exception:
                self._music_output = None
                self._music_player = None

            # If Qt failed, try ffplay (common on Windows if ffmpeg is installed)
            ffplay = shutil.which("ffplay")
            if ffplay:
                self._music_backend = "ffplay"
                self._ffplay = ffplay
                self._music_stop_event = threading.Event()
                return

            # As a last resort, if afplay exists use it (covers some Unix-like systems)
            afplay = shutil.which("afplay")
            if afplay:
                self._afplay = afplay
                self._music_backend = "afplay"
                self._music_stop_event = threading.Event()
                return

            self._music_backend = "none"
        except Exception:
            self._music_backend = "none"

    def start_background_music(self) -> None:
        try:
            backend = getattr(self, "_music_backend", "none")
            if getattr(self, "_music_muted", False):
                return

            # Qt backend: use QMediaPlayer
            if backend == "qt" and getattr(self, "_music_player", None) is not None:
                try:
                    try:
                        # If supported, set infinite looping
                        self._music_player.setLoops(QMediaPlayer.Loops.Infinite)
                    except Exception:
                        pass
                    self._music_player.setPosition(0)
                    self._music_player.play()
                except Exception:
                    pass
                return

            # afplay backend (macOS)
            if backend == "afplay":
                import subprocess
                import threading

                if getattr(self, "_music_stop_event", None) is None:
                    self._music_stop_event = threading.Event()
                self._music_stop_event.clear()

                def _loop_music() -> None:
                    while not self._music_stop_event.is_set():
                        try:
                            print("Starting background music:", str(self._music_path))
                            self._music_proc = subprocess.Popen(
                                [self._afplay, str(self._music_path)],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                            )
                            self._music_proc.wait()
                        except Exception:
                            break
                        if self._music_stop_event.wait(0.2):
                            break

                if getattr(self, "_music_thread", None) is None or not self._music_thread.is_alive():
                    self._music_thread = threading.Thread(target=_loop_music, daemon=True)
                    self._music_thread.start()
                return

            # ffplay backend (cross-platform fallback if ffmpeg is installed)
            if backend == "ffplay":
                import subprocess

                try:
                    # spawn ffplay in loop mode; -nodisp hides video window
                    self._music_proc = subprocess.Popen(
                        [self._ffplay, "-nodisp", "-autoexit", "-loop", "0", "-loglevel", "quiet", str(self._music_path)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except Exception:
                    self._music_proc = None
                return
        except Exception:
            pass

    def stop_background_music(self) -> None:
        backend = getattr(self, "_music_backend", "none")
        try:
            if backend == "afplay" or backend == "ffplay":
                if getattr(self, "_music_stop_event", None) is not None:
                    try:
                        self._music_stop_event.set()
                    except Exception:
                        pass
                if getattr(self, "_music_proc", None) is not None:
                    try:
                        self._music_proc.terminate()
                    except Exception:
                        pass
                self._music_proc = None
                return

            if backend == "qt" and getattr(self, "_music_player", None) is not None:
                try:
                    self._music_player.stop()
                except Exception:
                    pass
                return
        except Exception:
            pass

    def toggle_music_mute(self) -> None:
        self._music_muted = not getattr(self, "_music_muted", False)
        backend = getattr(self, "_music_backend", "none")
        try:
            if backend == "qt" and getattr(self, "_music_output", None) is not None:
                try:
                    self._music_output.setVolume(0.0 if self._music_muted else 1.0)
                except Exception:
                    pass
            else:
                if self._music_muted:
                    self.stop_background_music()
                elif not getattr(self, "_paused", False):
                    self.start_background_music()
        except Exception:
            pass
        if getattr(self, "mute_btn", None) is not None:
            self.mute_btn.setText("🔇" if self._music_muted else "🔊")

    def pop_balloon(self, balloon: BalloonLabel) -> None:
        # remove from active list so update loop no longer moves it
        try:
            if balloon in self._balloons:
                try:
                    self._balloons.remove(balloon)
                except ValueError:
                    pass
        except Exception:
            pass

        if getattr(balloon, "_is_bomb", False):
            try:
                self._spawn_timer.stop()
                self._move_timer.stop()
                self._paused = True
                if getattr(self, "toggle_btn", None) is not None:
                    self.toggle_btn.setChecked(True)
                    self.toggle_btn.setText("▶")
            except Exception:
                pass

            try:
                if getattr(self, "_burst_sound", None) is not None:
                    try:
                        self._burst_sound.play()
                    except Exception:
                        QApplication.beep()
                else:
                    QApplication.beep()

                effect = QGraphicsOpacityEffect(balloon)
                balloon.setGraphicsEffect(effect)

                opacity_anim = QPropertyAnimation(effect, b"opacity", parent=balloon)
                opacity_anim.setDuration(210)
                opacity_anim.setStartValue(1.0)
                opacity_anim.setEndValue(0.0)
                opacity_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

                geom = balloon.geometry()
                center = geom.center()
                end_rect = QRect(center.x(), center.y(), 0, 0)

                geom_anim = QPropertyAnimation(balloon, b"geometry", parent=balloon)
                geom_anim.setDuration(210)
                geom_anim.setStartValue(geom)
                geom_anim.setEndValue(end_rect)
                geom_anim.setEasingCurve(QEasingCurve.Type.InBack)

                balloon._opacity_anim = opacity_anim
                balloon._geom_anim = geom_anim
                balloon._effect = effect

                def _after_burst() -> None:
                    try:
                        balloon.deleteLater()
                    except Exception:
                        pass
                    self.stop_background_music()
                    self._show_game_over_dialog()

                geom_anim.finished.connect(_after_burst)
                opacity_anim.start()
                geom_anim.start()
            except Exception:
                try:
                    balloon.deleteLater()
                except Exception:
                    pass
                self._show_game_over_dialog()
            return

        # play a short audible feedback (pop sound if available)
        try:
            # debug: log which playback methods are available
            try:
                print('pop_balloon: QSoundEffect=', getattr(self, '_pop_sound', None) is not None,
                      'afplay=', getattr(self, '_afplay', None), 'file=', getattr(self, '_pop_file', None))
            except Exception:
                pass
            if getattr(self, "_pop_sound", None) is not None:
                try:
                    self._pop_sound.play()
                except Exception:
                    QApplication.beep()
            else:
                QApplication.beep()
        except Exception:
            try:
                QApplication.beep()
            except Exception:
                pass

        # macOS CLI fallback: if `afplay` is available, play the file via subprocess
        try:
            if getattr(self, "_afplay", None):
                import subprocess
                # fire-and-forget so UI isn't blocked; allow overlapping pops
                popfile = getattr(self, "_pop_file", None)
                if popfile is None:
                    popfile = Path(__file__).resolve().parent / "assets" / "sounds" / "pop.wav"
                subprocess.Popen([self._afplay, "-v", "0.35", str(popfile)])
        except Exception:
            pass

        # add a small pop animation (scale down + fade out)
        try:
            effect = QGraphicsOpacityEffect(balloon)
            balloon.setGraphicsEffect(effect)

            # parent animations to the balloon so they are kept alive
            opacity_anim = QPropertyAnimation(effect, b"opacity", parent=balloon)
            opacity_anim.setDuration(260)
            opacity_anim.setStartValue(1.0)
            opacity_anim.setEndValue(0.0)
            opacity_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

            geom = balloon.geometry()
            center = geom.center()
            end_rect = QRect(center.x(), center.y(), 0, 0)

            geom_anim = QPropertyAnimation(balloon, b"geometry", parent=balloon)
            geom_anim.setDuration(260)
            geom_anim.setStartValue(geom)
            geom_anim.setEndValue(end_rect)
            geom_anim.setEasingCurve(QEasingCurve.Type.InBack)

            # keep references on the balloon so Python doesn't GC them
            balloon._opacity_anim = opacity_anim
            balloon._geom_anim = geom_anim
            balloon._effect = effect

            def _cleanup():
                try:
                    balloon.deleteLater()
                except Exception:
                    pass

            geom_anim.finished.connect(_cleanup)
            opacity_anim.start()
            geom_anim.start()
        except Exception:
            try:
                balloon.deleteLater()
            except Exception:
                pass

        self._score += 1
        try:
            self.score_label.setText(str(self._score))
        except Exception:
            pass
        self._update_difficulty()

    def restart_game(self) -> None:
        # Reset game state after game over and start fresh in the same window.
        for b in list(self._balloons):
            try:
                b.deleteLater()
            except Exception:
                pass
        self._balloons.clear()

        self._score = 0
        self.score_label.setText("0")
        self._paused = False
        if getattr(self, "toggle_btn", None) is not None:
            self.toggle_btn.setChecked(False)
            self.toggle_btn.setText("⏸")

        self._update_difficulty()
        self.start_background_music()
        try:
            self._spawn_timer.start(self._spawn_interval_ms)
            self._move_timer.start(40)
        except Exception:
            pass

    def _show_game_over_dialog(self) -> None:
        dlg = GameOverDialog(self)
        center_x = self.geometry().center().x() - dlg.width() // 2
        center_y = self.geometry().center().y() - dlg.height() // 2
        dlg.move(center_x, center_y)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.restart_game()
        else:
            self.handle_quit()

    def handle_quit(self) -> None:
        # Close game and show Home if we were given a reference.
        try:
            self.stop_background_music()
            self.close()
        finally:
            if getattr(self, "_home", None) is not None:
                try:
                    self._home.show()
                    self._home.raise_()
                    self._home.activateWindow()
                except Exception:
                    pass

    def show_quit_confirm(self) -> None:
        dlg = ConfirmDialog(self)
        # center dialog on the game window
        center_x = self.geometry().center().x() - dlg.width() // 2
        center_y = self.geometry().center().y() - dlg.height() // 2
        dlg.move(center_x, center_y)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.handle_quit()

    def closeEvent(self, event) -> None:  # show home when window is closed
        self.stop_background_music()
        if getattr(self, "_home", None) is not None:
            try:
                self._home.show()
                self._home.raise_()
                self._home.activateWindow()
            except Exception:
                pass
        super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    splash = SplashScreen()
    if splash.exec() == QDialog.DialogCode.Accepted:
        home = HomeWindow()
        home.show()
        app.exec()


if __name__ == "__main__":
    main()

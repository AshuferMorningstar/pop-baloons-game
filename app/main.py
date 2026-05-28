from __future__ import annotations

import sys
from pathlib import Path
import random

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QGuiApplication, QPixmap
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
    """Simple circular balloon that reports clicks to the window."""

    def __init__(self, size: int, color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setStyleSheet(f"background: {color}; border-radius: {size//2}px; border: 2px solid rgba(255,255,255,0.6);")

    def mousePressEvent(self, event) -> None:  # pop on click
        window = self.window()
        if hasattr(window, "pop_balloon"):
            window.pop_balloon(self)


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
        dashboard.setFixedHeight(68)
        dashboard_layout = QHBoxLayout(dashboard)
        dashboard_layout.setContentsMargins(20, 10, 20, 10)

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
        # Hide the Home window and open the GameWindow in-place so macOS
        # doesn't create a separate desktop/space for it.
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
        top_bar.setFixedHeight(68)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)

        # Left: compact score panel placed directly in the top bar
        top_bar_layout.addStretch(1)

        score_text = QLabel("Score", top_bar)
        score_text.setObjectName("scoreText")
        score_font = QFont()
        score_font.setPointSize(12)
        score_font.setBold(False)
        score_text.setFont(score_font)

        score_panel = QFrame(top_bar)
        score_panel.setObjectName("scorePanel")
        score_panel.setFixedSize(84, 36)
        score_layout = QHBoxLayout(score_panel)
        score_layout.setContentsMargins(8, 4, 8, 4)

        self.score_label = QLabel("0", score_panel)
        self.score_label.setObjectName("scoreLabel")
        score_font = QFont()
        score_font.setPointSize(12)
        score_font.setBold(True)
        self.score_label.setFont(score_font)
        score_layout.addWidget(self.score_label, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        top_bar_layout.addWidget(score_text, alignment=Qt.AlignmentFlag.AlignVCenter)
        top_bar_layout.addSpacing(6)
        top_bar_layout.addWidget(score_panel, alignment=Qt.AlignmentFlag.AlignVCenter)
        top_bar_layout.addStretch(1)

        # Right: controls placed directly into the top bar
        # Single toggle button: shows ⏸ when running, ▶ when paused
        toggle_btn = QPushButton("⏸", top_bar)
        toggle_btn.setObjectName("toggleButton")
        toggle_btn.setFixedSize(44, 34)
        toggle_btn.setCheckable(True)
        toggle_btn.setChecked(False)
        toggle_btn.clicked.connect(self.toggle_pause)
        self.toggle_btn = toggle_btn

        quit_btn = QPushButton("✖", top_bar)
        quit_btn.setObjectName("quitButton")
        quit_btn.setFixedSize(44, 34)
        quit_btn.clicked.connect(self.handle_quit)

        top_bar_layout.addWidget(toggle_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        top_bar_layout.addSpacing(6)
        top_bar_layout.addWidget(quit_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        top_bar_layout.addStretch(1)

        # Game stage placeholder
        stage = QFrame(central)
        stage.setObjectName("gameStage")
        stage_layout = QVBoxLayout(stage)
        stage_layout.setContentsMargins(20, 20, 20, 20)
        stage_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        placeholder = QLabel("Game area — balloons will appear here", stage)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stage_layout.addWidget(placeholder)

        # Keep a reference to the stage and set up balloon timers
        self.stage = stage
        self._balloons: list[BalloonLabel] = []
        self._score = 0
        self._paused = False

        self._spawn_timer = QTimer(self)
        self._spawn_timer.timeout.connect(self.spawn_balloon)
        self._spawn_timer.start(900)

        self._move_timer = QTimer(self)
        self._move_timer.timeout.connect(self.update_balloons)
        self._move_timer.start(40)

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
                padding-left: 6px;
                font-weight: 600;
            }
            QPushButton#toggleButton, QPushButton#quitButton {
                background: #ffffff;
                border: 1px solid rgba(4,45,69,0.6);
                border-radius: 8px;
                padding: 2px 6px;
                color: #042d45;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton#toggleButton:hover, QPushButton#quitButton:hover {
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
        size = random.randint(28, 52)
        colors = ["#ff7fb3", "#ffb37f", "#7fd3ff", "#b37fff", "#7fff9a"]
        color = random.choice(colors)
        b = BalloonLabel(size, color, parent=self.stage)
        stage_w = max(1, self.stage.width())
        x = random.randint(10, max(10, stage_w - size - 10))
        y = self.stage.height() + size
        b.move(x, y)
        b.show()
        self._balloons.append(b)

    def update_balloons(self) -> None:
        if getattr(self, "_paused", False):
            return
        to_remove = []
        for b in list(self._balloons):
            new_y = b.y() - 4
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

    def pop_balloon(self, balloon: BalloonLabel) -> None:
        try:
            if balloon in self._balloons:
                self._balloons.remove(balloon)
            balloon.deleteLater()
        except Exception:
            pass
        self._score += 1
        try:
            self.score_label.setText(str(self._score))
        except Exception:
            pass

    def handle_quit(self) -> None:
        # Close game and show Home if we were given a reference.
        try:
            self.close()
        finally:
            if getattr(self, "_home", None) is not None:
                try:
                    self._home.show()
                    self._home.raise_()
                    self._home.activateWindow()
                except Exception:
                    pass

    def closeEvent(self, event) -> None:  # show home when window is closed
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

# Pop Balloons Game

A small PyQt6 balloon-popping game with clouds, score-based difficulty, bomb balloons, sound effects, and looping background music.

## Features

- Balloon popping with score tracking
- Difficulty increases as your score rises
- Bomb balloons that end the round
- Background music with external player fallback
- Pause, mute, replay, and quit controls
- Intro and game-over cards

## Requirements

- Python 3.10 or newer
- PyQt6

## Install

Create and activate your virtual environment, then install the dependency:

```bash
pip install -r requirements.txt
```

## Run

From the project root:

```bash
python app/main.py
```

If your environment uses a specific interpreter, run the one inside `.venv` instead.

## Controls

- Click balloons to pop them
- Click the pause button to pause or resume the game
- Click the speaker button to mute or unmute music
- Click the X button to quit

## Assets

The game expects its media files in `app/assets/images/` and `app/assets/sounds/`.

Background music will try `backgroundsound.mp3` first and can fall back to other audio files in the sounds folder.

The game prefers the Qt Multimedia backend when available. If Qt's multimedia backend is not present, the game will attempt to use an external audio player when available (for example, `ffplay` from FFmpeg). See `requirements.txt` and the system package manager for installing these tools.

## Notes

If audio still does not play, check whether the operating system has access to the audio device and whether the sound files are valid for your system.

## Tools Used

- **Python:** Project runtime; development uses a virtual environment (`.venv`) and `pip` with `requirements.txt` for reproducible installs.
- **PyQt6:** Provides the GUI and multimedia APIs (`QPainter`, `QTimer`, `QSoundEffect`, `QMediaPlayer`/`QAudioOutput`).
- **wave / struct / math (stdlib):** Synthesize fallback WAV audio files (`pop.wav`, `burst.wav`) when no audio bundle is present.
- **subprocess / shutil / threading (stdlib):** Detect and invoke external audio players (for example, `ffplay`) and run them without blocking the UI.
- **py_compile:** Used during development as a quick syntax check (`python -m py_compile app/main.py`).

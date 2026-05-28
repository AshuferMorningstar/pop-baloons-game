# Pop Balloons Game

A small PyQt6 balloon-popping game with clouds, score-based difficulty, bomb balloons, sound effects, and looping background music.

## Features

- Balloon popping with score tracking
- Difficulty increases as your score rises
- Bomb balloons that end the round
- Background music with a macOS `afplay` fallback
 - Background music with external player fallbacks (platform-dependent)
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

The game prefers the Qt Multimedia backend when available. If Qt's multimedia backend is not present, the game will attempt to use an external audio player when available (examples: `afplay` on macOS, `ffplay` from FFmpeg on many platforms). See `requirements.txt` and the system package manager for installing these tools.

## Notes

If audio still does not play, check whether the operating system has access to the audio device and whether the sound files are valid for your system.

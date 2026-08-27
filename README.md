# VoiceTasks

Always-on Mac menubar app that saves tasks to Google Tasks by voice or text. Uses Mac's native speech recognition (no Whisper, ~15MB RAM).

## Features

- 🎤 menubar icon, always running
- **Record Task** - speak, transcribes via Mac `SFSpeechRecognizer`, saves to Google Tasks
- **Add Text Task...** - type a task
- Auto-starts on login (LaunchAgent)

## Setup

### 1. Google Tasks API credentials

1. [Google Cloud Console](https://console.cloud.google.com) -> new project
2. Enable **Google Tasks API**
3. OAuth consent screen -> External -> add yourself as a test user
4. Credentials -> Create **OAuth 2.0 Client ID** -> Desktop app
5. Download JSON, save as `credentials.json` in this folder

### 2. Install dependencies

```
pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client \
    pynput pyobjc-framework-Speech pyobjc-framework-AVFoundation rumps py2app
```

### 3. Authenticate (one-time, opens browser)

```
python3 add_task.py "test task"
```

### 4. Build the app

```
rm -rf build dist && python3 setup.py py2app
install_name_tool -change "@executable_path/../../../../Python3" \
    "@executable_path/../Frameworks/Python3.framework/Versions/3.9/Python3" \
    dist/VoiceTasks.app/Contents/MacOS/python
codesign --force --deep --sign - dist/VoiceTasks.app
```

### 5. Auto-start on login

Copy `com.rahul.voicetasks.plist` to `~/Library/LaunchAgents/`, then:

```
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.rahul.voicetasks.plist
```

## Usage

Click 🎤 in menubar:
- **Record Task** -> speak -> wait 1-2s -> **Stop & Save**
- **Add Text Task...** -> type -> Save

## Notes

- Must run as `.app` bundle, not a bare `python3` LaunchAgent - background daemons can't capture mic audio on macOS.
- After editing `menubar_task.py`, rebuild (step 4) and restart the LaunchAgent.
- Speak, then wait 1-2s before Stop - the recognizer needs time or returns empty.

## Files

| File | Purpose |
|------|---------|
| `add_task.py` | Google Tasks API insert (OAuth) |
| `menubar_task.py` | Menubar app (rumps + native speech) |
| `setup.py` | py2app build config |
| `com.rahul.voicetasks.plist` | LaunchAgent for auto-start |

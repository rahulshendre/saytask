# saytask

Capture tasks to Google Tasks the instant you think of them - by voice, a terminal command, or a menubar click. Built for macOS. Uses Apple's native speech recognition, so there's no Whisper model to download and it idles at ~15 MB RAM.

- **Terminal** - `note buy coffee` saves a task; `tasks` lists them.
- **Menubar** - click the 🎤, speak or type, it's saved.
- **Global hotkey** - `Cmd+Ctrl+K` to record from anywhere.

The terminal commands are the most reliable path and need no special permissions. The menubar app and hotkey add voice capture.

---

## Before you begin

You need:

- **macOS** (tested on Apple Silicon, macOS 14+).
- **Python 3.9+** with `pip3`. Check with `python3 --version`.
- A **Google account** with Google Tasks.
- Roughly **10 minutes** for the one-time Google API setup.

> **Note:** The terminal commands (`note`, `tasks`) work on their own. You only need the app build steps (5-7) if you want the menubar app and voice recording.

---

## Objectives

- Create Google API credentials and authorize saytask.
- Save and list tasks from your terminal.
- (Optional) Build the menubar app and enable voice capture.

---

## Get the code

```shell
git clone https://github.com/rahulshendre/saytask.git
cd saytask
```

> **Note:** The examples below assume the repo lives at `~/saytask`. If you cloned it elsewhere, adjust the paths in the shell functions and `com.rahul.voicetasks.plist` accordingly.

---

## Step 1 - Create Google Tasks API credentials

saytask talks to your Google Tasks over the official API. You need an OAuth client so Google knows the request is yours.

1. Open the [Google Cloud Console](https://console.cloud.google.com) and create a new project (or pick an existing one).
2. Navigate to **APIs & Services > Library**, search for **Google Tasks API**, and click **Enable**.
3. Go to **APIs & Services > OAuth consent screen**:
   - Choose **External** as the user type.
   - Under **Test users**, add your own Google address.
4. Go to **APIs & Services > Credentials > Create Credentials > OAuth client ID**:
   - Application type: **Desktop app**.
   - Download the JSON file.
5. Save the downloaded file as `credentials.json` in the repo root.

> **Warning:** `credentials.json` and the `token.json` created in Step 3 are secrets. They are listed in `.gitignore` - never commit them.

---

## Step 2 - Install dependencies

```shell
pip3 install \
  google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client \
  rumps pynput pyobjc-framework-Speech pyobjc-framework-AVFoundation py2app
```

> **Note:** `google-*` packages are all you need for the terminal commands. `rumps`, `pynput`, `pyobjc-*`, and `py2app` are only used by the menubar app.

---

## Step 3 - Authorize saytask

Run any command once to trigger the OAuth browser flow:

```shell
python3 add_task.py "hello from saytask"
```

Your browser opens and asks you to sign in and grant access. After you approve, the tool writes `token.json` and creates the task.

**Verify** the task was created:

```shell
python3 list_tasks.py
```

You should see `hello from saytask` in the output. Open the Google Tasks app to confirm.

---

## Step 4 - Add the terminal commands

Add these functions to your `~/.zshrc` (adjust the path if you cloned elsewhere):

```shell
cat >> ~/.zshrc <<'EOF'

# saytask
note() {
  local text
  if [ "$1" = "-c" ]; then
    text="$(pbpaste)"
    [ -z "$text" ] && { echo "clipboard is empty"; return 1; }
  elif [ $# -eq 0 ]; then
    echo "usage: note <task text>  |  note -c (clipboard)"; return 1
  else
    text="$*"
  fi
  /usr/bin/python3 "$HOME/saytask/add_task.py" "$text"
}
tasks() { /usr/bin/python3 "$HOME/saytask/list_tasks.py" "$@"; }
gt()    { open "https://tasks.google.com/embed/"; }
EOF
source ~/.zshrc
```

**Verify:**

```shell
note pick up milk
tasks
```

You now have the core workflow:

```shell
note buy coffee        # add a task (no quotes needed)
note -c                # add whatever's on your clipboard
tasks                  # list pending tasks
tasks all              # include completed tasks
gt                     # open Google Tasks in the browser
```

For most people, this is enough. To add voice capture, continue below.

---

## Step 5 - Build the menubar app (optional)

The menubar app must run as a signed `.app` bundle. A bare `python3` process launched by `launchd` cannot capture microphone audio on macOS.

```shell
./build.sh
```

`build.sh` runs `py2app`, patches the Python framework path that py2app links incorrectly, and code-signs the bundle. The result is `dist/VoiceTasks.app`.

> **Note:** `build.sh` signs with a self-signed certificate named `SayTask Self Signed`. If you don't have one, either create it (so permissions survive rebuilds) or edit `build.sh` to use ad-hoc signing (`--sign -`). Ad-hoc works but macOS re-prompts for permissions after every rebuild.

---

## Step 6 - Enable auto-start on login (optional)

```shell
cp com.rahul.voicetasks.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.rahul.voicetasks.plist
```

**Verify** the agent is running:

```shell
launchctl list | grep voicetasks
```

A line with a PID means it's up. Look for the 🎤 in your menu bar.

---

## Step 7 - Grant permissions (optional)

The first time you record, macOS prompts for **Microphone** and **Speech Recognition** - allow both.

For the global hotkey, add the app to **System Settings > Privacy & Security > Accessibility**:

1. Click **+**.
2. Press `Cmd+Shift+G` and enter the path to `dist/VoiceTasks.app`.
3. Toggle it **on**.

---

## Using the menubar app

Click the 🎤 in the menu bar:

- **Record Task** - speak, then click **Stop & Save**. Pause ~1-2 seconds before stopping so the recognizer captures the tail of your speech.
- **Add Text Task...** - type a task and save.

**Global hotkey:** press `Cmd+Ctrl+K` to start recording, press it again to stop and save.

---

## Troubleshooting

**`note` or `tasks` prints nothing / "command not found"**
Open a new terminal tab, or run `source ~/.zshrc`. The functions load only in new shells.

**Recording saves an empty task ("No speech detected")**
You stopped too quickly. Speak, wait 1-2 seconds, then stop.

**The menubar app records but nothing is saved**
The bundled Python leaks env vars into the subprocess. saytask already strips `PYTHONPATH`/`PYTHONHOME`/`PYTHONEXECUTABLE`; if you forked the code, keep that logic.

**Global hotkey does nothing**
The app isn't trusted for input monitoring. Re-add `dist/VoiceTasks.app` under Accessibility. Note that re-signing the app (or an ad-hoc rebuild) invalidates the previous grant - use a stable certificate to avoid this.

**The hotkey moves a window instead of recording**
Another app (e.g. Rectangle) owns that shortcut. Change `HOTKEY` in `menubar_task.py`, then rebuild.

---

## Reference

| File | Purpose |
|------|---------|
| `add_task.py` | Adds a task to Google Tasks (OAuth). Powers `note`. |
| `list_tasks.py` | Lists tasks. Powers `tasks`. |
| `menubar_task.py` | The menubar app: native speech recognition + global hotkey. |
| `setup.py` | `py2app` build configuration. |
| `build.sh` | Builds, patches, and signs `VoiceTasks.app`. |
| `com.rahul.voicetasks.plist` | `launchd` agent for auto-start on login. |

---

## What's next

- Purge test entries with a cleanup command (planned).
- Parse due dates from natural language ("...tomorrow at 3").
- Auto-stop recording on silence, removing the second click.

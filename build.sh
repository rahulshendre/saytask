#!/bin/bash
# Build VoiceTasks.app with stable self-signed cert so mic/Accessibility
# permissions survive rebuilds. Run from the saytask/ folder.
set -e

CERT="SayTask Self Signed"
APP="dist/VoiceTasks.app"
PYFRAME="@executable_path/../Frameworks/Python3.framework/Versions/3.9/Python3"
BADPATH="@executable_path/../../../../Python3"

echo "==> cleaning"
rm -rf build dist

echo "==> py2app build"
python3 setup.py py2app >/dev/null

echo "==> fixing Python framework path"
install_name_tool -change "$BADPATH" "$PYFRAME" "$APP/Contents/MacOS/python" 2>/dev/null || true

echo "==> signing with stable cert: $CERT"
codesign --force --deep --sign "$CERT" "$APP"

echo "==> verify"
codesign -dvvv "$APP" 2>&1 | grep -i "authority" || echo "WARN: signature check failed"

echo "==> done. Restart daemon:"
echo "   launchctl bootout gui/\$(id -u) ~/Library/LaunchAgents/com.rahul.voicetasks.plist"
echo "   launchctl bootstrap gui/\$(id -u) ~/Library/LaunchAgents/com.rahul.voicetasks.plist"

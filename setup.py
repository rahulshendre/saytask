from setuptools import setup

APP = ['menubar_task.py']
OPTIONS = {
    'argv_emulation': False,
    'packages': ['rumps', 'Speech', 'AVFoundation', 'pynput'],
    'plist': {
        'CFBundleName': 'VoiceTasks',
        'CFBundleDisplayName': 'VoiceTasks',
        'CFBundleIdentifier': 'com.rahul.voicetasks',
        'CFBundleVersion': '1.0.0',
        'LSUIElement': True,
        'NSMicrophoneUsageDescription': 'VoiceTasks needs mic to record voice tasks.',
        'NSSpeechRecognitionUsageDescription': 'VoiceTasks uses speech recognition to transcribe tasks.',
    },
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

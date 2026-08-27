#!/usr/bin/env python3
import rumps
import threading
import subprocess
import sys
import os
import warnings
warnings.filterwarnings("ignore")

import Speech
import AVFoundation

ADD_TASK_SCRIPT = "/Users/rahulshendre/saytask/add_task.py"


class VoiceTaskApp(rumps.App):
    def __init__(self):
        super().__init__("🎤", quit_button="Quit")
        self.is_recording = False
        self.audio_engine = None
        self.request = None
        self._done_event = None
        self._result_holder = None
        self.menu = [
            rumps.MenuItem("Record Task", callback=self.toggle_record),
            rumps.MenuItem("Add Text Task...", callback=self.text_task),
            None
        ]

    def toggle_record(self, sender):
        print(f"toggle: is_recording={self.is_recording}", flush=True)
        if not self.is_recording:
            sender.title = "Stop & Save"
            self.title = "🔴"
            threading.Thread(target=self.start_recording, daemon=True).start()
        else:
            sender.title = "Record Task"
            self.title = "⏳"
            threading.Thread(target=self.stop_recording, daemon=True).start()

    def text_task(self, _):
        response = rumps.Window(
            message="Enter task:",
            title="Add Task",
            default_text="",
            ok="Save",
            cancel="Cancel"
        ).run()
        if response.clicked and response.text.strip():
            threading.Thread(target=self.save_task, args=(response.text.strip(),), daemon=True).start()

    def start_recording(self):
        print("start_recording", flush=True)
        self.recognizer = Speech.SFSpeechRecognizer.alloc().initWithLocale_(
            Speech.NSLocale.alloc().initWithLocaleIdentifier_("en-US")
        )
        self.audio_engine = AVFoundation.AVAudioEngine.alloc().init()
        self.request = Speech.SFSpeechAudioBufferRecognitionRequest.alloc().init()
        self.request.setShouldReportPartialResults_(False)

        input_node = self.audio_engine.inputNode()
        recording_format = input_node.outputFormatForBus_(0)

        self._result_holder = {"text": ""}
        self._done_event = threading.Event()

        def recognition_handler(result, error):
            print(f"handler: result={result} error={error}", flush=True)
            if result:
                self._result_holder["text"] = result.bestTranscription().formattedString()
            if error or (result and result.isFinal()):
                self._done_event.set()

        self.task = self.recognizer.recognitionTaskWithRequest_resultHandler_(self.request, recognition_handler)
        input_node.installTapOnBus_bufferSize_format_block_(
            0, 1024, recording_format,
            lambda buf, when: self.request.appendAudioPCMBuffer_(buf)
        )

        ok, err = self.audio_engine.startAndReturnError_(None)
        print(f"engine started ok={ok} err={err}", flush=True)
        self.is_recording = True
        rumps.notification("Voice Tasks", "", "Recording... click Stop & Save when done")

    def stop_recording(self):
        print("stop_recording", flush=True)
        self.is_recording = False

        if self.audio_engine:
            self.audio_engine.stop()
            self.audio_engine.inputNode().removeTapOnBus_(0)
        if self.request:
            self.request.endAudio()

        if self._done_event:
            self._done_event.wait(timeout=10)

        text = self._result_holder.get("text", "") if self._result_holder else ""
        print(f"recognized: '{text}'", flush=True)
        self.save_task(text)
        self.title = "🎤"

    def save_task(self, text):
        text = text.strip()
        if not text:
            rumps.notification("Voice Tasks", "", "No speech detected")
            return
        clean_env = {k: v for k, v in os.environ.items()
                     if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONEXECUTABLE")}
        result = subprocess.run(
            ["/usr/bin/python3", ADD_TASK_SCRIPT, text],
            capture_output=True, text=True, env=clean_env
        )
        if result.returncode == 0:
            rumps.notification("Task Saved", "", text)
            print(f"saved: {text}", flush=True)
        else:
            rumps.notification("Voice Tasks", "", "Failed to save")
            print(f"error: {result.stderr}", flush=True)


if __name__ == "__main__":
    Speech.SFSpeechRecognizer.requestAuthorization_(lambda s: None)
    VoiceTaskApp().run()

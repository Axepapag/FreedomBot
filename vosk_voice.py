import queue
import sounddevice as sd
import vosk
import json

MODEL_PATH = r"C:\Dexter\model\vosk-model-en-us-0.22"

class VoiceRecorder:
    def __init__(self):
        self.model = vosk.Model(MODEL_PATH)
        self.q = queue.Queue()
        self.recording = False
        self.rec = None
        self.text = ""
        self.stream = None

    def start(self):
        self.text = ""
        self.recording = True
        self.q = queue.Queue()
        self.rec = vosk.KaldiRecognizer(self.model, 16000)
        self.stream = sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=self.callback
        )
        self.stream.start()

    def stop(self):
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        final = self.rec.FinalResult()
        self.text += json.loads(final).get("text", "")
        return self.text.strip()

    def callback(self, indata, frames, time, status):
        if self.recording:
            audio_bytes = bytes(indata)
            if self.rec.AcceptWaveform(audio_bytes):
                res = json.loads(self.rec.Result())
                self.text += res.get("text", "") + " "

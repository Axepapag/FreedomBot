
import sys
import threading
import requests
from PyQt5 import QtWidgets, QtGui, QtCore
import pyttsx3

from vosk_voice import VoiceRecorder  # Ensure vosk_voice.py is present!

API_URL = "http://127.0.0.1:8080"
API_KEY = "changeme-strong-key"

def api_headers():
    return {"x-api-key": API_KEY}

def tts_speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    engine.say(text)
    engine.runAndWait()

class DexterVoiceGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dexter Voice Desktop GUI")
        self.setGeometry(200, 100, 950, 630)
        self.central_widget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.central_widget)
        self.last_dexter_reply = ""

        # --- CHAT TAB ---
        self.chat_tab = QtWidgets.QWidget()
        self.setup_chat_tab()
        self.central_widget.addTab(self.chat_tab, "Chat")

        # Add other tabs as in your classic GUI (skills, patch, etc.) if desired...

    def setup_chat_tab(self):
        layout = QtWidgets.QVBoxLayout()
        self.chat_history = QtWidgets.QTextEdit()
        self.chat_history.setReadOnly(True)

        # Input row: [Mic] [Text input] [Send] [Speaker]
        row = QtWidgets.QHBoxLayout()
        self.mic_btn = QtWidgets.QPushButton("🎤")
        self.mic_btn.setToolTip("Speak your message")
        self.mic_btn.setFixedWidth(38)
        self.mic_btn.clicked.connect(self.start_voice_input)
        self.chat_input = QtWidgets.QLineEdit()
        self.chat_input.setPlaceholderText("Type or speak your message to Dexter...")
        self.chat_input.returnPressed.connect(self.send_chat)
        self.send_btn = QtWidgets.QPushButton("Send")
        self.send_btn.setFixedWidth(60)
        self.send_btn.clicked.connect(self.send_chat)
        self.speaker_btn = QtWidgets.QPushButton("🔊")
        self.speaker_btn.setToolTip("Replay last Dexter reply")
        self.speaker_btn.setFixedWidth(38)
        self.speaker_btn.clicked.connect(self.replay_tts)
        row.addWidget(self.mic_btn)
        row.addWidget(self.chat_input)
        row.addWidget(self.send_btn)
        row.addWidget(self.speaker_btn)

        layout.addWidget(self.chat_history)
        layout.addLayout(row)
        self.chat_tab.setLayout(layout)

    def start_voice_input(self):
        self.chat_history.append("<i>Listening...</i>")
        QtCore.QCoreApplication.processEvents()
        def record_and_fill():
            try:
                recorder = VoiceRecorder()
                recorder.start()
                self.chat_history.append("<i>Recording... Press Enter in terminal or wait for silence.</i>")
                QtCore.QCoreApplication.processEvents()
                text = recorder.stop()
                if not text:
                    text = "[no speech detected]"
                self.chat_input.setText(text)
                self.chat_history.append(f"<i>You said:</i> {text}")
            except Exception as e:
                self.chat_history.append(f"<b>STT Error:</b> {e}")
        threading.Thread(target=record_and_fill, daemon=True).start()

    def send_chat(self):
        user_text = self.chat_input.text().strip()
        if not user_text:
            return
        self.chat_history.append(f"<b>You:</b> {user_text}")
        self.chat_input.clear()
        QtCore.QCoreApplication.processEvents()

        # Call Dexter API, stream reply, TTS on finish
        def chat_api():
            try:
                resp = requests.post(
                    f"{API_URL}/chat/stream",
                    json={"user_input": user_text},
                    headers=api_headers(),
                    stream=True,
                    timeout=180,
                )
                resp.raise_for_status()
                dexter_reply = ""
                self.chat_history.append("<b>Dexter:</b> ")
                for chunk in resp.iter_content(chunk_size=None):
                    token = chunk.decode(errors="ignore")
                    dexter_reply += token
                    self.chat_history.moveCursor(QtGui.QTextCursor.End)
                    self.chat_history.insertPlainText(token)
                    QtCore.QCoreApplication.processEvents()
                self.chat_history.append("\n")
                self.last_dexter_reply = dexter_reply
                # Optionally, auto-speak
                tts_speak(dexter_reply)
            except Exception as e:
                self.chat_history.append(f"\n<b>Error:</b> {e}\n")
        threading.Thread(target=chat_api, daemon=True).start()

    def replay_tts(self):
        if self.last_dexter_reply:
            tts_speak(self.last_dexter_reply)
        else:
            tts_speak("No previous reply to speak.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = DexterVoiceGUI()
    win.show()
    sys.exit(app.exec_())
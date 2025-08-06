from vosk_voice import VoiceRecorder

recorder = VoiceRecorder()
print("Speak now...")
recorder.start()
input("Press Enter to stop...")
text = recorder.stop()
print("You said:", text)

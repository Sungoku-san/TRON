from voice_module import TronAssistant
from biometrics import record_voice

tron = TronAssistant()
tron.speak("Voice enrollment started.")
record_voice(tron, "authorized_voice.wav", duration=5)
tron.speak("Voice enrollment completed successfully.")

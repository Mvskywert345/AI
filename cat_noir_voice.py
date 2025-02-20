import random
import pyttsx3
from pydub import AudioSegment
from pydub.playback import play

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 190)  # More energetic
engine.setProperty('voice', engine.getProperty('voices')[0].id)  # Replace 0 with your best voice index

# Clip mapping
cat_clips_map = {
    "meow": "cat-1.wav",
    "ready": "cat-2.wav",
    "save": "cat_3.wav",
    "day": "cat_4.wav",
    "default": "cat_5.wav"
}

def play_clip(text):
    """Play a clip based on text content, or a random default."""
    for keyword, clip in cat_clips_map.items():
        if keyword in text.lower():
            cat_audio = AudioSegment.from_wav(clip)
            play(cat_audio)
            return
    clip = random.choice(list(cat_clips_map.values()))
    cat_audio = AudioSegment.from_wav(clip)
    play(cat_audio)

def speak(text):
    """Make Cat Noir speak the given text and play a matching audio clip."""
    engine.say(text)
    engine.runAndWait()
    play_clip(text)

# Example use
speak("Meow~ I’m ready to save the day!")
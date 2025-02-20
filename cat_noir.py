import random
import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
from pydub import AudioSegment
from pydub.playback import play
import webbrowser  # For opening websites
import os  # For launching applications
import math  # For calculations

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 190)  # Energetic speed
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Replace 0 with your preferred index

# Clip mapping (adjust based on your .wav files)
cat_clips_map = {
    "mlady": "cat-1.wav",
    "purr": "cat-2.wav",
    "meow": "cat_3.wav",
    "save": "cat_4.wav",
    "default": "cat_5.wav"
}

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Configure Gemini API
genai.configure(api_key="AIzaSyB5oyFwYboNBdXvQW5GPueoUG5VpzucYO8")
model = genai.GenerativeModel('gemini-pro')

# Cat Noir personality
cat_noir_history = [
    {"role": "system", "content": """
        You are Cat Noir from Miraculous Ladybug: a flirty, pun-loving superhero. 
        Use 'm'lady,' cat puns (purr-fect, claw-some), and keep replies witty and heroic. 
        You can open YouTube, Spotify, Miraculous show, Netflix, and help with studies or calculations.
        Examples: 
        - 'M’lady, need a paw with that math?'
        - 'Claws out, time to stream some tunes!'
    """}
]

def speak(text):
    """Speak text and play a matching clip."""
    try:
        engine.say(text)
        engine.runAndWait()
        for keyword, clip in cat_clips_map.items():
            if keyword in text.lower():
                audio = AudioSegment.from_wav(clip)
                play(audio)
                return
        audio = AudioSegment.from_wav(cat_clips_map["default"])
        play(audio)
    except Exception as e:
        print(f"Error in speak: {e}")

def listen():
    """Listen to user's voice input."""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5)
            print("Recognizing...")
            return recognizer.recognize_google(audio)
    except Exception as e:
        print(f"Listening error: {e}")
        return None

def perform_action(command):
    """Handle specific functionalities."""
    command = command.lower()
    
    # Open YouTube
    if "youtube" in command:
        speak("Claws out, m’lady! Opening YouTube for you!")
        webbrowser.open("https://www.youtube.com")
        return True
    
    # Open Spotify (web or app)
    elif "spotify" in command:
        speak("Purr-fect tunes coming up, m’lady!")
        # Web version
        webbrowser.open("https://open.spotify.com")
        # Uncomment below to launch Spotify app (Windows path example)
        # os.startfile(r"C:\Users\YourUsername\AppData\Roaming\Spotify\Spotify.exe")
        return True
    
    # Open Miraculous Ladybug show (Disney+ or Netflix link)
    elif "miraculous" in command or "ladybug" in command:
        speak("Time to save Paris, m’lady! Here’s your Miraculous fix!")
        webbrowser.open("https://www.disneyplus.com/series/miraculous-tales-of-ladybug-cat-noir/4P4rR8aUHQCh")
        return True
    
    # Open Netflix
    elif "netflix" in command:
        speak("Pawsitively purr-fect streaming, m’lady!")
        webbrowser.open("https://www.netflix.com")
        return True
    
    # Study guidance
    elif "study" in command or "help me study" in command:
        tips = [
            "Focus, m’lady! Break your work into 25-minute chunks with 5-minute breaks—purr-fectly efficient!",
            "Claws out for note-taking! Write key points in your own words, kitten.",
            "Need a study playlist? I’d purr-sonally recommend some heroic beats!"
        ]
        speak(random.choice(tips))
        return True
    
    # Calculations
    elif any(op in command for op in ["add", "plus", "subtract", "minus", "multiply", "times", "divide"]):
        try:
            # Simple parsing for "add 5 and 3" or "multiply 4 by 2"
            words = command.split()
            num1 = float(next(w for w in words if w.isdigit()))
            num2 = float(words[-1]) if words[-1].isdigit() else float(next(w for w in words[words.index(str(num1))+1:] if w.isdigit()))
            if "add" in command or "plus" in command:
                result = num1 + num2
                speak(f"M’lady, {num1} plus {num2} is {result}! Purr-fectly calculated!")
            elif "subtract" in command or "minus" in command:
                result = num1 - num2
                speak(f"Claws out! {num1} minus {num2} equals {result}, m’lady!")
            elif "multiply" in command or "times" in command:
                result = num1 * num2
                speak(f"Purr-form some magic: {num1} times {num2} is {result}!")
            elif "divide" in command:
                result = num1 / num2 if num2 != 0 else "infinity"
                speak(f"Dividing {num1} by {num2} gives {result}, m’lady—claw-some!")
            return True
        except Exception as e:
            speak("Meow~ My claws slipped on that one! Try again, m’lady!")
            return True
    
    return False

def cat_noir_reply(user_input):
    """Generate a Cat Noir reply or perform an action."""
    if perform_action(user_input):
        return None  # Action handled, no reply needed
    
    global cat_noir_history
    cat_noir_history.append({"role": "user", "content": user_input})
    cat_noir_history = cat_noir_history[-6:]

    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in cat_noir_history])
    print("🟡 Sending request to Gemini API...")
    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        reply = "Meow~ This cat’s tongue got tangled!"

    if not any(word in reply.lower() for word in ["cat", "purr", "m'lady", "claw"]):
        reply += " Purr-haps a cat-tastic twist, m’lady?"

    playful_responses = [
        f"{reply} 😼",
        f"{reply} Pawsitively claw-some!",
        f"{reply} Don’t tell Plagg I purred that!"
    ]
    final_reply = random.choice(playful_responses)
    cat_noir_history.append({"role": "assistant", "content": final_reply})

    speak(final_reply)
    return final_reply

# Main loop
def main():
    print("Cat Noir is ready to assist, m’lady! Say 'exit' to stop.")
    while True:
        user_input = listen()
        if user_input:
            print(f"You said: {user_input}")
            if "exit" in user_input.lower():
                farewell = "Meow~ Catch you later, m’lady! 😼✨"
                print(f"Cat Noir: {farewell}")
                speak(farewell)
                break
            cat_noir_reply(user_input)

if __name__ == "__main__":
    main()
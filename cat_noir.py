import random
import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
from pydub import AudioSegment
from pydub.playback import play
import webbrowser
import os
import platform
import subprocess
import sqlite3
import spacy
import requests
from bs4 import BeautifulSoup
from sympy import symbols, solve, sympify

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 190)
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

# Load NLP model
nlp = spacy.load("en_core_web_sm")  # Install: pip install spacy; python -m spacy download en_core_web_sm

# Configure Gemini API
genai.configure(api_key=" ")
model = genai.GenerativeModel('gemini-pro')

# Persistent memory with SQLite
conn = sqlite3.connect("cat_noir_memory.db")
conn.execute("CREATE TABLE IF NOT EXISTS memory (command TEXT, response TEXT)")
conn.commit()

# Cat Noir personality
cat_noir_history = [
    {"role": "system", "content": """
        You are Cat Noir from Miraculous Ladybug: flirty, pun-loving, heroic. 
        Use 'm'lady,' cat puns (purr-fect, claw-some), and keep it witty. 
        You can open apps/websites, help with studies (especially computer topics), and solve math problems.
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

def save_memory(command, response):
    """Save user command and response to SQLite."""
    conn.execute("INSERT INTO memory VALUES (?, ?)", (command, response))
    conn.commit()

def open_app_or_web(command, doc):
    """Cross-platform app/website launching with NLP."""
    system = platform.system()
    if "youtube" in command:
        speak("Claws out, m’lady! Opening YouTube!")
        webbrowser.open("https://www.youtube.com")
        return True
    elif "spotify" in command:
        speak("Purr-fect tunes, m’lady!")
        if system == "Windows":
            try: os.startfile(r"C:\Users\YourUsername\AppData\Roaming\Spotify\Spotify.exe")  # Adjust path
            except: webbrowser.open("https://open.spotify.com")
        elif system == "Darwin":
            subprocess.run(["open", "-a", "Spotify"])
        elif system == "Linux":
            subprocess.run(["spotify"])
        return True
    elif "miraculous" in command or "ladybug" in command:
        speak("Time to save Paris, m’lady!")
        webbrowser.open("https://www.disneyplus.com/series/miraculous-tales-of-ladybug-cat-noir/4P4rR8aUHQCh")
        return True
    elif "netflix" in command:
        speak("Pawsitively purr-fect streaming!")
        webbrowser.open("https://www.netflix.com")
        return True
    return False

def study_help(command, doc):
    """Study help with computer science resources from GeeksforGeeks and JavaPoint."""
    
    # Extract verbs safely
    verbs = [token.text.lower() for token in doc if token.pos_ == "VERB"]
    
    # Check if the command is asking for study help
    if "study" in command or "help" in verbs:
        topic = next((token.text for token in reversed(doc) if token.pos_ == "NOUN"), "study tips")

        # Computer science keywords
        cs_keywords = ["computer", "programming", "code", "algorithm", "data", "software", "python", "java", "c++"]
        
        if any(keyword in command.lower() for keyword in cs_keywords) or topic.lower() in cs_keywords:
            # Try GeeksforGeeks
            gfg_url = f"https://www.geeksforgeeks.org/{topic.replace(' ', '-')}/"
            try:
                response = requests.get(gfg_url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    intro = soup.find("p").text[:200].strip() if soup.find("p") else "Check this out!"
                    speak(f"Purr-fect coding knowledge, m’lady! From GeeksforGeeks: {intro}")
                    webbrowser.open(gfg_url)
                    return True
            except requests.RequestException:
                pass  # Fallback to JavaPoint if GeeksforGeeks fails
            
            # Try JavaPoint
            jp_url = f"https://www.javatpoint.com/{topic.replace(' ', '-')}"
            try:
                response = requests.get(jp_url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    intro = soup.find("p").text[:200].strip() if soup.find("p") else "Learn this, kitten!"
                    speak(f"Claw-some tech info, m’lady! From JavaPoint: {intro}")
                    webbrowser.open(jp_url)
                    return True
            except requests.RequestException:
                speak("Meow~ Couldn’t fetch that tech topic! Try a simpler one, m’lady!")
                return True

        # Fallback to Wikipedia for non-CS topics
        try:
            wiki_url = f"https://en.wikipedia.org/wiki/{topic}"
            response = requests.get(wiki_url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                intro = soup.find("p").text[:200].strip() if soup.find("p") else "Interesting topic!"
                speak(f"Here’s a purr-fect nugget, m’lady: {intro}")
                webbrowser.open(wiki_url)
            else:
                speak("Meow~ Couldn’t claw that info! Try again, m’lady!")
        except requests.RequestException:
            speak("Meow~ Couldn’t claw that info! Try again, m’lady!")

        return True

    return False

def calculate(command, doc):
    """Advanced symbolic math with sympy and basic parsing."""
    if "calculate" in command or "solve" in command or any(t.pos_ == "NUM" for t in doc):
        try:
            if any(op in command for op in ["add", "plus", "subtract", "minus", "multiply", "times", "divide"]):
                nums = [float(token.text) for token in doc if token.pos_ == "NUM"]
                if len(nums) >= 2:
                    num1, num2 = nums[0], nums[1]
                    if "add" in command or "plus" in command:
                        result = num1 + num2
                        speak(f"{num1} plus {num2} is {result}, m’lady!")
                    elif "subtract" in command or "minus" in command:
                        result = num1 - num2
                        speak(f"{num1} minus {num2} equals {result}, claw-some!")
                    elif "multiply" in command or "times" in command:
                        result = num1 * num2
                        speak(f"{num1} times {num2} is {result}, purr-fect!")
                    elif "divide" in command:
                        result = num1 / num2 if num2 != 0 else "infinity"
                        speak(f"{num1} divided by {num2} is {result}, m’lady!")
                    return True
            elif "solve" in command:
                eq = command.split("solve")[1].strip().replace("=", "-")
                x = symbols('x')
                result = solve(sympify(eq), x)
                speak(f"Solved it, m’lady! The answer is {result}, claw-some!")
                return True
        except Exception as e:
            speak(f"Meow~ My claws slipped on that math! Try again, m’lady!")
            return True
    return False

def cat_noir_reply(user_input):
    """Process input with NLP and perform actions or reply."""
    doc = nlp(user_input.lower())
    
    # Check memory for past responses
    cursor = conn.execute("SELECT response FROM memory WHERE command = ?", (user_input,))
    past_response = cursor.fetchone()
    if past_response:
        speak(f"Remember this, m’lady? {past_response[0]}")
        return past_response[0]

    # Handle specific actions
    if open_app_or_web(user_input, doc):
        return None
    if study_help(user_input, doc):
        return None
    if calculate(user_input, doc):
        return None

    # Fallback to Gemini API
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

    final_reply = random.choice([f"{reply} 😼", f"{reply} Pawsitively claw-some!"])
    save_memory(user_input, final_reply)
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
                conn.close()
                break
            cat_noir_reply(user_input)

if __name__ == "__main__":
    main()

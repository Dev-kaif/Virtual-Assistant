import speech_recognition as sr
import requests
import pyjokes
import sys
import webbrowser
import random
from youtubesearchpython import VideosSearch
from googleapiclient.discovery import build
import google.generativeai as genai
from pydub import AudioSegment
from pydub.playback import play
import io

# API keys
YOUTUBE_API_KEY = 'AIzaSyAuDhKY-KP1zGzTUosNTcWM5j1Yt2RrCus'
GEMINI_API_KEY = 'AIzaSyC28Uzj9xiOIBuXh0Xwao6yhKOfKfpxCYU'
ELEVENLABS_API_KEY = 'sk_6e1cdfcd5ed9c6985206781f40261c5870305de4e23ccce5'

# Initialize the recognizer
recognizer = sr.Recognizer()

# List of curses or harsh phrases
curses = [
    "Fuck you, {name}.",
    "{name}, you dick head.",
    "{name}, you son of a bitch.",
    "{name}, asshole.",
    "{name}, motherfucking bastard.",
    "Piss off, {name}."
]

# Function to convert text to speech using 11labs API
def speak(text):
    """Convert text to speech using 11labs API."""
    try:
        url = 'https://api.elevenlabs.io/v1/text-to-speech'
        headers = {
            'Authorization': f'Bearer {ELEVENLABS_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            "text": text,
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
            }
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        audio_content = response.content
        audio = AudioSegment.from_file(io.BytesIO(audio_content), format="mp3")
        play(audio)
    except requests.exceptions.RequestException as e:
        print(f"Error calling 11labs API: {e}")
        print(response.json())

# Function to get a joke
def get_joke():
    """Return a joke."""
    return pyjokes.get_joke()

# Function to search and play a song on YouTube
def search_and_play_song(song_name):
    """Search for a song on YouTube and play it."""
    try:
        videos_search = VideosSearch(song_name, limit=1)
        result = videos_search.result()
        video_url = result['result'][0]['link']
        webbrowser.get('brave').open(video_url)
    except Exception as e:
        print(f"Error playing song: {e}")
        speak("Sorry, I couldn't find the song.")

# Function to play a random trending song on YouTube
def play_random_trending_song():
    """Play a random trending song on YouTube."""
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode="US",
            videoCategoryId="10",  # Music category
            maxResults=50
        )
        response = request.execute()
        video = random.choice(response['items'])
        video_url = f"https://www.youtube.com/watch?v={video['id']}"
        webbrowser.get('brave').open(video_url)
    except Exception as e:
        print(f"Error playing random trending song: {e}")
        speak("Sorry, I couldn't play a random trending song.")

# Function to search Google
def search_google(query):
    """Search Google."""
    search_url = f"https://www.google.com/search?q={query}"
    webbrowser.get('brave').open(search_url)

# Function to randomly curse at a given name three times
def curse_name(name):
    """Randomly curse at the provided name three times."""
    for _ in range(3):
        curse = random.choice(curses).format(name=name)
        speak(curse)

def call_google_gemini(input_text):
    """Call Google Gemini API with the given input text and return the response."""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(input_text)
        return response.text
    except Exception as e:
        error_msg = f"Error calling Google Gemini API: {e}"
        print(error_msg)
        return error_msg

def listen_for_wake_word(wake_word="raven"):
    """Listen for the wake word."""
    while True:
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise... Please wait.")
                recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for ambient noise
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=5)
                print("Recognizing speech...")
                word = recognizer.recognize_google(audio)
                print(f"You said: {word}")
                if wake_word in word.lower():
                    speak("Yes, I am listening")
                    return True
                elif "stop" in word.lower() or "kill" in word.lower():
                    speak("Stopping")
                    sys.exit()  # Exit the entire program
        except sr.UnknownValueError:
            print("Could not understand the audio")
        except Exception as e:
            print(f"Error: {e}")
            speak("Please say Raven")

def command(word):
    """Process the recognized command word."""
    if "stop" in word.lower() or "kill" in word.lower():
         speak("Stopping")
         sys.exit()  # Exit the entire program
    elif "joke" in word.lower():
        speak(get_joke())
    elif "open google" in word.lower():
        webbrowser.get('brave').open("https://www.google.com/")
    elif "open facebook" in word.lower():
        webbrowser.get('brave').open("https://facebook.com")
    elif "open youtube" in word.lower():
        webbrowser.get('brave').open("https://youtube.com")
    elif "open linkedin" in word.lower():
        webbrowser.get('brave').open("https://linkedin.com")
    elif "random song" in word.lower():
        speak("Playing a random trending song from YouTube")
        play_random_trending_song()    
    elif "play" in word.lower():
        song_name = word.lower().replace("play", "").strip()
        search_and_play_song(song_name)
    elif "search" in word.lower():
        query = word.lower().replace("search", "").strip()
        speak(f"Searching Google for {query}")
        search_google(query)
    elif "curse" in word.lower():
        name = word.lower().replace("curse", "").strip()
        speak(f"Cursing at {name}")
        curse_name(name)
    else:
        input_text = word.lower().replace("gemini", "").strip()
        try:
            response = call_google_gemini(input_text)
            print(response)
            speak(response)
        except Exception as e:
            error_msg = f"Error: {e}"
            print(error_msg)
            speak(error_msg)

def listen_for_commands():
    """Listen for commands after the wake word is detected."""
    while True:
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise... Please wait.")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                audio = recognizer.listen(source, timeout=2, phrase_time_limit=5)
                print("Recognizing speech...")
                word = recognizer.recognize_google(audio)
                print(f"You said: {word}")
            command(word)
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
        except sr.UnknownValueError:
            print("Could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Web Speech API; {e}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function to start the assistant."""
    speak("Initializing Raven...")
    while True:
        if listen_for_wake_word():
            listen_for_commands()

if __name__ == "__main__":
    brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    try:
        webbrowser.register('brave', None, webbrowser.BackgroundBrowser(brave_path))
        print("Brave browser registered successfully.")
    except webbrowser.Error as e:
        print(f"Failed to register Brave browser: {e}")
    main()

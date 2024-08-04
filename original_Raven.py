import speech_recognition as sr
import pyttsx3
import sys
import webbrowser
import random
from youtubesearchpython import VideosSearch
from googleapiclient.discovery import build
import google.generativeai as genai

class RavenVoiceAssistant:
    # API keys
    YOUTUBE_API_KEY = ''
    GEMINI_API_KEY = ''

    def __init__(self):
        # Initialize the recognizer and text-to-speech engine
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 190)  # Set the speaking rate

        # List available voices and select one
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)  # Change the index to the voice you prefer

        # List of curses or harsh phrases
        self.curses = [
            "Fuck you, {name}.",
            "{name}, you dick head.",
            "{name}, you son of a bitch.",
            "{name}, asshole.",
            "{name}, motherfucking bastard.",
            "Piss off, {name}."
        ]

    def speak(self, text):
        """Convert text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()

    def search_and_play_song(self, song_name):
        """Search for a song on YouTube and play it."""
        try:
            videos_search = VideosSearch(song_name, limit=1)
            result = videos_search.result()
            video_url = result['result'][0]['link']
            webbrowser.open(video_url)  # Use default browser
        except Exception as e:
            print(f"Error playing song: {e}")
            self.speak("Sorry, I couldn't find the song.")

    def play_random_trending_song(self):
        """Play a random trending song on YouTube."""
        try:
            youtube = build('youtube', 'v3', developerKey=self.YOUTUBE_API_KEY)
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
            webbrowser.open(video_url)  # Use default browser
        except Exception as e:
            print(f"Error playing random trending song: {e}")
            self.speak("Sorry, I couldn't play a random trending song.")

    def search_google(self, query):
        """Search Google using default browser."""
        search_url = f"https://www.google.com/search?q={query}"
        webbrowser.open(search_url)  # Use default browser

    def curse_name(self, name):
        """Randomly curse at the provided name three times."""
        for _ in range(3):
            curse = random.choice(self.curses).format(name=name)
            self.speak(curse)

    def call_google_gemini(self, input_text):
        """Call Google Gemini API with the given input text and return a short response."""
        try:
            genai.configure(api_key=self.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Adjust the prompt to request a brief response
            prompt = f"Please answer the following query briefly: {input_text}"
            
            # Generate response
            response = model.generate_content(prompt)
            
            return response.text
        except Exception as e:
            error_msg = f"Error calling Google Gemini API: {e}"
            print(error_msg)
            return error_msg

    def listen_for_wake_word(self, wake_word="raven"):
        """Listen for the wake word."""
        while True:
            try:
                with sr.Microphone() as source:
                    print("Adjusting for ambient noise... Please wait.")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for ambient noise
                    print("Listening for wake word...")
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    print("Recognizing speech...")
                    word = self.recognizer.recognize_google(audio)
                    print(f"You said: {word}")
                    if wake_word in word.lower():
                        self.speak("Yes, I am listening")
                        return True
                    elif "stop" in word.lower() or "kill" in word.lower():
                        self.speak("Stopping")
                        sys.exit()  # Exit the entire program
            except sr.UnknownValueError:
                print("Could not understand the audio")
            except Exception as e:
                print(f"Error: {e}")
                self.speak("Please say Raven")

    def command(self, word):
        """Process the recognized command word."""
        if "stop" in word.lower() or "kill" in word.lower():
            self.speak("Stopping")
            sys.exit()  # Exit the entire program
        elif "open google" in word.lower():
            webbrowser.open("https://www.google.com/")  # Use default browser
        elif "open facebook" in word.lower():
            webbrowser.open("https://facebook.com")  # Use default browser
        elif "open youtube" in word.lower():
            webbrowser.open("https://youtube.com")  # Use default browser
        elif "open linkedin" in word.lower():
            webbrowser.open("https://linkedin.com")  # Use default browser
        elif "random song" in word.lower():
            self.speak("Playing a random trending song from YouTube")
            self.play_random_trending_song()    
        elif "play" in word.lower():
            song_name = word.lower().replace("play", "").strip()
            self.search_and_play_song(song_name)
        elif "search" in word.lower():
            query = word.lower().replace("search", "").strip()
            self.speak(f"Searching Google for {query}")
            self.search_google(query)
        elif "curse" in word.lower():
            name = word.lower().replace("curse", "").strip()
            self.speak(f"Cursing at {name}")
            self.curse_name(name)
        elif "tell me" in word:
            input_text = word.lower().replace("gemini", "").strip()
            try:
                response = self.call_google_gemini(input_text)
                print(response)
                self.speak(response)
            except Exception as e:
                error_msg = f"Error: {e}"
                print(error_msg)
                self.speak(error_msg)

    def listen_for_commands(self):
        """Listen for commands after the wake word is detected."""
        while True:
            try:
                with sr.Microphone() as source:
                    print("Adjusting for ambient noise... Please wait.")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    print("Listening...")
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    print("Recognizing speech...")
                    word = self.recognizer.recognize_google(audio)
                    print(f"You said: {word}")
                self.command(word)
            except sr.WaitTimeoutError:
                print("Listening timed out while waiting for phrase to start")
            except sr.UnknownValueError:
                print("Could not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Web Speech API; {e}")
            except Exception as e:
                print(f"Error: {e}")

    def main(self):
        """Main function to start the assistant."""
        self.speak("Initializing Raven...")
        while True:
            if self.listen_for_wake_word():
                self.listen_for_commands()

if __name__ == "__main__":
    assistant = RavenVoiceAssistant()
    assistant.main()

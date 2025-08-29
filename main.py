import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import sys
import requests
import json
import random
from threading import Thread
import time
import openai
from openai import OpenAI

class JARVIS:
    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)  # Speed of speech
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize OpenAI client
        self.openai_client = None
        self.setup_openai()
        
        # Conversation history for context
        self.conversation_history = []
        
        # Calibrate microphone for ambient noise
        print("Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        print("JARVIS initialized successfully!")
        self.speak("Good day sir, JARVIS is online and ready to assist you.")
    
    def setup_openai(self):
        """Initialize OpenAI client with API key"""
        api_key = os.getenv('OPENAI_API_KEY') or "YOUR_OPENAI_API_KEY_HERE"
        
        if api_key and api_key != "YOUR_OPENAI_API_KEY_HERE":
            try:
                self.openai_client = OpenAI(api_key=api_key)
                print("OpenAI client initialized successfully!")
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}")
                self.openai_client = None
        else:
            print("OpenAI API key not found. AI chat features will be limited.")
            self.openai_client = None
    
    def chat_with_gpt(self, message, use_jarvis_personality=True):
        """Send message to ChatGPT and get response"""
        if not self.openai_client:
            return "I'm sorry sir, my advanced AI capabilities are currently offline. Please configure the OpenAI API key."
        
        try:
            # System message to maintain JARVIS personality
            system_message = {
                "role": "system",
                "content": "You are JARVIS, Tony Stark's AI assistant. Respond in a polite, sophisticated, and helpful manner. Address the user as 'sir' and maintain the persona of an advanced AI butler. Keep responses concise but informative, suitable for text-to-speech output."
            } if use_jarvis_personality else {
                "role": "system",
                "content": "You are a helpful AI assistant. Provide clear, concise responses suitable for text-to-speech output."
            }
            
            # Add conversation history for context (keep last 6 messages)
            messages = [system_message]
            if len(self.conversation_history) > 6:
                messages.extend(self.conversation_history[-6:])
            else:
                messages.extend(self.conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            # Get response from OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can change to "gpt-4" if you have access
                messages=messages,
                max_tokens=150,  # Keep responses concise for speech
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except openai.RateLimitError:
            return "I'm sorry sir, I've reached my API rate limit. Please try again in a moment."
        except openai.AuthenticationError:
            return "I'm sorry sir, there seems to be an authentication issue with my AI services."
        except Exception as e:
            return f"I encountered an error while processing your request, sir: {str(e)[:100]}"
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        return "Conversation history cleared, sir. We can start fresh."
    
    def get_ai_response(self, query):
        """Get AI response for general queries"""
        # Check if it's a command that should be handled by built-in functions
        query_lower = query.lower()
        
        # Skip ChatGPT for specific system commands
        skip_gpt_keywords = [
            'time', 'clock', 'date', 'today', 'open youtube', 'open google', 
            'open github', 'system status', 'system info', 'exit', 'quit', 
            'goodbye', 'bye', 'clear history'
        ]
        
        if any(keyword in query_lower for keyword in skip_gpt_keywords):
            return None  # Let the main command processor handle it
        
        # Use ChatGPT for general conversation and complex queries
        return self.chat_with_gpt(query)
        """Convert text to speech"""
        print(f"JARVIS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """Listen for voice commands"""
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Processing...")
            command = self.recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
            
        except sr.RequestError:
            self.speak("Sorry sir, I'm having trouble connecting to the speech recognition service.")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.WaitTimeoutError:
            print("Listening timeout")
            return None
    
    def get_time(self):
        """Get current time"""
        now = datetime.datetime.now()
        time_string = now.strftime("%I:%M %p")
        return f"The current time is {time_string}"
    
    def get_date(self):
        """Get current date"""
        now = datetime.datetime.now()
        date_string = now.strftime("%B %d, %Y")
        return f"Today is {date_string}"
    
    def search_wikipedia(self, query):
        """Search Wikipedia for information"""
        try:
            self.speak("Searching Wikipedia...")
            results = wikipedia.summary(query, sentences=2)
            return results
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple results found. Did you mean: {e.options[0]}?"
        except wikipedia.exceptions.PageError:
            return "Sorry, I couldn't find any information on that topic."
        except Exception as e:
            return "Sorry, I encountered an error while searching Wikipedia."
    
    def open_website(self, url):
        """Open a website in the default browser"""
        try:
            webbrowser.open(url)
            return "Opening website now."
        except Exception as e:
            return "Sorry, I couldn't open that website."
    
    def get_weather(self, city="New York"):
        """Get weather information (requires API key)"""
        # Note: You'll need to get a free API key from OpenWeatherMap
        api_key = "YOUR_API_KEY_HERE"
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        
        if api_key == "YOUR_API_KEY_HERE":
            return "Weather service requires API key configuration."
        
        try:
            complete_url = base_url + "appid=" + api_key + "&q=" + city
            response = requests.get(complete_url)
            data = response.json()
            
            if data["cod"] != "404":
                main = data["main"]
                weather_desc = data["weather"][0]["description"]
                temperature = round(main["temp"] - 273.15)  # Convert from Kelvin to Celsius
                
                return f"The weather in {city} is {weather_desc} with a temperature of {temperature} degrees Celsius."
            else:
                return "City not found."
        except Exception as e:
            return "Sorry, I couldn't fetch the weather information."
    
    def system_status(self):
        """Get basic system information"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            return f"System status: CPU usage is {cpu_percent}%, Memory usage is {memory_percent}%"
        except ImportError:
            return "System monitoring requires psutil package. Install with: pip install psutil"
    
    def tell_joke(self):
        """Tell a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why don't programmers like nature? It has too many bugs!",
            "I'm reading a book about anti-gravity. It's impossible to put down!",
            "Why do Java developers wear glasses? Because they don't C#!"
        ]
        return random.choice(jokes)
    
    def calculate(self, expression):
        """Perform basic calculations"""
        try:
            # Remove any non-mathematical characters for safety
            allowed_chars = "0123456789+-*/.() "
            cleaned_expr = ''.join(c for c in expression if c in allowed_chars)
            
            if cleaned_expr:
                result = eval(cleaned_expr)
                return f"The answer is {result}"
            else:
                return "Invalid mathematical expression."
        except Exception as e:
            return "Sorry, I couldn't calculate that expression."
    
    def process_command(self, command):
        """Process voice commands and execute appropriate functions"""
        if not command:
            return
        
        # Time commands
        if any(word in command for word in ['time', 'clock']):
            response = self.get_time()
        
        # Date commands
        elif any(word in command for word in ['date', 'today']):
            response = self.get_date()
        
        # Wikipedia search
        elif 'wikipedia' in command or 'search for' in command:
            query = command.replace('wikipedia', '').replace('search for', '').strip()
            response = self.search_wikipedia(query)
        
        # Website opening
        elif 'open youtube' in command:
            response = self.open_website('https://youtube.com')
        elif 'open google' in command:
            response = self.open_website('https://google.com')
        elif 'open github' in command:
            response = self.open_website('https://github.com')
        
        # Weather
        elif 'weather' in command:
            city = command.replace('weather', '').replace('in', '').strip()
            if not city:
                city = "New York"
            response = self.get_weather(city)
        
        # System status
        elif 'system status' in command or 'system info' in command:
            response = self.system_status()
        
        # Jokes
        elif 'joke' in command or 'funny' in command:
            response = self.tell_joke()
        
        # Calculator
        elif any(word in command for word in ['calculate', 'compute', 'math']):
            expression = command.replace('calculate', '').replace('compute', '').replace('math', '').strip()
            response = self.calculate(expression)
        
        # Clear conversation history
        elif 'clear history' in command or 'reset conversation' in command:
            response = self.clear_conversation_history()
        
        # ChatGPT Integration - Handle general AI queries
        elif any(word in command for word in ['ask', 'question', 'explain', 'how', 'what', 'why', 'when', 'where', 'who']):
            # Remove trigger words and send to ChatGPT
            clean_query = command.replace('ask', '').replace('question', '').strip()
            if not clean_query:
                clean_query = command
            response = self.get_ai_response(clean_query)
            if not response:
                # If ChatGPT didn't handle it, fall back to default response
                response = "I'm not sure how to help with that, sir. Could you be more specific?"
        
        # Greeting
        elif any(word in command for word in ['hello', 'hi', 'hey']):
            responses = [
                "Hello sir, how may I assist you today?",
                "Good to see you sir, what can I do for you?",
                "At your service, sir. How may I help?"
            ]
            response = random.choice(responses)
        
        # Exit commands
        elif any(word in command for word in ['exit', 'quit', 'goodbye', 'bye']):
            response = "Goodbye sir, it was a pleasure assisting you."
            self.speak(response)
            return False
        
        # Default response for unrecognized commands - Try ChatGPT first
        else:
            # Try to get AI response for unrecognized commands
            ai_response = self.get_ai_response(command)
            if ai_response and "API" not in ai_response and "error" not in ai_response.lower():
                response = ai_response
            else:
                # Fall back to default responses
                responses = [
                    "I'm sorry sir, I didn't understand that command.",
                    "Could you please repeat that, sir?",
                    "I'm not sure what you mean, sir. Could you rephrase that?",
                    "I didn't catch that, sir. Please try again."
                ]
                response = random.choice(responses)
        
        self.speak(response)
        return True
    
    def run(self):
        """Main loop to run JARVIS"""
        print("\n" + "="*50)
        print("JARVIS AI Assistant is now running!")
        print("Say 'exit', 'quit', or 'goodbye' to stop.")
        print("="*50 + "\n")
        
        while True:
            try:
                command = self.listen()
                if command:
                    continue_running = self.process_command(command)
                    if not continue_running:
                        break
                else:
                    # If no command was recognized, continue listening
                    time.sleep(0.5)
                    
            except KeyboardInterrupt:
                self.speak("Goodbye sir.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                self.speak("I encountered an error, but I'm still operational.")

# Installation requirements and usage instructions
def print_requirements():
    """Print installation requirements"""
    print("\n" + "="*60)
    print("JARVIS AI Assistant Setup Requirements:")
    print("="*60)
    print("\n1. Install required packages:")
    print("   pip install speechrecognition pyttsx3 wikipedia requests openai")
    print("   pip install pyaudio  # For microphone input")
    print("   pip install psutil   # For system monitoring (optional)")
    print("\n2. For ChatGPT functionality:")
    print("   - Get API key from: https://platform.openai.com/api-keys")
    print("   - Set environment variable: export OPENAI_API_KEY='your-key-here'")
    print("   - Or replace 'YOUR_OPENAI_API_KEY_HERE' in the code")
    print("\n3. For weather functionality:")
    print("   - Get free API key from: https://openweathermap.org/api")
    print("   - Replace 'YOUR_API_KEY_HERE' in the code")
    print("\n3. Make sure your microphone is working properly")
    print("\n4. Available Commands:")
    print("   - 'What time is it?' / 'Tell me the time'")
    print("   - 'What's the date?' / 'What day is today?'")
    print("   - 'Search for [topic]' / 'Wikipedia [topic]'")
    print("   - 'Open YouTube/Google/GitHub'")
    print("   - 'What's the weather?' / 'Weather in [city]'")
    print("   - 'System status' / 'System info'")
    print("   - 'Tell me a joke'")
    print("   - 'Calculate [expression]' / 'Math [expression]'")
    print("   - 'Hello' / 'Hi' (greetings)")
    print("   - 'Clear history' / 'Reset conversation'")
    print("   - 'Ask [question]' / 'Explain [topic]' (ChatGPT)")
    print("   - General conversation and questions (ChatGPT)")
    print("   - 'Exit' / 'Quit' / 'Goodbye' (to stop)")
    print("="*60 + "\n")

# Main execution
if __name__ == "__main__":
    print_requirements()
    
    try:
        # Create and run JARVIS
        jarvis = JARVIS()
        jarvis.run()
        
    except KeyboardInterrupt:
        print("\nJARVIS shutdown initiated by user.")
    except Exception as e:
        print(f"\nFailed to initialize JARVIS: {e}")
        print("Please make sure all required packages are installed.")
        print("Run: pip install speechrecognition pyttsx3 wikipedia requests pyaudio")
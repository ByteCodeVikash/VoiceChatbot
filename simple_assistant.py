# simple_assistant.py
import numpy as np
import sounddevice as sd
from config import PHRASES

def beep():
    """Play a simple beep tone"""
    print("Playing beep...")
    sample_rate = 22050
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration))
    sine_wave = 0.3 * np.sin(2 * np.pi * 440 * t)
    sd.play(sine_wave, sample_rate)
    sd.wait()

def main():
    """Run a simplified assistant using beeps instead of TTS"""
    print("Starting simplified assistant...")
    
    # Speak initial prompt (use beep instead)
    language = "english"
    prompt = PHRASES["select_language"][language]
    print(f"[{language.upper()}]: {prompt}")
    beep()
    
    # Get language selection (simulate with input)
    user_input = input("Your language choice (english/hindi/hinglish): ")
    
    if user_input.lower() in ["english", "hindi", "hinglish"]:
        language = user_input.lower()
    else:
        language = "english"
    
    # Confirm language selection
    confirmation = PHRASES["language_selected"][language]
    print(f"[{language.upper()}]: {confirmation}")
    beep()
    
    # Say welcome
    welcome = PHRASES["welcome"][language]
    print(f"[{language.upper()}]: {welcome}")
    beep()
    
    # Ask for name
    ask_name = PHRASES["ask_name"][language]
    print(f"[{language.upper()}]: {ask_name}")
    beep()
    
    name = input("Your name: ")
    
    # Thank the user
    thank_you = PHRASES["thank_you"][language].format(name)
    print(f"[{language.upper()}]: {thank_you}")
    beep()
    
    # Ask for occupation
    ask_occupation = PHRASES["ask_occupation"][language]
    print(f"[{language.upper()}]: {ask_occupation}")
    beep()
    
    occupation = input("Your occupation/location: ")
    
    # Main conversation loop
    while True:
        ask_query = PHRASES["ask_query"][language]
        print(f"[{language.upper()}]: {ask_query}")
        beep()
        
        query = input("Your query (type 'exit' to quit): ")
        if query.lower() == "exit":
            break
        
        # Simulate response
        response = PHRASES["schemes_intro"][language] + "\n\n"
        response += "**1. Sample Scheme**\n"
        response += "Description: This is a sample scheme for demonstration.\n\n"
        
        print(f"[{language.upper()}]: {response}")
        beep()
        
        anything_else = PHRASES["anything_else"][language]
        print(f"[{language.upper()}]: {anything_else}")
        beep()
        
    # Closing
    closing = PHRASES["closing"][language].format(name)
    print(f"[{language.upper()}]: {closing}")
    beep()
    
    print("Simplified assistant finished.")

if __name__ == "__main__":
    main()
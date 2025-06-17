import speech_recognition as sr
import winsound
import pygame
import time
import os
import numpy as np
import scipy.io.wavfile as wav

# ✅ Initialize pygame mixer once
pygame.mixer.init()
SOUND_FOLDER = "sounds"

# ✅ Morse Code Dictionary
MORSE_CODE_DICT = {
    'A': '.-',    'B': '-...',  'C': '-.-.', 'D': '-..',   'E': '.',
    'F': '..-.',  'G': '--.',   'H': '....', 'I': '..',    'J': '.---',
    'K': '-.-',   'L': '.-..',  'M': '--',   'N': '-.',    'O': '---',
    'P': '.--.',  'Q': '--.-',  'R': '.-.',  'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',  'X': '-..-',  'Y': '-.--',
    'Z': '--..',  '1': '.----', '2': '..---','3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..','9': '----.',
    '0': '-----', ' ': '/', ',': '--..--', '.': '.-.-.-', '?': '..--..'
}

# ✅ Inverted Morse Dictionary
INVERSE_MORSE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}

def text_to_morse(text):
    return ' '.join(MORSE_CODE_DICT.get(char, '') for char in text.upper())

def morse_to_text(morse):
    words = morse.strip().split(' / ')
    decoded = []
    for word in words:
        letters = word.split()
        decoded_word = ''.join(INVERSE_MORSE_DICT.get(l, '') for l in letters)
        decoded.append(decoded_word)
    return ' '.join(decoded)

def play_morse_code(morse_code):
    DOT_DURATION = 100
    DASH_DURATION = 300
    FREQ = 750
    GAP = 0.1

    for symbol in morse_code:
        if symbol == '.':
            winsound.Beep(FREQ, DOT_DURATION)
        elif symbol == '-':
            winsound.Beep(FREQ, DASH_DURATION)
        elif symbol == ' ':
            time.sleep(GAP)
        elif symbol == '/':
            time.sleep(0.5)

def play_letter_sounds(text):
    for char in text.upper():
        if char.isalnum():
            file_path = os.path.join(SOUND_FOLDER, f"{char}.wav")
            if os.path.exists(file_path):
                try:
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                except Exception as e:
                    print(f"❌ Error playing {char}: {e}")
            else:
                print(f"⚠️ Missing sound file: {file_path}")

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak something in English...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"📝 You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
    except sr.RequestError:
        print("⚠️ Speech recognition service error.")
    return ""

def speech_to_morse_string():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak your Morse (say 'dot dash slash')...")
        audio = recognizer.listen(source)
    try:
        spoken = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {spoken}")
        return spoken.lower().replace("dot", ".").replace("dash", "-").replace("slash", "/")
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
    except sr.RequestError:
        print("⚠️ Speech recognition service error.")
    return ""

# ✅ Decode Morse audio beeps using signal analysis
def audiofile_to_morse_string(filepath):
    try:
        rate, data = wav.read(filepath)
        if len(data.shape) == 2:
            data = data[:, 0]
        data = data / np.max(np.abs(data))

        frame_size = int(rate * 0.02)
        energy = np.array([np.sum(np.abs(data[i:i+frame_size])) for i in range(0, len(data), frame_size)])

        high_threshold = np.max(energy) * 0.5
        signal = energy > high_threshold

        durations = []
        current = signal[0]
        count = 1
        for s in signal[1:]:
            if s == current:
                count += 1
            else:
                durations.append((current, count))
                current = s
                count = 1
        durations.append((current, count))

        unit_samples = min([d for state, d in durations if state])
        morse_string = ""
        for is_beep, duration in durations:
            units = round(duration / unit_samples)
            if is_beep:
                morse_string += "." if units <= 2 else "-"
            else:
                if units >= 7:
                    morse_string += " / "
                elif units >= 3:
                    morse_string += " "
        print(f"📡 Decoded Morse: {morse_string}")
        return morse_string
    except Exception as e:
        print(f"❌ Error decoding Morse from audio: {e}")
        return ""

def main():
    print("\n📡 MORSE CODE TRANSLATOR")
    print("1. English text → Morse")
    print("2. English speech → Morse")
    print("3. Morse text → English")
    print("4. Spoken Morse → English\n")

    choice = input("Select an option (1-4): ")

    if choice == "1":
        user_text = input("Enter English text: ")
        morse = text_to_morse(user_text)
        print(f"📡 Morse Code:\n{morse}")
        play_mode = input("🔊 Play as (1) Morse beeps or (2) .wav letter sounds? ").strip()
        if play_mode == "1":
            play_morse_code(morse)
        elif play_mode == "2":
            play_letter_sounds(user_text)

    elif choice == "2":
        user_text = speech_to_text()
        if user_text:
            morse = text_to_morse(user_text)
            print(f"📡 Morse Code:\n{morse}")
            play_mode = input("🔊 Play as (1) Morse beeps or (2) .wav letter sounds? ").strip()
            if play_mode == "1":
                play_morse_code(morse)
            elif play_mode == "2":
                play_letter_sounds(user_text)

    elif choice == "3":
        morse_input = input("Enter Morse Code (use / for space): ")
        text = morse_to_text(morse_input)
        print(f"🔤 English Text:\n{text}")

    elif choice == "4":
        print("🎧 Choose input type:")
        print("   1. Microphone")
        print("   2. Pre-recorded audio file")
        sub_choice = input("Select (1 or 2): ").strip()

        morse_string = ""
        if sub_choice == "1":
            morse_string = speech_to_morse_string()
        elif sub_choice == "2":
            file_path = input("Enter path to audio file (e.g., audio.wav): ").strip()
            morse_string = audiofile_to_morse_string(file_path)
        else:
            print("❌ Invalid sub-option.")

        if morse_string:
            text = morse_to_text(morse_string)
            print(f"🔤 English Text:\n{text}")

    else:
        print("❌ Invalid choice.")

if __name__ == "__main__":
    main()

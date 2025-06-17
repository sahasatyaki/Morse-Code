# Morse Code Translator & Audio Toolkit

A comprehensive Python application that converts English text or speech to Morse code—and back—while also supporting audio generation, real‑time beep playback, waveform visualisation, and batch decoding from `.wav` files. Built for hobbyists, educators, amateur radio enthusiasts, and anyone curious about digital signal processing, this project is delivered as a single script for maximum portability yet organised as a full‑featured library.

---

## Table of Contents

1. [Features](#features)  
2. [Quick Start](#quick-start)  
3. [Command‑Line Menu](#command-line-menu)  
4. [Library API](#library-api)  
5. [How It Works](#how-it-works)  
6. [Project Structure](#project-structure)  
7. [Requirements](#requirements)  
8. [Troubleshooting](#troubleshooting)  
9. [Roadmap](#roadmap)  
10. [Contributing](#contributing)  
11. [License & Ownership](#license--ownership)  
12. [Author & Contact](#author--contact)

---

## Features

* **Bidirectional conversion** – Translate English text to Morse code and vice versa.  
* **Speech recognition input** – Dictate English sentences or *spoken* “dot dash slash” Morse phrases via microphone.  
* **Interactive CLI menu** – Perform common tasks quickly from an intuitive numbered prompt.  
* **Audio generation** – Render high‑quality `.wav` files of encoded Morse with configurable frequency and timing.  
* **Live beep playback** – Hear dits and dahs in real time using the Windows `winsound` API.  
* **Letter pronunciation** – Optionally play `.wav` recordings of individual A–Z/0–9 characters.  
* **Waveform analysis** – Visualise amplitude and energy envelopes of any audio file for debugging.  
* **Automatic Morse unit estimation** – Adaptive decoder that measures beep/silence durations to infer dot length automatically.  
* **Pure‑Python, no C extensions** – Cross‑platform except for the Windows‑specific beep mode.  
* **Modular library** – All core logic is encapsulated in functions you can import elsewhere.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your‑username>/Morse-Code.git
cd Morse-Code
```

### 2. Create a virtual environment (optional but recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # PowerShell: .venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note** : `winsound` ships with CPython on Windows; on Linux/macOS the *beep* playback fallback is to `pygame` letter sounds or generated `.wav` files.

### 4. Run the program

```bash
python morse.py
```

### 5. Example session

```
 MORSE CODE TRANSLATOR
 1. English text → Morse
 2. English speech → Morse
 3. Morse text → English
 4. Spoken Morse → English
 5. Generate Morse .wav from text
 6. Plot waveform of .wav file

Select an option (1‑6): 1
Enter English text: SOS
Morse Code:
... --- ...
Play as (1) Morse beeps or (2) .wav letter sounds? 1
```

---

## Command‑Line Menu

The script launches an interactive prompt in `main()` that offers six high‑level tasks:

| Option | Action | Key Functions Called |
| ------ | ------ | -------------------- |
| **1** | Convert **English text** → Morse | `text_to_morse`, `play_morse_code` or `play_letter_sounds` |
| **2** | Convert **English speech** (microphone) → Morse | `speech_to_text`, `text_to_morse`, playback |
| **3** | Convert **typed Morse** → English | `morse_to_text` |
| **4** | Convert **spoken Morse** (microphone or file) → English | `speech_to_morse_string` or `audiofile_to_morse_string`, then `morse_to_text` |
| **5** | **Generate `.wav`** file from text | `generate_morse_audio` |
| **6** | **Plot waveform** for inspection | `plot_waveform` |

All menu logic lives in the `main()` function for clarity and is completely decoupled from the library layer.

---

## Library API

Import individual utilities in your own projects:

```python
from morse_translator import (
    text_to_morse,
    morse_to_text,
    speech_to_text,
    speech_to_morse_string,
    audiofile_to_morse_string,
    generate_morse_audio,
    plot_waveform,
)
```

| Function Name | Signature | Purpose |
| ------------- | --------- | ------- |
| `text_to_morse` | `(text: str) → str` | Encodes alphanumeric & punctuation to Morse with spaces between letters and `/` between words. |
| `morse_to_text` | `(morse: str) → str` | Decodes Morse (with or without spaces) back to English. Internally auto‑inserts spaces when a continuous pattern is supplied. |
| `speech_to_text` | `() → str` | Records microphone input and returns recognised English via Google Web Speech API. |
| `speech_to_morse_string` | `() → str` | Listens for the words “dot”, “dash”, and “slash” and assembles them into a raw Morse string. |
| `audiofile_to_morse_string` | `(filepath: str) → str` | Analyses a `.wav` file, estimates the time unit, and returns the Morse pattern. |
| `generate_morse_audio` | `(text: str, filename='morse_output.wav', unit_duration=0.1, freq=700, rate=44100)` | Synthesises a sine‑wave Morse message into a 16‑bit mono WAV file. |
| `play_morse_code` | `(morse: str)` | Blocking Windows beep playback using `winsound.Beep`. |
| `play_letter_sounds` | `(text: str)` | Sequentially plays pre‑recorded letter sound files via `pygame`. |
| `plot_waveform` | `(filepath: str)` | Displays waveform and short‑time energy envelope with `matplotlib`. |
| `main` | `()` | CLI entry point; safe to ignore if you only need the library. |

Each function is fully type‑hinted and contains inline docstrings for quick reference.

---

## How It Works

### 1. Text Encoding / Decoding

* A constant `MORSE_CODE_DICT` maps characters to dot‑dash strings.  
* The inverse mapping is generated on start‑up for O(1) decoding.  
* For run‑on Morse without inter‑symbol spaces, the helper `insert_spaces_into_morse` uses a greedy longest‑match scan to re‑insert boundaries.

### 2. Real‑Time Beep Playback

* Windows‑only beep mode leverages `winsound.Beep(freq, duration_ms)` with 100 ms dits and 300 ms dahs by default.  
* Intra‑symbol, inter‑letter, and inter‑word gaps match ITU‑R M.1677‑1 timing ratios (1 : 1 : 3 : 7).

### 3. Speech Recognition Pipeline

* `speech_recognition.Recognizer` streams microphone audio to Google’s free Web Speech API.  
* Two independent entry points are provided: natural English sentences or phonetic Morse words (“dot dash”).  
* Network connectivity is required; offline models can be integrated later (see *Roadmap*).

### 4. Audio File Decoding

* Reads 16‑bit PCM WAV with `scipy.io.wavfile`.  
* Normalises to ±1 and segments into 20 ms frames.  
* Calculates frame energy and threshold‑bins into *beep* vs *silence*.  
* Median silence/beep length yields the fundamental time unit to classify short (dot) vs long (dash) pulses and small/large gaps.

### 5. Audio Generation

* Synthesises 700 Hz sine waves sampled at 44.1 kHz (CD quality) for each dit/dah.  
* Uses three separate gaps (intra‑symbol, inter‑letter, inter‑word) filled with zeros.  
* Streams samples into a `wave.Wave_write` object in little‑endian 16‑bit format.

### 6. Waveform Visualisation

* Plots raw amplitude and computed energy envelope on two stacked axes for clarity.  
* Useful to verify unit duration estimation and noise levels in recorded messages.

---

## Project Structure

```
morse-code-translator/
├── sounds/               # Optional A‑Z, 0‑9 PCM samples (16‑bit mono)
│   ├── A.wav
│   ├── B.wav
│   └── ...
├── requirements.txt
├── README.md             # ← you are here
└── morse.py   # Single‑file implementation
```

> In larger deployments you may wish to split `morse.py` into a package (`morse/`) with separate modules for `audio.py`, `recognition.py`, etc. The current monolithic script simplifies distribution to beginners.

---

## Requirements

| Package | Tested Version | Purpose |
| ------- | ------------- | ------- |
| Python  | ≥ 3.9 | Core language |
| `speech_recognition` | 3.10.0 | Microphone to text |
| `pygame` | 2.5.2 | Playback of letter WAVs |
| `numpy` | 1.26.4 | Numerical processing |
| `scipy` | 1.13.0 | WAV I/O |
| `matplotlib` | 3.9.0 | Waveform plots |
| `winsound` | stdlib (Windows) | Beep generation |
| `statistics` | stdlib | Median unit estimation |

Install everything via `pip install -r requirements.txt`. The `requirements.txt` file is auto‑generated with exact constraints but you may pin your own versions.

---

## Troubleshooting

| Symptom | Probable Cause | Fix |
| ------- | -------------- | --- |
| `OSError: No Default Input Device` | Microphone not detected | Verify system audio settings and default input device. |
| `Recognizer request failed` | Offline or blocked by firewall | Ensure internet access to Google Web Speech API. |
| **No sound in option 1** | `winsound` is Windows‑only | Select option 2 for WAV playback or run on Windows 10+. |
| Distorted generated WAV | Clipping due to high amplitude | Lower `freq` or increase `unit_duration`. |
| Decoder returns nonsense | Wrong sample rate or noisy recording | Resample to 44.1 kHz and apply a band‑pass filter around 700 Hz. |

---

## Roadmap

* [ ] **Cross‑platform beep playback** using `simpleaudio` or `pyaudio`.  
* [ ] **Offline speech model** via Vosk or Whisper for air‑gapped machines.  
* [ ] **GUI front‑end** built with Tkinter or PySide6.  
* [ ] **Config file** (`.ini`/`.yaml`) for custom timings and frequencies.  
* [ ] **Unit tests** with `pytest` & GitHub Actions CI.  
* [ ] **Package to PyPI** under the name `morse‑audio`.  
* [ ] **Web‑based demo** – Flask API and React front‑end.

---

## Contributing

1. Fork the repository and create your feature branch:  
   `git checkout -b feature/my‑feature`
2. Commit your changes with conventional commit messages.  
3. Push to your fork and open a Pull Request describing *why* not just *what*.  
4. Ensure all new code is type‑annotated, passes `ruff` linting, and includes docstrings.  
5. Be polite in code reviews; this project supports a **zero‑tolerance** policy on harassment.

---

## License & Ownership

> **Proprietary Notice**  
> This software, its source code, and all associated assets are the **exclusive property of the repository owner** (“Satyaki Saha”). Distribution, modification, or commercial use is **prohibited** without the Author’s prior written consent.

A permissive licence (e.g. MIT) may be granted by the Author on request for academic or non‑profit purposes. If you wish to use this project beyond fair‑use cloning for personal study, please contact the Author to negotiate terms.

---

## Author & Contact

**Name**  : *Satyaki Saha*  
**Email**  : satyakisaha33@gmail.com  
**GitHub** : [https://github.com/sahasatyaki](https://github.com/sahasatyaki)

Feel free to open an Issue for bug reports or feature requests. For private enquiries, email is preferred.

---
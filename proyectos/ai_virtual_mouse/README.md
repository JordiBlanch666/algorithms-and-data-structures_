# AI Virtual Mouse

**Control your mouse using only your hand — no physical mouse needed.**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.13-5C3EE8?style=flat&logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-FF6F00?style=flat&logo=google&logoColor=white)](https://mediapipe.dev/)
[![GitHub](https://img.shields.io/badge/JordiBlanch666-181717?style=flat&logo=github&logoColor=white)](https://github.com/JordiBlanch666)

---

## Overview

This project uses your webcam to track hand landmarks in real time and translate finger gestures into mouse actions — move, click, right-click, and drag — with no physical mouse required.

---

## How it works

```
Capture Video → Detect Hand → Track Fingers → Map to Screen → Control Mouse
```

| Step | Technology | What it does |
|------|-----------|--------------|
| Capture | OpenCV | Reads frames from webcam |
| Detect | MediaPipe | Locates 21 hand landmarks |
| Track | Custom logic | Identifies which fingers are up |
| Map | Math scaling | Converts camera coords to screen coords |
| Control | PyAutoGUI | Moves cursor, clicks, drags |

---

## Gesture controls

| Gesture | Action |
|---------|--------|
| Index finger up only | Move cursor |
| Index + middle pinched | Left click |
| Index + ring pinched | Right click |
| Thumb + index pinched | Drag & Drop |
| `Q` key | Exit |

---

## Installation

**Requirements:** Python 3.11

```bash
pip install -r requirements.txt
```

**Run:**
```bash
python main.py
```

---

## Libraries used

| Library | Purpose |
|---------|---------|
| `opencv-python` | Video capture and image processing |
| `mediapipe` | Hand landmark detection and tracking |
| `pyautogui` | Mouse movement and click control |

---

## Real-world applications

- **Presentations** — control slides without touching anything
- **Accessibility** — useful for people with physical disabilities
- **Smart TV / Media** — navigate menus using hand gestures
- **Touchless interaction** — interact with systems in a contactless way

---

## Project structure

```
PythonProject1/
 ├── main.py           ← Core application
 └── requirements.txt  ← Dependencies
```

---

> *I show up. I document everything. I don't break things.*
> Currently finalizing a Software Engineering degree at Hybridge · Certified in Git/GitHub & n8n automation.

---

[![Email](https://img.shields.io/badge/paastor.blanch@gmail.com-EA4335?style=flat&logo=gmail&logoColor=white)](mailto:paastor.blanch@gmail.com)
[![GitHub](https://img.shields.io/badge/JordiBlanch666-181717?style=flat&logo=github&logoColor=white)](https://github.com/JordiBlanch666)

*Hybridge — Software Engineering · 2025–2026*

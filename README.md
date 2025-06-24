# Criminal-Face-Recognition-with-OSINT-Tools
# 🔍 Criminal Face Recognition with OSINT Tools

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=flat&logo=opencv)
![OSINT](https://img.shields.io/badge/OSINT-Automated-yellow?style=flat)

## 📌 Project Overview

**Face Recognition with OSINT Tools** is an advanced Python-based application that combines facial recognition technology with OSINT (Open Source Intelligence) techniques to identify individuals and retrieve publicly available intelligence about them. This project is particularly useful for cybersecurity, law enforcement, and investigative journalism.

The system detects faces, registers them with user-entered data, and uses web scraping (Google Search API) to gather intelligence from the public domain.

---

## 📸 Features

- ✔️ Facial recognition using OpenCV + Haarcascade
- 🌐 OSINT data gathering using live search queries
- 📝 Criminal registration with user-friendly GUI (Tkinter)
- 📁 Automatic saving of cropped face datasets
- 📄 OSINT report generation in `.txt` format
- 🧠 Designed for ethical intelligence and forensics

---

## 🧰 Technologies Used

| Category             | Tools & Libraries                            |
|----------------------|----------------------------------------------|
| Programming Language | Python 3.9+                                  |
| Face Detection       | OpenCV, Haarcascade                          |
| GUI                  | Tkinter                                      |
| Image Handling       | Pillow (PIL)                                 |
| OSINT Search         | `googlesearch-python`                        |
| Reporting            | Text File Output (`osint_result.txt`)        |
| Optional Tools       | SpiderFoot, Recon-ng, Maltego, Twint         |

---

## 🧑‍💻 How It Works

CRIMINAL-FACE-IDENTIFICATION-SYSTEM/
├── home.py
├── register.py
├── facerec.py
├── osint_module.py
├── criminal_data/
├── face_samples/
├── profile_pics/
├── osint_result.txt
├── logo.png, back.png, next.png ...

### 1. Register a Criminal
- Fill in basic details: name, gender, DOB, etc.
- Select **at least 5 face images** for registration.

### 2. Face Recognition
- Each image is scanned using Haarcascade.
- Cropped faces are saved in dataset folders.

### 3. OSINT Integration
- Google search is triggered using the individual’s **name and nationality**.
- Top 5 relevant results are extracted and saved.

### 4. Report Generation
- OSINT results are stored in `osint_result.txt`.
- User is alerted with a success message.

### ✅ What You Should Do:

1. Create a new GitHub repo and push your project.
2. Paste this content into `README.md`.
3. Replace placeholders like `[Your Name]` and `[your.email@example.com]`.

Let me know if you'd like:
- `requirements.txt`
- GitHub repo setup help
- Screenshots to embed inside README

I can generate those instantly for you.

## 🧪 Sample Result


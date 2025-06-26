

import cv2
import os
import numpy as np
import requests
from bs4 import BeautifulSoup
import exifread
import logging

# API credentials
SERPAPI_KEY = os.getenv('SERPAPI_KEY', 'Your-Api-Key')
FACEPP_API_KEY = os.getenv('FACEPP_API_KEY', 'Your-Api-Key')
FACEPP_API_SECRET = os.getenv('FACEPP_API_SECRET', 'Your-Api-Key')
FACEPP_DETECT_URL = 'https://api-us.faceplusplus.com/facepp/v3/detect'

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

project_dir = os.path.dirname(os.path.abspath(__file__))
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

if face_cascade.empty() or eye_cascade.empty():
    logger.error("Haar cascade file(s) not found or corrupted.")
    raise FileNotFoundError("Haar cascade files missing.")

def get_image_metadata(image_path):
    try:
        with open(image_path, 'rb') as img_file:
            tags = exifread.process_file(img_file)
            metadata = {str(tag): str(tags[tag]) for tag in tags.keys()
                        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote')}
            return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata from {image_path}: {e}")
        return {}

def search_image_online_scrape(query):
    try:
        if not query:
            logger.warning("Empty search query for scraping.")
            return []
        search_url = f"https://serpapi.com/search.json?q={query.replace(' ', '+')}&api_key={SERPAPI_KEY}&engine=google&tbm=isch"
        response = requests.get(search_url, timeout=10)
        results = response.json().get("images_results", [])
        links = [r.get("original") or r.get("link") for r in results[:5]]
        return links
    except Exception as e:
        logger.error(f"SERPAPI search failed: {e}")
        return []

def call_facepp_api(image_path):
    try:
        with open(image_path, 'rb') as image_file:
            files = {'image_file': image_file}
            data = {
                'api_key': FACEPP_API_KEY,
                'api_secret': FACEPP_API_SECRET,
                'return_attributes': 'gender,age,smiling,ethnicity,emotion,beauty,glass'
            }
            response = requests.post(FACEPP_DETECT_URL, files=files, data=data)
            print("[DEBUG] Face++ raw response:", response.text)  # helpful for testing
            return response.json()
    except Exception as e:
        logger.error(f"Face++ API call failed: {e}")
        return {}

def detect_faces(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    eyes = []
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        detected_eyes = eye_cascade.detectMultiScale(roi_gray)
        eyes.append([(ex + x, ey + y, ew, eh) for (ex, ey, ew, eh) in detected_eyes])
    return faces, gray, eyes

def detect_faces_only(image_path):
    img = cv2.imread(image_path)
    if img is None or img.size == 0:
        logger.error("Invalid image file")
        return []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    return faces

def draw_faces_and_show(image_path):
    img = cv2.imread(image_path)
    faces = detect_faces_only(image_path)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow("Detected Faces", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def train_model():
    faces = []
    labels = []
    names = []
    face_samples_dir = os.path.join(project_dir, "face_samples")
    if not os.path.exists(face_samples_dir):
        logger.warning("Face samples directory not found.")
        return None, []
    people = os.listdir(face_samples_dir)
    label = 0
    for person in people:
        person_dir = os.path.join(face_samples_dir, person)
        if not os.path.isdir(person_dir):
            continue
        names.append(person)
        for image_name in os.listdir(person_dir):
            img_path = os.path.join(person_dir, image_name)
            img = cv2.imread(img_path)
            if img is None:
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces_rect, _, _ = detect_faces(img)
            if len(faces_rect) != 1:
                continue
            (x, y, w, h) = faces_rect[0]
            face = gray[y:y + h, x:x + w]
            faces.append(face)
            labels.append(label)
        label += 1
    if not faces:
        logger.warning("No valid faces for training.")
        return None, []
    model = cv2.face.LBPHFaceRecognizer_create()
    model.train(faces, np.array(labels))
    return model, names

def recognize_face(model, frame, gray_frame, face_coords, names, eye_coords=None):
    recognized = []
    for i, (x, y, w, h) in enumerate(face_coords):
        face = gray_frame[y:y+h, x:x+w]
        label, confidence = model.predict(face)
        if confidence < 100:
            name = names[label] if label < len(names) else "Unknown"
            recognized.append((name, confidence))
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"{name} ({confidence:.2f})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        else:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    return frame, recognized

def run_osint_analysis(image_path):
    logger.info(f"Running OSINT analysis for {image_path}")
    results = {}
    results['faces'] = detect_faces_only(image_path)
    results['metadata'] = get_image_metadata(image_path)
    query = os.path.basename(image_path).split('.')[0]
    results['search_results'] = search_image_online_scrape(query)
    results['facepp'] = call_facepp_api(image_path)

    with open("osint_result.txt", "w", encoding="utf-8") as f:
        f.write(f"OSINT Analysis for: {image_path}\n")
        f.write("\n=== Face Bounding Boxes ===\n")
        for i, (x, y, w, h) in enumerate(results['faces'], 1):
            f.write(f"Face {i}: x={x}, y={y}, w={w}, h={h}\n")
        f.write("\n=== Image Metadata ===\n")
        for key, val in results['metadata'].items():
            f.write(f"{key}: {val}\n")
        f.write("\n=== Google Search Links ===\n")
        for link in results['search_results']:
            f.write(link + "\n")
        f.write("\n=== Face++ Attributes ===\n")
        for face in results['facepp'].get('faces', []):
            attrs = face.get('attributes', {})
            for key, val in attrs.items():
                f.write(f"{key}: {val}\n")

    logger.info("Analysis complete. Results saved in osint_result.txt")
    return results

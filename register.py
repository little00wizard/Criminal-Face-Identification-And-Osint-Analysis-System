import os
import cv2
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from datetime import datetime
import json
import traceback

# === FACE DETECTION ===
def detect_faces(gray_img):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        print("Error: Could not load Haar cascade file.")
        return []
    # Adjusted parameters to improve detection
    faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    print(f"Detected {len(faces)} faces in image.")
    return faces

# === REGISTER CRIMINAL ===
def registerCriminal(img, path, img_num):
    size = 2
    (im_width, im_height) = (112, 92)
    file_num = 2 * img_num - 1

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detect_faces(gray)

    if len(faces) > 0:
        faces = sorted(faces, key=lambda x: x[3], reverse=True)
        (x, y, w, h) = [v * size for v in faces[0]]

        face = gray[y:y + h, x:x + w]
        face = cv2.resize(face, (im_width, im_height))

        try:
            cv2.imwrite(f'{path}/{file_num}.png', face)
            file_num += 1
            face = cv2.flip(face, 1)
            cv2.imwrite(f'{path}/{file_num}.png', face)
            print(f"Image {img_num}: Face detected and saved successfully at {path}/{file_num}.png")
        except Exception as e:
            print(f"Image {img_num}: Failed to save face image: {str(e)}")
            return img_num
    else:
        print(f"Image {img_num}: No face detected.")
        return img_num

    return None

# === GUI SECTION ===
class RegisterCriminalApp:
    def __init__(self, master):
        self.master = master
        master.title("Criminal Face  Identification System")
        master.configure(bg="#172c45")
        master.geometry("1000x600")

        self.image_paths = []

        self.label_title = tk.Label(master, text="Register Criminal", font=("Helvetica", 20, "bold"), fg="white", bg="#172c45")
        self.label_title.pack(pady=10)

        self.label_info = tk.Label(master, text="* Required Fields", font=("Arial", 10, "bold"), fg="yellow", bg="#172c45")
        self.label_info.pack()

        self.details_frame = tk.Frame(master, bg="#172c45")
        self.details_frame.pack(pady=5)

        labels = ["Name", "Father's Name", "Mother's Name", "Gender", "DOB(yyyy-mm-dd)", "Identification Mark",
                  "Nationality", "Religion", "Crimes Done"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(self.details_frame, text=label, fg="white", bg="#172c45").grid(row=i, column=0, sticky='w', padx=5, pady=3)
            entry = tk.Entry(self.details_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=3)
            self.entries[label] = entry

        self.img_btn = tk.Button(master, text="Select Images", bg="#3399ff", fg="white", font=("Arial", 10, "bold"), command=self.select_images)
        self.img_btn.pack(pady=5)

        self.register_btn = tk.Button(master, text="Register", bg="#00cc66", fg="white", font=("Arial", 12, "bold"), command=self.register)
        self.register_btn.pack(pady=15)

    def select_images(self):
        try:
            self.image_paths = filedialog.askopenfilenames(title="Select at least 5 images", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
            if len(self.image_paths) < 5:
                messagebox.showerror("Error", "Choose at least 5 images.")
                self.image_paths = []
            else:
                print(f"Selected {len(self.image_paths)} images: {self.image_paths}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select images: {str(e)}")
            print(f"Error in select_images: {str(e)}")

    def register(self):
        print("Register button clicked at", datetime.now())
        self.master.update()  # Force GUI update to ensure button isn't stuck
        try:
            if not self.image_paths:
                messagebox.showwarning("Warning", "No images selected.")
                print("No images selected, exiting register method.")
                return

            info = {label: entry.get().strip() for label, entry in self.entries.items()}
            print(f"Collected info: {info}")

            if not info['Name']:
                messagebox.showerror("Error", "Name is a required field.")
                print("Name field is empty, exiting register method.")
                return

            save_path = os.path.join("dataset", info['Name'].replace(" ", "_"))
            try:
                os.makedirs(save_path, exist_ok=True)
                print(f"Created directory: {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create directory: {str(e)}")
                print(f"Failed to create directory: {str(e)}")
                return

            no_face_images = []
            for i, img_path in enumerate(self.image_paths[:5]):
                print(f"Processing image {i+1}: {img_path}")
                try:
                    img = cv2.imread(img_path)
                    if img is None:
                        messagebox.showerror("Error", f"Failed to load image: {img_path}")
                        print(f"Failed to load image: {img_path}")
                        no_face_images.append(i + 1)
                        continue
                    result = registerCriminal(img, save_path, i + 1)
                    if result is not None:
                        no_face_images.append(result)
                except Exception as e:
                    messagebox.showerror("Error", f"Error processing image {img_path}: {str(e)}")
                    print(f"Error processing image {img_path}: {str(e)}")
                    return

            if no_face_images:
                messagebox.showerror("Error", f"No face detected in images: {', '.join(map(str, no_face_images))}")
                print(f"No faces detected in images: {no_face_images}")
                # Clean up the directory if registration fails
                try:
                    import shutil
                    shutil.rmtree(save_path)
                    print(f"Cleaned up directory: {save_path}")
                except Exception as e:
                    print(f"Failed to clean up directory: {str(e)}")
                return

            # Run OSINT analysis and save in JSON format
            try:
                from facerec import run_osint_analysis
                print("Starting OSINT analysis...")
                run_osint_analysis(info['Name'], dob=info['DOB(yyyy-mm-dd)'], nationality=info['Nationality'])
                print("OSINT analysis completed.")
            except Exception as e:
                messagebox.showwarning("Warning", f"OSINT analysis failed: {str(e)}. Proceeding with registration.")
                print(f"OSINT analysis failed: {str(e)}")

            messagebox.showinfo("Success", f"Criminal Registered Successfully. OSINT report saved for {info['Name']}.")
            print("Registration completed successfully at", datetime.now())

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error during registration: {str(e)}")
            print(f"Unexpected error in register method: {str(e)}")
            print(traceback.format_exc())

if __name__ == '__main__':
    root = tk.Tk()
    app = RegisterCriminalApp(root)
    root.mainloop()

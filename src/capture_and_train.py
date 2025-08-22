import cv2
import numpy as np # type: ignore
import os
import tkinter as tk
from tkinter import simpledialog, messagebox

def capture_and_train1(name, num_samples=300, camera_index=0):
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        messagebox.showerror("Error", f"Could not open camera with index {camera_index}.")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    save_path = f'dataset/{name}'
    os.makedirs(save_path, exist_ok=True)
    count = 0

    print(f"Capturing {num_samples} images for {name}...")

    while count < num_samples:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (100, 100))
            cv2.imwrite(f"{save_path}/{count}.jpg", face_img)
            count += 1
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Display the progress to the user
        text = f'Captured: {count}/{num_samples}'
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Capturing Images - Press ESC to cancel", frame)

        if cv2.waitKey(1) == 27:  # Press ESC to exit
            break
    cap.release()
    cv2.destroyAllWindows()
    
    if count < num_samples:
        print("Image capture cancelled or incomplete.")
        return # Do not proceed to training if capture was not finished

    print("Images captured successfully! ✅")
    
    # --- Train the model immediately after capturing ---
    recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=6, grid_x=6, grid_y=6)
    faces, labels = [], []
    label_map = {}
    label_id = 0

    print("Preparing training data...")
    for person in os.listdir('dataset'):
        person_path = os.path.join('dataset', person)
        if os.path.isdir(person_path):
            label_map[label_id] = person
            for img_name in os.listdir(person_path):
                img_path = os.path.join(person_path, img_name)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    faces.append(img)
                    labels.append(label_id)
            label_id += 1
    
    if not faces:
        messagebox.showerror("Error", "No faces found in the dataset to train. Please capture images first.")
        print("❌ Training failed. No faces found in the dataset.")
        return

    print("Training model...")
    recognizer.train(faces, np.array(labels))
    recognizer.save('trained_model.xml')
    np.save('label_map.npy', label_map)

    print("Model trained successfully! ✅")
    messagebox.showinfo("Success", f"Model trained successfully for {len(label_map)} person(s)!")

# This block allows you to run this script directly for testing
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    
    name = simpledialog.askstring("Input", "Enter person's name:")
    if name:
        # You can specify the camera index here for testing
        capture_and_train1(name, camera_index=0)
    else:
        messagebox.showwarning("Warning", "Please enter a valid name!")
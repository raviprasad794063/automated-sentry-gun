import ctypes
from tkinter import *
from PIL import Image, ImageTk, ImageSequence
from tkinter import simpledialog, messagebox
import threading

# Import your project's modules
import capture_and_train
import track
import object_detection

class SentryGUI:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)  # Fullscreen mode
        self.root.configure(bg='black')  # Black background
        self.root.title("Sentry Control")

        # Allow exiting fullscreen with the Escape key
        self.root.bind('<Escape>', lambda e: self.root.destroy())

        try:
            root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
        except Exception:
            pass

       
        self.gif_path = "gun_gologram.gif"
        self.gif = Image.open(self.gif_path)
        self.frames = [ImageTk.PhotoImage(frame.copy().resize((1200, 600), Image.LANCZOS)) for frame in ImageSequence.Iterator(self.gif)]

        self.frame_index = 0
        self.background_label = Label(self.root, bg='black')
        self.background_label.place(relx=0.5, rely=0.4, anchor=CENTER)

        self.animate_gif()
        self.add_buttons()

    def animate_gif(self):
        """Cycles through the GIF frames to create an animation."""
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.background_label.config(image=self.frames[self.frame_index])
        self.root.after(10, self.animate_gif)  # Animation speed (10ms delay)

    def add_buttons(self):
        """Creates and places the control buttons on the GUI."""
        # Load button images using relative paths
        button_img = ImageTk.PhotoImage(Image.open(self.gif_path).resize((150, 150), Image.LANCZOS))

        # --- Button 1: Train Model ---
        train_button = Button(self.root, image=button_img, bg="black", bd=0, relief=FLAT, command=self.start_face_training)
        train_button.image = button_img # Keep a reference to avoid garbage collection
        train_button.place(relx=0.2, rely=0.85, anchor=CENTER)
        Label(self.root, text="Show Enemy (Train)", bg="black", fg="white").place(relx=0.2, rely=0.93, anchor=CENTER)

        # --- Button 2: Object Shooting ---
        object_button = Button(self.root, image=button_img, bg="black", bd=0, relief=FLAT, command=self.start_object_tracking)
        object_button.image = button_img
        object_button.place(relx=0.4, rely=0.85, anchor=CENTER)
        Label(self.root, text="Object Shooting", bg="black", fg="white").place(relx=0.4, rely=0.93, anchor=CENTER)

        # --- Button 3: Inactive/Placeholder ---
        free_arduino_button = Button(self.root, image=button_img, bg="black", bd=0, relief=FLAT, state=DISABLED) # Redefine krlena incase window freeze ho.
        free_arduino_button.image = button_img
        free_arduino_button.place(relx=0.6, rely=0.85, anchor=CENTER)
        Label(self.root, text="Free Arduino", bg="black", fg="white").place(relx=0.6, rely=0.93, anchor=CENTER)

        # --- Button 4: Track Enemy ---
        track_button = Button(self.root, image=button_img, bg="black", bd=0, relief=FLAT, command=self.start_face_tracking)
        track_button.image = button_img
        track_button.place(relx=0.8, rely=0.85, anchor=CENTER)
        Label(self.root, text="Track Enemy", bg="black", fg="white").place(relx=0.8, rely=0.93, anchor=CENTER)

    def start_face_training(self):
        """Handles the user input and calls the training script."""
        name = simpledialog.askstring("Input", "Enter person's name to train:")
        if name:
            capture_and_train.capture_and_train1(name)
        else:
            messagebox.showwarning("Warning", "Please enter a valid name!")

    def start_face_tracking(self):
        """Launches the face tracking module in a separate thread to avoid freezing the GUI."""
        print("Starting face tracking...")
        tracking_thread = threading.Thread(target=track.start_face_tracking, kwargs={'camera_index': 1}, daemon=True)
        tracking_thread.start()

    def start_object_tracking(self):
        """Launches the object detection module in a separate thread."""
        print("Starting object tracking...")
        object_thread = threading.Thread(target=object_detection.start_object_tracking, kwargs={'camera_index': 1}, daemon=True)
        object_thread.start()


if __name__ == "__main__":
    root = Tk()
    app = SentryGUI(root)
    root.mainloop()
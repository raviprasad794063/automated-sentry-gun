import cv2
import numpy as np
import pyfirmata2 as pyfirmata
from ultralytics import YOLO
import tkinter as tk
from PIL import Image, ImageTk
import time

def start_object_tracking(camera_index=1, com_port="COM7"):
   
    model = YOLO("yolov8n.pt")
    
    # --- Camera Setup using the camera_index parameter ---
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {camera_index}.")
        return
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 60)

    board = None
    laser_pin = None
    try:
        # --- Initialize Arduino board using the com_port parameter ---
        print(f"Connecting to Arduino on port {com_port}...")
        board = pyfirmata.Arduino(com_port)
        servo_pinX = board.get_pin('d:9:s')
        servo_pinY = board.get_pin('d:10:s')
        laser_pin = board.get_pin('d:11:o')
        laser_pin.write(1)  # Laser off initially
        print("✅ Arduino connection successful.")
    except Exception as e:
        print(f"❌ Could not connect to Arduino on {com_port}. Running in video-only mode. Error: {e}")
        board = None 

    # This creates a new window for the object detection feed
    root = tk.Tk()
    root.title("Object Detection Feed")
    canvas = tk.Canvas(root, width=640, height=480)
    canvas.pack()

    tracked_object_name = ""
    tracked_object_number = None
    servo_control_enabled = False
    fire_commanded = False
    servoX, servoY = 90, 90
    firing_label_timer = 0

    def update_frame():
        nonlocal tracked_object_name, tracked_object_number, servo_control_enabled
        nonlocal fire_commanded, servoX, servoY, firing_label_timer

        ret, frame = cap.read()
        if not ret:
            root.after(10, update_frame)
            return

        results = model(frame, verbose=False)
        object_count = {}
        object_instances = {}
        target_visible = False

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0].item()
                label = result.names[int(box.cls[0])].lower()

                if conf > 0.5:
                    object_count[label] = object_count.get(label, 0) + 1
                    label_numbered = f"{label} {object_count[label]}"
                    object_instances.setdefault(label, []).append((label_numbered, x1, y1, x2, y2))

        if tracked_object_name and tracked_object_name in object_instances:
            instances = object_instances[tracked_object_name]
            # Track the specific instance if a number is given, otherwise track the first one
            instance_to_track = -1
            if tracked_object_number is not None and tracked_object_number <= len(instances):
                instance_to_track = tracked_object_number - 1
            elif len(instances) > 0:
                instance_to_track = 0

            if instance_to_track != -1:
                label_numbered, x1, y1, x2, y2 = instances[instance_to_track]
                fx, fy = (x1 + x2) // 2, (y1 + y2) // 2
                
                # Calculate servo positions
                servoX = np.interp(fx, [0, 640], [180, 0]) # Invert for intuitive movement
                servoY = np.interp(fy, [0, 480], [180, 0]) # Invert for intuitive movement
                
                if servo_control_enabled and board:
                    servo_pinX.write(servoX)
                    servo_pinY.write(servoY)
                
                target_visible = True
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label_numbered, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if fire_commanded and target_visible and board:
            laser_pin.write(0) # Fire laser
            firing_label_timer = time.time()
            fire_commanded = False
            # Turn laser off after a short duration
            root.after(200, lambda: laser_pin.write(1))

        if time.time() - firing_label_timer < 0.5:
            cv2.putText(frame, "🔥 FIRING", (460, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        if servo_control_enabled:
            cv2.putText(frame, f'Servo X: {int(servoX)} deg', (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            cv2.putText(frame, f'Servo Y: {int(servoY)} deg', (10, 60), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.image = img_tk
        root.after(10, update_frame)

    def set_object_to_track():
        nonlocal tracked_object_name
        tracked_object_name = object_entry.get().strip().lower()

    def select_object_to_track():
        nonlocal tracked_object_number
        try:
            tracked_object_number = int(object_number_entry.get().strip())
        except ValueError:
            tracked_object_number = None # If empty or invalid, track first found

    def toggle_servo_control():
        nonlocal servo_control_enabled
        servo_control_enabled = not servo_control_enabled
        start_stop_button.config(text="Stop Servo Control" if servo_control_enabled else "Start Servo Control")

    def fire_laser():
        nonlocal fire_commanded
        fire_commanded = True

    # --- Setup GUI Controls ---
    controls_frame = tk.Frame(root)
    controls_frame.pack()
    tk.Label(controls_frame, text="Track Object:").pack(side=tk.LEFT)
    object_entry = tk.Entry(controls_frame)
    object_entry.pack(side=tk.LEFT)
    tk.Button(controls_frame, text="Set", command=set_object_to_track).pack(side=tk.LEFT)
    
    tk.Label(controls_frame, text="Instance #:").pack(side=tk.LEFT)
    object_number_entry = tk.Entry(controls_frame, width=5)
    object_number_entry.pack(side=tk.LEFT)
    tk.Button(controls_frame, text="Select", command=select_object_to_track).pack(side=tk.LEFT)

    start_stop_button = tk.Button(root, text="Start Servo Control", command=toggle_servo_control)
    start_stop_button.pack()

    fire_button = tk.Button(root, text="🔥 Fire Laser (F)", command=fire_laser, bg='red', fg='white', font=('Arial', 12))
    fire_button.pack(pady=5)
    
    def on_closing():
        print("Releasing resources...")
        cap.release()
        if board:
            if laser_pin:
                laser_pin.write(1)
            board.exit()
            print("✅ Arduino disconnected.")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.bind('<f>', lambda event: fire_laser()) # Bind 'f' key to fire
    update_frame()
    root.mainloop()

# This block allows the script to be run directly for testing purposes
if __name__ == "__main__":
    # You can run this file by itself to test object detection.
    # It will use camera 1 and COM7 by default.
    start_object_tracking(camera_index=1, com_port="COM7")
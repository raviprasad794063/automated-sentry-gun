import cv2
import numpy as np
import pyfirmata2 as pyfirmata
import time

def start_face_tracking(camera_index=1, com_port="COM7"):
    board = None
    laser_pin = None
    fire_button_pressed = False # This can be local to the function

    try:
        # --- Initialize Arduino board and pins using the com_port parameter ---
        print(f"Connecting to Arduino on port {com_port}...")
        board = pyfirmata.Arduino(com_port)
        it = pyfirmata.util.Iterator(board)
        it.start()

        servo_pinX = board.get_pin('d:9:s')
        servo_pinY = board.get_pin('d:10:s')
        laser_pin = board.get_pin('d:11:o')
        laser_pin.write(1)  # Laser off initially
        print("✅ Arduino connection successful.")

        # Load face recognition model
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('trained_model.xml')
        label_map = np.load('label_map.npy', allow_pickle=True).item()
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # --- Camera Setup using the camera_index parameter ---
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Error: Could not open camera with index {camera_index}.")
            return

        ws, hs = 1280, 720
        cap.set(3, ws)
        cap.set(4, hs)

        servoPos = [90, 90]
        sweep_mode = False
        sweep_angle = 90 # Start sweep from center
        direction = 1

        def click_event(event, x, y, flags, param):
            nonlocal fire_button_pressed
            if event == cv2.EVENT_LBUTTONDOWN:
                # Check if the click is within the "FIRE" button coordinates
                if 1000 <= x <= 1200 and 600 <= y <= 680:
                    fire_button_pressed = True

        cv2.namedWindow("Face Tracking")
        cv2.setMouseCallback("Face Tracking", click_event)

        while True:
            success, img = cap.read()
            if not success:
                break

            key = cv2.waitKey(1) & 0xFF
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            face_tracked = False

            for (x, y, w, h) in faces:
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (100, 100))
                label, confidence = recognizer.predict(face_img)
                accuracy = 100 - confidence

                if accuracy >= 70:
                    face_tracked = True
                    fx, fy = x + w // 2, y + h // 2
                    servoX = np.interp(fx, [0, ws], [180, 0]) # Invert X-axis for intuitive movement
                    servoY = np.interp(fy, [0, hs], [180, 0]) # Invert Y-axis

                    servoPos[0] = max(0, min(180, servoX))
                    servoPos[1] = max(0, min(180, servoY))

                    # Draw target
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(img, "TARGET LOCKED", (850, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                    cv2.circle(img, (fx, fy), 15, (0, 0, 255), cv2.FILLED)

                    # Fire condition
                    if key == ord('f') or fire_button_pressed:
                        laser_pin.write(0) # Laser ON
                        cv2.putText(img, "🔥 FIRING", (850, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
                        time.sleep(0.2)
                        laser_pin.write(1) # Laser OFF
                        fire_button_pressed = False

            if not face_tracked:
                cv2.putText(img, "NO TARGET", (880, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
                cv2.circle(img, (640, 360), 80, (0, 0, 255), 2)
                laser_pin.write(1)

            # Sweep mode logic
            if sweep_mode and not face_tracked:
                sweep_angle += direction * 1
                if sweep_angle >= 160 or sweep_angle <= 20:
                    direction *= -1
                servo_pinX.write(sweep_angle)
                servoPos[0] = sweep_angle # Update servoPos to reflect sweep angle
                time.sleep(0.01)

            # Move servos only if a face is being tracked
            if face_tracked:
                servo_pinX.write(servoPos[0])
                servo_pinY.write(servoPos[1])

            # UI Info
            cv2.putText(img, f'Servo X: {int(servoPos[0])} deg', (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            cv2.putText(img, f'Servo Y: {int(servoPos[1])} deg', (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

            # Draw Fire Button
            cv2.rectangle(img, (1000, 600), (1200, 680), (0, 0, 255), -1)
            cv2.putText(img, "FIRE", (1040, 650), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

            cv2.imshow("Face Tracking", img)

            # Key controls
            if key == 27:  # ESC to quit
                break
            elif key == ord('s'):
                sweep_mode = not sweep_mode
                print(f"Sweep mode {'ON' if sweep_mode else 'OFF'}")

        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"An error occurred in face tracking: {e}")

    finally:
        # Safely release resources
        if laser_pin:
            laser_pin.write(1)
        if board:
            board.exit()
        print("✅ Face tracking stopped. Arduino disconnected and resources released.")

# This block allows you to run this script directly for testing
if __name__ == "__main__":
    # To test, you can run this file directly.
    # It will use camera 1 and COM7 by default.
    start_face_tracking()
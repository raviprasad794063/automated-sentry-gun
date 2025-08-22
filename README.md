# automated-sentry-gun
🤖 Automated AI Sentry Gun Project! 🔫
Welcome to the AI Sentry Gun project! 🎉 This is an awesome application that brings software and hardware together, using the power of computer vision to create a real-life automated turret. If you've ever wanted to make your code interact with the physical world, you're in the right place!

This project uses a webcam to see the world, identifies targets using advanced AI models, and aims a physical turret using an Arduino and servos. Let's dive in!

✨ What's Inside? (Features)
This project is packed with cool features you can run right out of the box:

🎯 Real-Time Object Tracking: Uses the powerful YOLOv8 model to detect and follow any object you specify (like a "person" or "cup").

👤 Custom Face Recognition: Train the turret to recognize you or your friends! The system can capture facial images and learn to lock onto specific people.

⚡ Lightning-Fast Servo Control: Interfaces directly with an Arduino using PyFirmata2 to control pan and tilt servos for smooth and responsive aiming.

💥 Laser/Relay Engagement: Includes functionality to activate a laser or relay module when a target is locked, which can be triggered with the press of a key or a button.

🖥️ Interactive GUI: Comes with a fun, fullscreen graphical user interface built with Tkinter that lets you easily switch between modes and train the face recognition model.

🚀 The Tech Stack
This project combines some amazing technologies:

Python: The core of our project!


OpenCV: For all the heavy lifting in computer vision and camera interactions.


YOLOv8 (Ultralytics): State-of-the-art AI for real-time object detection.

Tkinter: For creating the fun and easy-to-use graphical interface.


PyFirmata2: The magic that lets our Python script talk to the Arduino.

Arduino: The heart of our hardware control.

🛠️ Hardware You'll Need
To build the physical turret, you'll need a few parts:

A Webcam (an external one is recommended)

An Arduino UNO (or a compatible board)

2x Servo Motors ( MG996R )

A Laser Diode Module
 
A Relay Module

Jumper Wires

A custom mount to hold everything together (get creative!)

⚙️ Let's Get Building! (Setup Guide)
Ready to get this running? Just follow these simple steps.

1. Clone the Repository
First, grab the code from GitHub.

Bash

git clone https://github.com/your-username/automated-sentry-gun.git
cd automated-sentry-gun
2. Set Up a Python Virtual Environment
It's always a good idea to keep project dependencies tidy.

Bash

# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. Install All the Goodies
This one command installs all the necessary Python libraries for you.

Bash

pip install -r requirements.txt
4. Configure Your Hardware
This is the most hands-on part!

Arduino Sketch: Open the Arduino IDE and upload the StandardFirmataPlus sketch to your board. You can find it under File > Examples > Firmata > StandardFirmataPlus.

Wiring:

Connect your pan (X-axis) servo to Pin 9.

Connect your tilt (Y-axis) servo to Pin 10.

Connect your laser/relay module to Pin 11.

Set Your COM Port: Find your Arduino's COM port (e.g., in the Arduino IDE or your system's device manager). This is important! Open the track.py and object_detection.py files and change the com_port variable to match yours.

Python

# In both track.py and object_detection.py
# Change "COM7" to your actual port!
def start_face_tracking(camera_index=1, com_port="COM7"):
🎉 Let's Go! (Usage)
You're all set! To launch the main application, run the gui.py script from your terminal:

Bash

python gui.py
The fullscreen GUI will appear, and you can choose what you want to do:

Show Enemy (Train): Click this to start the face capture process. Enter a name, look at the camera, and let it learn a new face!

Object Shooting: Launches the YOLOv8 object tracker. You can type in an object class (like "person") and watch it lock on.

Track Enemy: Activates the face recognition mode. The turret will now hunt for any faces it has been trained to recognize.
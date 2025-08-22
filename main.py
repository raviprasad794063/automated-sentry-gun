
from tkinter import Tk
# The imported class name is updated to match the corrected gui.py file.
from src.gui import SentryGUI 

if __name__ == "__main__":
    # Create the main Tkinter window instance
    root = Tk()
    
    # Instantiate the main application class, passing the root window to it
    app = SentryGUI(root)
    
    # Start the Tkinter event loop to run the application
    root.mainloop()
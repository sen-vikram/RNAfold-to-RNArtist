import customtkinter as ctk
import os
import sys

# Add the current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_gui.main_window import RNAfoldApp

import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    # Set the theme and appearance mode
    ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    app = RNAfoldApp()
    app.mainloop()

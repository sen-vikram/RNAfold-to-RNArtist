import customtkinter as ctk
import subprocess
import threading
import json
import os
import sys

class RunTab:
    def __init__(self, parent_frame, app_instance):
        self.app = app_instance
        self.frame = parent_frame
        
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

        # Controls Area
        self.control_frame = ctk.CTkFrame(self.frame)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.run_btn = ctk.CTkButton(self.control_frame, text="RUN ENGINE", command=self.start_engine, width=200, height=50, font=("Arial", 16, "bold"), fg_color="green", hover_color="darkgreen")
        self.run_btn.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.control_frame, text="Ready", text_color="gray")
        self.status_label.pack(pady=5)

        # Log Area
        self.log_box = ctk.CTkTextbox(self.frame, font=("Consolas", 12))
        self.log_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.log_box.configure(state="disabled")

        self.clear_btn = ctk.CTkButton(self.frame, text="Clear Log", command=self.clear_log, width=100)
        self.clear_btn.grid(row=2, column=0, pady=10)

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("0.0", "end")
        self.log_box.configure(state="disabled")

    def start_engine(self):
        # 1. Get Data
        input_path = self.app.get_input_path()
        if not input_path:
            self.log("Error: No input file/directory selected!")
            self.status_label.configure(text="Error: Missing Input", text_color="red")
            return

        profile_data = self.app.get_current_profile()
        
        # 2. Save Temp Profile
        temp_profile_path = "temp_gui_profile.json"
        try:
            with open(temp_profile_path, "w") as f:
                json.dump(profile_data, f, indent=2)
            self.log(f"Generated Profile: {temp_profile_path}")
        except Exception as e:
            self.log(f"Error saving profile: {e}")
            return

        # 3. Disable Button
        self.run_btn.configure(state="disabled", text="Running...")
        self.status_label.configure(text="Processing...", text_color="orange")

        # 4. Threaded Execution
        thread = threading.Thread(target=self.run_subprocess, args=(input_path, temp_profile_path))
        thread.start()

    def run_subprocess(self, input_path, profile_path):
        engine_script = "RNAfold_to_RNArtis_v5_engine.py"
        
        # Determine python executable
        python_exe = sys.executable

        cmd = [python_exe, engine_script, input_path, "--profile", profile_path]
        
        self.log(f"Executing: {' '.join(cmd)}")
        self.log("-" * 40)

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            # Read output real-time
            for line in process.stdout:
                self.app.after(0, self.log, line.strip())
            
            # Check stderr
            stderr = process.stderr.read()
            if stderr:
                self.app.after(0, self.log, f"STDERR: {stderr}")

            process.wait()
            
            if process.returncode == 0:
                self.app.after(0, lambda: self.status_label.configure(text="Completed Successfully", text_color="green"))
                self.app.after(0, self.log, "Done.")
            else:
                self.app.after(0, lambda: self.status_label.configure(text="Failed", text_color="red"))
                self.app.after(0, self.log, f"Process exited with code {process.returncode}")

        except Exception as e:
            self.app.after(0, self.log, f"Exception: {e}")
            self.app.after(0, lambda: self.status_label.configure(text="Error", text_color="red"))
        
        finally:
            self.app.after(0, lambda: self.run_btn.configure(state="normal", text="RUN ENGINE"))

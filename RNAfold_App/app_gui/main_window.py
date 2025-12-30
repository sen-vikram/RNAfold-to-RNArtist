import customtkinter as ctk
import threading
import json
import os
import sys

from .ui_components import AccordionFrame
from .tabs.input_tab import InputTab
from .tabs.params_tab import ParamsTab
from .tabs.constraints_tab import ConstraintsTab
from .tabs.advanced_tabs import DanglesTab, EnergyTab
from .tabs.visual_tab import VisualTab

# Import Engine Programmatic Entry Point
# Assuming the file is in the root directory relative to execution
sys.path.append(os.getcwd()) 
import RNAfold_to_RNArtist_engine as engine

class RNAfoldApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("RNAfold to RNArtist")
        self.geometry("1000x900")
        
        # Grid: Row 0 = Scrollable Content, Row 1 = Footer (Run Button)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ------------------------
        # 1. Main Scrollable Area
        # ------------------------
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="RNAfold Configuration")
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # --- A. Sequence Input (Always Visible) ---
        ctk.CTkLabel(self.scroll_frame, text="Sequence Input", font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        input_frame_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        input_frame_container.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.input_ui = InputTab(input_frame_container, self) 

        # --- B. Accordions ---
        
        # 1. Folding Constraints (Collapsed by default)
        self.acc_constraints = AccordionFrame(self.scroll_frame, "Folding Constraints", start_collapsed=True)
        self.acc_constraints.grid(row=2, column=0, sticky="ew", pady=2)
        self.constraints_ui = ConstraintsTab(self.acc_constraints.get_content_frame(), self)

        # 2. Fold algorithms and basic options
        self.acc_algo = AccordionFrame(self.scroll_frame, "Fold algorithms and basic options", start_collapsed=True)
        self.acc_algo.grid(row=3, column=0, sticky="ew", pady=2)
        self.params_ui = ParamsTab(self.acc_algo.get_content_frame(), self)

        # 3. Dangling end options
        self.acc_dangles = AccordionFrame(self.scroll_frame, "Dangling end options", start_collapsed=True)
        self.acc_dangles.grid(row=4, column=0, sticky="ew", pady=2)
        self.dangles_ui = DanglesTab(self.acc_dangles.get_content_frame(), self)

        # 4. Energy Parameters
        self.acc_energy = AccordionFrame(self.scroll_frame, "Energy Parameters", start_collapsed=True)
        self.acc_energy.grid(row=5, column=0, sticky="ew", pady=2)
        self.energy_ui = EnergyTab(self.acc_energy.get_content_frame(), self)

        # 5. Visualization Options
        self.acc_visual = AccordionFrame(self.scroll_frame, "Visualization Options (Colormap & Style)", start_collapsed=True)
        self.acc_visual.grid(row=6, column=0, sticky="ew", pady=2)
        self.visual_tab = VisualTab(self.acc_visual.get_content_frame(), self)

        # --- C. Log Area ---
        self.log_frame = ctk.CTkFrame(self.scroll_frame)
        self.log_frame.grid(row=7, column=0, sticky="ew", pady=20)
        ctk.CTkLabel(self.log_frame, text="Execution Log:").pack(anchor="w", padx=5)
        self.log_box = ctk.CTkTextbox(self.log_frame, height=150, font=("Consolas", 11))
        self.log_box.pack(fill="x", padx=5, pady=5)
        self.log_box.configure(state="disabled")

        # ------------------------
        # 2. Footer (Run Button)
        # ------------------------
        self.footer = ctk.CTkFrame(self, height=80)
        self.footer.grid(row=1, column=0, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self.footer, text="Ready", text_color="gray")
        self.status_label.pack(side="left", padx=20)

        self.run_btn = ctk.CTkButton(self.footer, text="RUN ENGINE", command=self.start_engine, 
                                     font=("Arial", 16, "bold"), fg_color="green", hover_color="darkgreen", 
                                     width=200, height=40)
        self.run_btn.pack(side="right", padx=20, pady=20)

    # ------------------
    # Helper Methods
    # ------------------
    def get_current_profile(self):
        """Collects data from UI components."""
        
        # Combine folding params from multiple tabs
        folding_params = self.params_ui.get_folding_params()
        folding_params["dangles"] = self.dangles_ui.get_value()
        
        energy_values = self.energy_ui.get_values()
        folding_params["temperature"] = energy_values["temperature"]
        folding_params["param_set"] = energy_values["param_set"]
        folding_params["salt"] = energy_values["salt"]

        profile = {
            "folding_params": folding_params,
            "constraints": self.constraints_ui.get_values(),
            "algorithms": self.params_ui.get_algorithms(),
        }
        profile.update(self.visual_tab.get_data())
        return profile

    def get_input_path(self):
        return self.input_ui.get_selected_path()

    def log(self, message):
        """Thread-safe logging to GUI."""
        def _update():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", str(message) + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(0, _update)

    def start_engine(self):
        # 1. Get Data
        input_path = self.get_input_path()
        if not input_path:
            self.log("Error: No input file/directory selected!")
            self.status_label.configure(text="Error: Missing Input", text_color="red")
            return

        profile_data = self.get_current_profile()
        
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

        # 4. Threaded Execution (Direct Call)
        thread = threading.Thread(target=self.run_direct, args=(input_path, temp_profile_path))
        thread.start()

    def run_direct(self, input_path, profile_path):
        try:
            # We pass self.log as the callback to route logs to GUI
            success = engine.run_engine_programmatic(
                input_path=input_path,
                profile_path=profile_path,
                output_dir="outputs", # Or configurable
                callback=self.log
            )
            
            if success:
                self.after(0, lambda: self.status_label.configure(text="Completed Successfully", text_color="green"))
                self.log("Done.")
            else:
                self.after(0, lambda: self.status_label.configure(text="Failed", text_color="red"))
                self.log("Engine reported failure.")

        except Exception as e:
            self.after(0, self.log, f"Exception: {e}")
            self.after(0, lambda: self.status_label.configure(text="Error", text_color="red"))
            import traceback
            self.after(0, self.log, traceback.format_exc())
        
        finally:
            self.after(0, lambda: self.run_btn.configure(state="normal", text="RUN ENGINE"))

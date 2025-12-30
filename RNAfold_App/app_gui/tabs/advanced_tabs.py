import customtkinter as ctk

class DanglesTab:
    def __init__(self, parent_frame, app_instance):
        self.app = app_instance
        self.frame = parent_frame
        
        self.dangles_var = ctk.IntVar(value=2)
        
        ctk.CTkRadioButton(self.frame, text="no dangling end energies", variable=self.dangles_var, value=0, font=("Arial", 12)).pack(anchor="w", padx=20, pady=5)
        ctk.CTkRadioButton(self.frame, text="unpaired bases can participate in at most one dangling end (MFE folding only)", variable=self.dangles_var, value=1, font=("Arial", 12)).pack(anchor="w", padx=20, pady=5)
        ctk.CTkRadioButton(self.frame, text="dangling energies on both sides of a helix in any case", variable=self.dangles_var, value=2, font=("Arial", 12)).pack(anchor="w", padx=20, pady=5)
        ctk.CTkRadioButton(self.frame, text="allow coaxial stacking of adjacent helices in multi-loops (MFE folding only)", variable=self.dangles_var, value=3, font=("Arial", 12)).pack(anchor="w", padx=20, pady=5)

    def get_value(self):
        return self.dangles_var.get()

class EnergyTab:
    """
    Refactored to match 'Energy Parameters' section of online RNAfold.
    """
    def __init__(self, parent_frame, app_instance):
        self.app = app_instance
        self.frame = parent_frame
        
        # 1. Parameter Set Selection
        
        self.param_set_var = ctk.StringVar(value="turner2004")
        
        self.r_turner2004 = ctk.CTkRadioButton(self.frame, text="RNA parameters (Turner model, 2004)", 
                                               variable=self.param_set_var, value="turner2004", font=("Arial", 12))
        self.r_turner2004.pack(anchor="w", padx=20, pady=5)

        self.r_turner1999 = ctk.CTkRadioButton(self.frame, text="RNA parameters (Turner model, 1999)", 
                                               variable=self.param_set_var, value="turner1999", font=("Arial", 12))
        self.r_turner1999.pack(anchor="w", padx=20, pady=5)
        
        self.r_andronescu = ctk.CTkRadioButton(self.frame, text="RNA parameters (Andronescu model, 2007)", 
                                               variable=self.param_set_var, value="andronescu2007", font=("Arial", 12))
        self.r_andronescu.pack(anchor="w", padx=20, pady=5)
        
        self.r_dna = ctk.CTkRadioButton(self.frame, text="DNA parameters (Matthews model, 2004)", 
                                        variable=self.param_set_var, value="dna_matthews2004", font=("Arial", 12))
        self.r_dna.pack(anchor="w", padx=20, pady=5)

        # 2. Temperature
        temp_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        temp_frame.pack(anchor="w", padx=20, pady=5)
        
        self.temp_var = ctk.StringVar(value="37.0")
        self.temp_entry = ctk.CTkEntry(temp_frame, textvariable=self.temp_var, width=60)
        self.temp_entry.pack(side="left")
        ctk.CTkLabel(temp_frame, text="rescale energy parameters to given temperature (C)", font=("Arial", 12)).pack(side="left", padx=5)

        # 3. Salt Concentration
        salt_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        salt_frame.pack(anchor="w", padx=20, pady=5)
        
        self.salt_var = ctk.StringVar(value="1.021")
        self.salt_entry = ctk.CTkEntry(salt_frame, textvariable=self.salt_var, width=60)
        self.salt_entry.pack(side="left")
        ctk.CTkLabel(salt_frame, text="Use this salt concentration in molar (M)", font=("Arial", 12)).pack(side="left", padx=5)


    def get_values(self):
        """Returns dict of energy parameters."""
        try:
            temp = float(self.temp_var.get())
        except:
            temp = 37.0
            
        try:
            salt = float(self.salt_var.get())
        except:
            salt = 1.021
            
        return {
            "temperature": temp,
            "param_set": self.param_set_var.get(),
            "salt": salt
        }

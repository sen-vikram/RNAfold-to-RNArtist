import customtkinter as ctk

class ParamsTab:
    """
    Implements the 'Fold algorithms and basic options' section exactly as requested.
    """
    def __init__(self, parent_frame, app_instance):
        self.app = app_instance
        self.frame = parent_frame
        
        self.frame.grid_columnconfigure(0, weight=1)

        # 1. Algorithm Selection (Radio Buttons)
        # Default: MFE and Partition Function
        self.algo_var = ctk.IntVar(value=0) # 0 = MFE & PF, 1 = MFE Only

        self.radio_pf = ctk.CTkRadioButton(self.frame, text="minimum free energy (MFE) and partition function", 
                                           variable=self.algo_var, value=0, font=("Arial", 12))
        self.radio_pf.grid(row=0, column=0, sticky="w", padx=20, pady=5)

        self.radio_mfe = ctk.CTkRadioButton(self.frame, text="minimum free energy (MFE) only", 
                                            variable=self.algo_var, value=1, font=("Arial", 12))
        self.radio_mfe.grid(row=1, column=0, sticky="w", padx=20, pady=5)

        # Separator (visually implied by spacing)

        # 2. Basic Options (Checkboxes)
        # "no GU pairs at the end of helices" (noClosingGU) -> Default: Unselected
        self.noClosingGU_var = ctk.BooleanVar(value=False)
        self.chk_closing = ctk.CTkCheckBox(self.frame, text="no GU pairs at the end of helices", 
                                           variable=self.noClosingGU_var, font=("Arial", 12))
        self.chk_closing.grid(row=2, column=0, sticky="w", padx=20, pady=5)

        # "avoid isolated base pairs" (noLP) -> Default: Selected
        # Note: logic in engine is: noLP=True means "No Lonely Pairs" is ON.
        self.noLP_var = ctk.BooleanVar(value=True)
        self.chk_nolp = ctk.CTkCheckBox(self.frame, text="avoid isolated base pairs", 
                                        variable=self.noLP_var, font=("Arial", 12))
        self.chk_nolp.grid(row=3, column=0, sticky="w", padx=20, pady=5)

        # "assume RNA molecule to be circular" (circ) -> Default: Unselected
        self.circ_var = ctk.BooleanVar(value=False)
        self.chk_circ = ctk.CTkCheckBox(self.frame, text="assume RNA molecule to be circular", 
                                        variable=self.circ_var, font=("Arial", 12))
        self.chk_circ.grid(row=4, column=0, sticky="w", padx=20, pady=5)

        # "Incorporate G–Quadruplex formation..." (gquad) -> Default: Unselected
        self.gquad_var = ctk.BooleanVar(value=False)
        self.chk_gquad = ctk.CTkCheckBox(self.frame, text="Incorporate G–Quadruplex formation into the structure prediction algorithm", 
                                         variable=self.gquad_var, font=("Arial", 12))
        self.chk_gquad.grid(row=5, column=0, sticky="w", padx=20, pady=5)

    def get_folding_params(self):
        """Returns the dictionary for 'folding_params' keys managed by this tab."""
        return {
            "noLP": self.noLP_var.get(),
            "noClosingGU": self.noClosingGU_var.get(),
            "gquad": self.gquad_var.get(),
            "circ": self.circ_var.get(),
            "noGU": False 
        }

    def get_algorithms(self):
        """Returns the dictionary for 'algorithms'."""
        pf = (self.algo_var.get() == 0)
        return {
            "partition_function": pf,
            "mfe": True
        }

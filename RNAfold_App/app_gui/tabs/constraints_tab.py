import customtkinter as ctk

class ConstraintsTab:
    """
    Implements the 'Folding Constraints' section matching the online RNAfold server.
    """
    def __init__(self, parent_frame, app_instance):
        self.app = app_instance
        self.frame = parent_frame
        
        self.frame.grid_columnconfigure(0, weight=1)

        # 1. Legend
        # Using a frame for the legend
        legend_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        legend_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        l1 = (
            "| : paired with another base\n"
            "x : base must not pair\n"
            ". : no constraint at all"
        )
        l2 = (
            "> : base i is paired with a base j>i\n"
            "< : base i is paired with a base j<i\n"
            "matching brackets ( ) : base i pairs base j"
        )
        # Legend keeps Consolas 11 - appropriate for code/symbols
        ctk.CTkLabel(legend_frame, text=l1, justify="left", font=("Consolas", 11)).pack(side="left", anchor="n", padx=10)
        ctk.CTkLabel(legend_frame, text=l2, justify="left", font=("Consolas", 11)).pack(side="left", anchor="n", padx=30)

        # 2. Label
        ctk.CTkLabel(self.frame, text="Paste or type your structure constraint using the symbols described above here:",
                     anchor="w", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=(10, 0))

        # 3. Text Area
        self.constraint_text = ctk.CTkTextbox(self.frame, height=80, font=("Consolas", 12))
        self.constraint_text.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # 4. Enforce Checkbox
        # Default: Disabled (unchecked)
        self.enforce_var = ctk.BooleanVar(value=False)
        self.chk_enforce = ctk.CTkCheckBox(self.frame, text="Enforce Constrained pairing pattern", 
                                           variable=self.enforce_var, font=("Arial", 12))
        self.chk_enforce.grid(row=3, column=0, sticky="w", padx=10, pady=10)

        # 5. Note
        note_text = ("Note: The string for the structure constraint must be of the length of the sequence. "
                     "Leave this field blank if no constraints should be applied during structure predictions.")
        ctk.CTkLabel(self.frame, text=note_text, text_color="gray", wraplength=800, justify="left", font=("Arial", 11)).grid(row=4, column=0, sticky="w", padx=10, pady=5)

    def get_values(self):
        """Returns constraint dictionary for profile."""
        text = self.constraint_text.get("0.0", "end").strip()
        return {
            "enforce": self.enforce_var.get(),
            "string": text if text else None,
            "file": None
        }

    def get_shape_values(self):
        return None

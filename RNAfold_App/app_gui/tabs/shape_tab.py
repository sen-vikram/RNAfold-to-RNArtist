import customtkinter as ctk
from tkinter import filedialog

class ShapeTab:
    """
    Implements the 'SHAPE reactivity data' section.
    """
    def __init__(self, parent_frame, app_instance):
        self.app = app_instance
        self.frame = parent_frame
        
        self.frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frame, text="File with SHAPE reactivity data:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        self.shape_file_path = ctk.StringVar()
        self.shape_entry = ctk.CTkEntry(self.frame, textvariable=self.shape_file_path, placeholder_text="No file chosen", width=300)
        self.shape_entry.grid(row=0, column=1, sticky="w", padx=10)
        
        ctk.CTkButton(self.frame, text="Choose file", command=self.browse_shape, width=100).grid(row=0, column=2, padx=10)

        # Advanced SHAPE params (Method, Slope, Intercept)
        # The online version has more options, but for now we keep the ones we had.
        
        ctk.CTkLabel(self.frame, text="Conversion Method:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.method_var = ctk.StringVar(value="Deigan")
        ctk.CTkOptionMenu(self.frame, variable=self.method_var, values=["Deigan", "Zarringhalam", "Washietl"]).grid(row=1, column=1, sticky="w", padx=10)

        param_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        param_frame.grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=5)
        
        ctk.CTkLabel(param_frame, text="Slope (m):").pack(side="left")
        self.slope_var = ctk.StringVar(value="1.8")
        ctk.CTkEntry(param_frame, textvariable=self.slope_var, width=60).pack(side="left", padx=5)
        
        ctk.CTkLabel(param_frame, text="Intercept (b):").pack(side="left", padx=(10, 0))
        self.intercept_var = ctk.StringVar(value="-0.6")
        ctk.CTkEntry(param_frame, textvariable=self.intercept_var, width=60).pack(side="left", padx=5)

    def browse_shape(self):
        path = filedialog.askopenfilename(filetypes=[("Data files", "*.dat *.txt"), ("All files", "*.*")])
        if path:
            self.shape_file_path.set(path)

    def get_shape_values(self):
        path = self.shape_file_path.get()
        return {
            "file": path if path else None,
            "method": self.method_var.get(),
            "slope": float(self.slope_var.get()),
            "intercept": float(self.intercept_var.get())
        }

import customtkinter as ctk

class AccordionFrame(ctk.CTkFrame):
    def __init__(self, parent, title="Accordion", start_collapsed=True):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.animation_step = 0.02
        self.collapsed = start_collapsed
        
        # 1. Toggle Button (Header)
        # We use a button that spans the full width to act as the header
        self.toggle_btn = ctk.CTkButton(
            self, 
            text=f"▶ {title}" if start_collapsed else f"▼ {title}", 
            command=self.toggle, 
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            anchor="w", 
            font=("Arial", 12, "bold"),
            height=30
        )
        self.toggle_btn.grid(row=0, column=0, sticky="ew")

        # 2. Content Frame
        # This frame will hold the actual content. We show/hide it.
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        if not start_collapsed:
            self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
    
    def toggle(self):
        if self.collapsed:
            # Expand
            self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
            self.toggle_btn.configure(text=self.toggle_btn.cget("text").replace("▶", "▼"))
            self.collapsed = False
        else:
            # Collapse
            self.content_frame.grid_forget()
            self.toggle_btn.configure(text=self.toggle_btn.cget("text").replace("▼", "▶"))
            self.collapsed = True

    def get_content_frame(self):
        return self.content_frame

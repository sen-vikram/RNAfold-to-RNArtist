import customtkinter as ctk
from tkinter import filedialog
import os

class InputTab:
    def __init__(self, parent_frame, app_instance):
        self.app = app_instance
        self.frame = parent_frame
        
        # Grid layout for the tab frame
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_rowconfigure(3, weight=1) # Adjusted row weight

        # 1. Selection Mode
        self.selection_label = ctk.CTkLabel(self.frame, text="Select Input Type:", font=("Arial", 14, "bold"))
        self.selection_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.input_mode = ctk.StringVar(value="file")
        
        self.radio_file = ctk.CTkRadioButton(self.frame, text="Single FASTA File (or Paste below)", variable=self.input_mode, value="file", command=self.on_mode_change)
        self.radio_file.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.radio_dir = ctk.CTkRadioButton(self.frame, text="Directory of FASTAs", variable=self.input_mode, value="dir", command=self.on_mode_change)
        self.radio_dir.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        # Removed explicit Paste RadioButton as requested

        # 2. Path Selection
        self.path_entry = ctk.CTkEntry(self.frame, placeholder_text="No file selected... (Paste sequence below if empty)")
        self.path_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.browse_btn = ctk.CTkButton(self.frame, text="Browse", command=self.browse_path)
        self.browse_btn.grid(row=1, column=2, padx=10, pady=10)

        # 3. Preview/Input Area
        self.preview_label = ctk.CTkLabel(self.frame, text="Content Preview / Input:", font=("Arial", 12, "bold"))
        self.preview_label.grid(row=2, column=0, padx=10, pady=(20, 0), sticky="nw")
        
        # Instruction Label (Small font)
        self.help_label = ctk.CTkLabel(self.frame, text="(Paste FASTA sequence here OR select file above)", font=("Arial", 10), text_color="gray")
        self.help_label.grid(row=3, column=0, padx=10, sticky="nw")

        # Preview Box (Editable by default for pasting)
        self.preview_box = ctk.CTkTextbox(self.frame, height=50) # Small height as requested
        self.preview_box.grid(row=2, column=1, rowspan=2, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.preview_box.insert("0.0", "") # Empty by default

    def on_mode_change(self):
        mode = self.input_mode.get()
        # Ensure box is cleared or reset if switching modes, though logic is now simpler
        if mode == "dir":
            self.path_entry.configure(placeholder_text="Select Directory...")
            self.preview_box.delete("0.0", "end")
            self.preview_box.insert("0.0", "Directory mode selected.")
        else:
            self.path_entry.configure(placeholder_text="No file selected... (Paste sequence below if empty)")
            if self.preview_box.get("0.0", "end").strip() == "Directory mode selected.":
                 self.preview_box.delete("0.0", "end")

    def browse_path(self):
        mode = self.input_mode.get()
        path = ""
        if mode == "file":
            path = filedialog.askopenfilename(filetypes=[("FASTA files", "*.fasta *.fa *.txt"), ("All files", "*.*")])
        elif mode == "dir":
            path = filedialog.askdirectory()
        
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)
            self.load_preview(path)

    def load_preview(self, path):
        # Clear previous content and show loading state
        self.preview_box.configure(state="normal")
        self.preview_box.delete("0.0", "end")
        self.preview_box.insert("0.0", "Loading preview...")
        self.preview_box.configure(state="disabled")

        import threading
        def _read_file():
            content = ""
            try:
                if os.path.isfile(path):
                    with open(path, "r") as f:
                        content = f.read(2000) # Read slightly more
                        if len(content) == 2000:
                            content += "\n... (truncated)"
                elif os.path.isdir(path):
                    files = [f for f in os.listdir(path) if f.endswith(('.fasta', '.fa', '.txt'))]
                    content = f"Found {len(files)} potential FASTA files:\n"
                    for f in files[:10]:
                        content += f"- {f}\n"
                    if len(files) > 10:
                        content += "... and more."
            except Exception as e:
                content = f"Error reading path: {e}"

            # Update UI on main thread (safe in Tkinter via after or just careful calls, 
            # CustomTkinter usually handles thread-safe calls reasonably well or we use app.after)
            # For strict safety we should use after, but for simple text insert often works.
            # Let's use self.frame.after to be safe.
            self.frame.after(0, lambda: self._update_preview_content(content))

        threading.Thread(target=_read_file, daemon=True).start()

    def _update_preview_content(self, content):
        self.preview_box.configure(state="normal")
        self.preview_box.delete("0.0", "end")
        self.preview_box.insert("0.0", content)
        self.preview_box.configure(state="disabled")
        
    def get_selected_path(self):
        mode = self.input_mode.get()
        path_val = self.path_entry.get().strip()

        if mode == "dir":
            return path_val if path_val else None
        
        # File Mode Logic:
        # 1. If Path Entry has content -> Use File
        if path_val:
            return path_val
        
        # 2. If Path Entry is Empty -> Check Text Box for content (Manual Paste)
        content = self.preview_box.get("0.0", "end").strip()
        if content:
             # Sanity check: ensure it looks slightly like FASTA or just sequence?
             # Engine handles raw sequence usually, but FASTA header is safer.
             # If user pastes just sequence, we might want to prepend header if missing?
             # For now, raw dump.
             
             temp_file = os.path.abspath("temp_manual_input.fasta")
             try:
                with open(temp_file, "w") as f:
                    # If it doesn't start with >, add a dummy header?
                    # ViennaRNA usually handles raw sequences in files too.
                    if not content.startswith(">"):
                        f.write(">manual_input\n")
                    f.write(content)
                return temp_file
             except Exception as e:
                print(f"Error saving temp input: {e}")
                return None
        
        return None

import customtkinter as ctk
import yaml
import os
import sys
from PIL import Image

class VisualTab:
    def __init__(self, frame, app=None, colormaps_path="colormaps.yaml", input_path=".", catalog_dir="colormap_catalogs"):
        self.frame = frame
        self.app = app
        
        # Resolve paths for frozen app
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            self.colormaps_path = os.path.join(base_path, colormaps_path)
            self.catalog_dir = os.path.join(base_path, catalog_dir)
        else:
            self.colormaps_path = colormaps_path
            self.catalog_dir = catalog_dir
            
        self.colormaps_data = self.load_colormaps()
        self.categories = self.get_categories()
        
        # --- UI Components ---
        
        # 1. Visualization Category
        ctk.CTkLabel(self.frame, text="Colormap Category:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        self.category_var = ctk.StringVar(value="rna_analysis")
        self.category_dropdown = ctk.CTkOptionMenu(self.frame, variable=self.category_var, values=self.categories, command=self.update_colormaps_and_image)
        self.category_dropdown.grid(row=0, column=1, sticky="w", padx=10, pady=(10, 0))
        
        # 2. Catalog Image Preview
        self.image_label = ctk.CTkLabel(self.frame, text="Loading Preview...")
        self.image_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        # 3. Colormap Selection
        ctk.CTkLabel(self.frame, text="Select Colormap:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
        self.colormap_var = ctk.StringVar()
        self.colormap_dropdown = ctk.CTkOptionMenu(self.frame, variable=self.colormap_var)
        self.colormap_dropdown.grid(row=2, column=1, sticky="w", padx=10, pady=(10, 0))
        
        # 4. Reverse Toggle
        self.reverse_var = ctk.BooleanVar(value=False)
        self.chk_reverse = ctk.CTkCheckBox(self.frame, text="Reverse Gradient (flip colors)", variable=self.reverse_var, font=("Arial", 12))
        self.chk_reverse.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=10)
        
        # 5. Coloring Mode
        ctk.CTkLabel(self.frame, text="Coloring Mode:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))
        self.mode_var = ctk.StringVar(value="all_pi")
        self.mode_dropdown = ctk.CTkOptionMenu(self.frame, variable=self.mode_var, values=["all_pi", "paired_only"])
        self.mode_dropdown.grid(row=4, column=1, sticky="w", padx=10, pady=(10, 0))
        
        # Initial Population
        self.update_colormaps_and_image("rna_analysis")

    def load_colormaps(self):
        if os.path.exists(self.colormaps_path):
            with open(self.colormaps_path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def get_categories(self):
        # Filter out metadata keys
        if not self.colormaps_data:
            return ["Default"]
        
        # Define preferred order
        preferred_order = ["rna_analysis", "scientific_favorites", "sequential", "diverging", "qualitative", "cyclic"]
        
        # Get all available keys that are actual categories
        available_keys = [k for k in self.colormaps_data.keys() if k not in ["default", "categories", "legacy_and_specialized"]]
        
        # Reorder available keys based on preferred order, appending any others at the end
        ordered_cats = [c for c in preferred_order if c in available_keys]
        for c in available_keys:
            if c not in ordered_cats:
                ordered_cats.append(c)
                
        return ordered_cats

    def update_colormaps_and_image(self, category):
        # Update Image
        img_filename = f"{category}.png"
        img_path = os.path.join(self.catalog_dir, img_filename)
        
        if os.path.exists(img_path):
            try:
                # Load and resize for preview (max width 400ish)
                pil_img = Image.open(img_path)
                w, h = pil_img.size
                target_w = 400
                target_h = int(h * (target_w / w))
                
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(target_w, target_h))
                self.image_label.configure(image=ctk_img, text="")
            except Exception as e:
                self.image_label.configure(image=None, text=f"Error loading image: {e}")
        else:
            self.image_label.configure(image=None, text=f"No preview available for '{category}'")

        # Update Colormap Dropdown
        if category in self.colormaps_data:
            # Filter out _r variants to avoid redundancy with the Reverse checkbox
            # Do NOT sort, preserve yaml/image order
            cmaps = [name for name in self.colormaps_data[category].keys() if not name.endswith("_r")]
            
            self.colormap_dropdown.configure(values=cmaps)
            
            if cmaps:
                # Set default: coolwarm for rna_analysis, otherwise first item
                if category == "rna_analysis" and "coolwarm" in cmaps:
                    self.colormap_var.set("coolwarm")
                else:
                    self.colormap_var.set(cmaps[0])
            else:
                self.colormap_var.set("")
        else:
             self.colormap_dropdown.configure(values=["default"])
             self.colormap_var.set("default")

    def get_data(self):
        # Handle logic for name + reverse
        base_name = self.colormap_var.get()
        reverse = self.reverse_var.get()
        
        # Since dropdown now filters out _r, we simply append it if reverse is checked
        final_name = base_name + "_r" if reverse else base_name
        
        return {
            "visualization": {
                "colormap": final_name,
                "coloring_mode": self.mode_var.get(),
                "base_colormap": base_name, # For UI restoration if needed
                "reverse": reverse 
            }
        }

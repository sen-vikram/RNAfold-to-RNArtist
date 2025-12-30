# Legacy Script: RNAfold to RNArtist (v4)

This folder contains the **Command Line** version of the pipeline. Use this if you want to run batch processing without the GUI or integrate it into other scripts.

**Recommended Script:** `RNAfold_to_RNArtist_CLI.py`

---

## 🚀 Quick Start

### 1. Prerequisites
You need **Python 3** and **Java (JRE 8+)**.

**Install Dependencies:**
```bash
pip install -r requirements.txt
```
*(Note: Ensure `ViennaRNA` is correctly installed for your system).*

### 2. Run the Script
The script takes a **FASTA file** or a **folder of FASTA files** as input.

**Command Syntax:**
```bash
python RNAfold_to_RNArtist_CLI.py <INPUT_PATH> [THREADS]
```

### 3. Examples

**Process a single file:**
```bash
python RNAfold_to_RNArtist_CLI.py sequences.fasta
```

**Process a folder of files:**
```bash
python RNAfold_to_RNArtist_CLI.py my_data_folder/
```

**Process with parallel speed (e.g., 4 CPU cores):**
```bash
python RNAfold_to_RNArtist_CLI.py my_data_folder/ 4
```

---

## 📂 Output
Results are saved in the `outputs/` folder (created automatically).
- **Structure Plots**: SVG, PNG (via RNArtist)
- **Data**: CSVs for probability, Varna files, etc.

## ⚙️ Configuration
You can customize the output by editing these files in this folder:
- **`config.yaml`**: The main configuration file. Change `colormap: name: ...` here to select your preferred style.
- **`colormaps.yaml`**: A catalog of available color schemes.

### Using `colormaps.yaml`
This file serves as a **dictionary of valid colormaps**. The script uses it to validate your choice and display descriptions.

1.  **Browse Options**: Open this file to see valid names (e.g., `viridis`, `coolwarm`, `Spectral_r`) and their descriptions.
2.  **Select a Colormap**:
    *   Open `config.yaml`.
    *   Find the `colormap` section.
    *   Update the name: `name: "inferno_r"` (or any key from `colormaps.yaml`).
3.  **Add Custom Colormaps**: 
    *   If you use a standard Matplotlib colormap not listed here, you can add it under the appropriate category in `colormaps.yaml` to make it "valid" for the script's strict checking mode.
    *   Format: `colormap_name: "Description of what this does"`

# RNAfold to RNArtist

<div align="center">
  <img src="RNAfold_App/rna_icon.png" alt="RNAfold to RNArtist Logo" width="120">
  <br>
  <b>A powerful, modern GUI application for RNA/DNA structure prediction and visualization.</b>
  <br>
  <i>Combines the scientific accuracy of ViennaRNA with the artistic rendering of RNArtistCore.</i>
  <br><br>
  <img src="https://img.shields.io/badge/Version-v1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Platform-Windows-green" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</div>

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Getting Started](#-getting-started)
  - [Run the Executable (No Install)](#option-a-executable-windows-recommended)
  - [Run from Source](#option-b-run-from-source-developers)
- [How to Use the App](#-how-to-use-the-app)
- [Command Line Interface (CLI)](#-command-line-interface-cli)
- [Benchmarking](#-benchmarking)
- [Project Structure](#-project-structure)
- [Technical Details](#-technical-details)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## ✨ Key Features

| Feature                   | Description                                                                                    |
| :------------------------ | :--------------------------------------------------------------------------------------------- |
| **🖥️ Modern GUI**          | Sleek, dark-mode interface built with **CustomTkinter**.                                       |
| **⚡ Direct Engine**       | Runs the folding engine directly in Python memory (no fragile subprocess calls).               |
| **🎨 Visualization**       | Real-time **Colormap Previews** (Sequential, Diverging, RNA Analysis). Output to **SVG, PNG**. |
| **🧪 Scientific Accuracy** | Aligned with **RNAfold Web Server** defaults (`T=37°C`, `dangles=2`, `noLP=1`).                |
| **📂 Project Management**  | Organize outputs by sequence name. Automatic export of probability data and Vienna files.      |
| **🔄 Portable Config**     | Configuration files are resolved relative to engine location for maximum portability.          |

---

## 🚀 Getting Started

### Option A: Executable (Windows) [Recommended]

The easiest way to use the app. No Python installation required.

**Requirements:** Java 8+ (for RNArtistCore visualization)

1.  Go to the **[Releases](../../releases)** section of this repository.
2.  Download **`RNAfold_to_RNArtist_Windows_v1.0.0.zip`**.
3.  Extract the zip file to a folder of your choice.
4.  Double-click **`RNAfold_to_RNArtist.exe`**.
5.  The app will launch instantly.

### Option B: Run from Source (Developers)

If you want to modify the code or run it on Linux/macOS.

**Prerequisites:**

- **Python 3.9+**
- **Java (JRE 8+)** (Required for the RNArtist visualization core)
- **ViennaRNA** Python bindings installed

**Install Dependencies:**
```bash
pip install -r RNAfold_App/requirements.txt
```

**Launch:**
```bash
cd RNAfold_App
python app.py
```

---

## 🎮 How to Use the App

1. **Input**: Select a `.fasta` file (single or multiple sequences) or paste a sequence directly.
2. **Configure**:
   - **Constraints**: Apply hard constraints using dot-bracket notation.
   - **Parameters**: Adjust temperature, salt, or algorithm options (MFE vs Partition Function).
   - **Visuals**: Pick a colormap (e.g., `coolwarm`, `viridis`, `plasma`) and see a live preview.
3. **Run**: Click the green **RUN ENGINE** button at the bottom.
4. **Results**: Check the `outputs/` folder for your generated structures and data.

---

## 💻 Command Line Interface (CLI)

For power users who need to process hundreds of files in batches, we preserve the robust CLI version.

- **Script**: `Legacy_Versions/RNAfold_to_RNArtist_CLI.py`
- **Documentation**: [Read CLI Docs](./Legacy_Versions/README.md)

**Usage:**
```bash
python RNAfold_to_RNArtist_CLI.py <input_file_or_folder> [max_workers]
```

---

## 📊 Benchmarking

The `Dev_Tools/` folder contains benchmark scripts with real RNA sequences from Rfam:

| File                     | Sequences | Purpose                    |
| ------------------------ | --------- | -------------------------- |
| `benchmark_single.fasta` | 1         | Quick single-sequence test |
| `benchmark_10seq.fasta`  | 10        | Multithread parallel test  |

**Run benchmarks:**
```bash
cd Dev_Tools
python benchmark_profiling.py single   # Quick test
python benchmark_profiling.py multi    # Full parallel test
```

---

## 📂 Project Structure

```text
RNAfold_to_RNArtist/
├── RNAfold_App/                 # MAIN APPLICATION
│   ├── app.py                   # GUI Entry point
│   ├── RNAfold_to_RNArtist_engine.py # Core Logic
│   ├── app_gui/                 # GUI components (tabs, widgets)
│   ├── bin/                     # RNArtistCore JAR
│   ├── config.yaml              # Configuration file
│   └── colormaps.yaml           # Visual styling configs
├── Legacy_Versions/             # CLI TOOLS
│   └── RNAfold_to_RNArtist_CLI.py
├── Dev_Tools/                   # DEVELOPMENT & BENCHMARKING
│   ├── benchmark_profiling.py
│   ├── benchmark_single.fasta
│   └── benchmark_10seq.fasta
├── Tests/                       # QUALITY ASSURANCE
│   └── run_tests.py
└── docs/                        # DOCUMENTATION
```

---

## 🔧 Technical Details

- **Engine**: Pure Python integration with the `ViennaRNA` Python interface (SWIG bindings).
- **Visualization**: Generates `.kts` (Kotlin Script) files rendered by the embedded `RNArtistCore.jar`.
- **Packaging**: Built with PyInstaller in "One-Directory" mode for fast startup.
- **Configuration**: YAML-based config with portable path resolution.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 **Vikram Sen** ([@sen-vikram](https://github.com/sen-vikram))

---

## 👏 Acknowledgements

- **Original Concept & Code**: Vikram Sen
- **AI Assistance**: Code architecture and GUI development assisted by AI coding agents.
- **Core Technologies**:
  - [ViennaRNA Package](https://www.tbi.univie.ac.at/RNA/ViennaRNA/doc/html/api_python.html) (Folding Engine)
  - [RNArtistCore](https://github.com/fjossinet/RNArtistCore) (Visualization)
  - [Matplotlib](https://matplotlib.org/) (Colormap support)
  - [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (UI Framework)

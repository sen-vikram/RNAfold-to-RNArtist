# RNAfold to RNArtist (App)

<div align="center">
  <img src="RNAfold_App/rna_icon.png" alt="RNAfold to RNArtist Logo" width="120">
  <br>
  <b>A powerful, modern GUI application for RNA/DNA structure prediction and visualization.</b>
  <br>
  <i>Combines the scientific accuracy of ViennaRNA with the artistic rendering of RNArtistCore.</i>
</div>

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Getting Started](#-getting-started)
  - [Run the Executable (No Install)](#option-a-executable-windows-recommended)
  - [Run from Source](#option-b-run-from-source-developers)
- [How to Use the App](#-how-to-use-the-app)
- [Command Line Interface (CLI)](#-command-line-interface-cli)
- [Project Structure](#-project-structure)
- [Technical Details](#-technical-details)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## ✨ Key Features

This application (v5) represents a complete overhaul of the original scripts, moving to a fully integrated GUI and Engine.

| Feature                   | Description                                                                                    |
| :------------------------ | :--------------------------------------------------------------------------------------------- |
| **🖥️ Modern GUI**          | Sleek, dark-mode interface built with**CustomTkinter**.                                        |
| **⚡ Direct Engine**       | Runs the folding engine directly in Python memory (no fragile subprocess calls).               |
| **🎨 Visualization**       | Real-time**Colormap Previews** (Sequential, Diverging, RNA Analysis). Output to **SVG, PNG**.  |
| **🧪 Scientific Accuracy** | Aligned with**RNAfold Web Server** defaults (`T=37°C`, `dangles=2`, `noLP=1`).                 |
| **📂 Project Management**  | Organize outputs by sequence name. Automatic export of probability data (CSV) and Varna files. |

---

## 🚀 Getting Started

### Option A: Executable (Windows) [Recommended]

The easiest way to use the app. No Python installation required.

1.  Go to the **[Releases](../../releases)** section of this repository.
2.  Download the **`RNAfold_to_RNArtist_Windows.zip`** file.
3.  Extract the zip file to a folder of your choice.
4.  Double-click **`RNAfold_to_RNArtist.exe`**.
5.  The app will launch instantly.

### Option B: Run from Source (Developers)

If you want to modify the code or run it on Linux/macOS.

**Prerequisites**:

- **Python 3.9+**
- **Java (JRE 8+)** (Required for the RNArtist visualization core)
- Dependencies:
  ```bash
  pip install -r RNAfold_App/requirements.txt
  ```

**Launch**:

```bash
cd RNAfold_App
python app.py
```

---

## 🎮 How to Use the App

1. **Input**: Select a `.fasta` file (can contain single or multiple sequence in fasta format)or paste a sequence directly in the "Input" tab.
2. **Configure**:
   - **Constraints**: Apply hard constraints or shape reactivity data.
   - **Parameters**: Adjust temperature, salt, or algorithm options (MFE vs Partition Function).
   - **Visuals**: Pick a colormap (e.g., `viridis`, `plasma`, `ocean`) and see a live preview.
3. **Run**: Click the green **RUN ENGINE** button.
4. **Results**: Check the `outputs/` folder for your generated structures and data.

---

## 💻 Command Line Interface (CLI)

For power users who need to process hundreds of files in batches, we preserve the robust CLI version.

- **Script**: `Legacy_Versions/RNAfold_to_RNArtist_CLI.py`
- **Documentation**: [Read CLI Docs](./Legacy_Versions/README.md)

Validation scripts are also available in the `Tests/` directory to ensure your environment is set up correctly.

---

## 📂 Project Structure

A quick guide to navigating this repository:

```text
RNAfold_to_RNArtist/
├── RNAfold_App/                 # MAIN APPLICATION (v5)
│   ├── app.py                   # GUI Entry point
│   ├── RNAfold_to_RNArtist_engine.py # Core Logic
│   ├── dist/                    # Compiled Executable
│   └── colormaps.yaml           # Visual styling configs
├── Legacy_Versions/             # CLI TOOLS
│   └── RNAfold_to_RNArtist_CLI.py    # Command Line Script
├── Tests/                       # QUALITY ASSURANCE
│   └── run_tests.py             # Validation Runner
└── docs/                        # DOCUMENTATION
```

---

## 🔧 Technical Details

- **Engine**: Pure Python integration with the `ViennaRNA` Python interface (swig).
- **Visualization**: Generates `.kts` (Kotlin Script) files which are rendered by the embedded `RNArtistCore.jar`.
- **Packaging**: Built with PyInstaller in "One-Directory" mode for fast startup.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 **Vikram Sen** ([@sen-vikram](https://github.com/sen-vikram))

---

## 👏 Acknowledgements

- **Original Concept & Code**: Vikram Sen
- **AI Assistance**: Code architecture and GUI development assisted by AI coding agents.
- **Core Technologies**:
  - [ViennaRNA Package](https://www.tbi.univie.ac.at/RNA/) (Folding Engine)
  - [RNArtistCore](https://github.com/RNArtist/RNArtistCore) (Visualization)
  - [Matplotlib](https://matplotlib.org/) (Legacy CLI plotting)
  - [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (UI Framework)

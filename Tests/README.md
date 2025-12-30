# Test Suite

This folder contains verification scripts to ensure the **RNAfold to RNArtist** engine works correctly on your system.

## 🚀 Quick Run (Recommended)
Run the consolidated test runner to execute all checks at once:

```bash
cd Tests
python run_tests.py
```

If everything is green, your installation (Python + Java + Dependencies) is perfect!

---

## 🧪 Detailed Scripts

| Script                       | Purpose                                                                                                         |
| :--------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| **`verify_engine_logic.py`** | **Unit Tests**: Checks if parameters (Temperature, Dangles, NoLP) are passing correctly to the ViennaRNA model. |
| **`verify_vis.py`**          | **Viz Check**: Runs a dummy sequence to ensure RNArtistCore (Java) is callable and generates a script.          |
| **`verify_full_run.py`**     | **Integration**: Simulates a real GUI run (creates temp files, runs engine, cleans up).                         |
| **`debug_engine.py`**        | **Debugging**: Minimal script to check if the `RNA` python module imports correctly.                            |

## 📁 Test Data
- `test.fasta`: A sample file you can use for manual testing in the main App.

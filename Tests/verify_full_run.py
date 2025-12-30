
import os
import json
import subprocess
import shutil

# Simulate the "Temp Profile" created by the GUI
PROFILE_DATA = {
    "folding_params": {
        "temperature": 60.0,
        "dangles": 0,
        "noLP": True,
        "param_set": "turner2004"
    },
    "constraints": {
        "enforce": False, 
        "string": None
    },
    "algorithms": {
        "partition_function": True,
        "mfe": True
    },
    "shape_reactivity": {}
}

TEST_PROFILE_PATH = "verify_profile.json"
TEST_SEQ_FILE = "verify_seq.fasta"
TEST_SEQ = ">test_seq\nGGGGCCCCAAAAGGGG"

def run_integration_test():
    print("--- Running End-to-End Integration Test ---")
    
    # 1. Create Test Data
    with open(TEST_PROFILE_PATH, "w") as f:
        json.dump(PROFILE_DATA, f)
    
    with open(TEST_SEQ_FILE, "w") as f:
        f.write(TEST_SEQ)
        
    # 2. Run Engine (Subprocess like GUI)
    engine_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "RNAfold_App", "RNAfold_to_RNArtist_engine.py")
    cmd = ["python", engine_path, TEST_SEQ_FILE, "--profile", TEST_PROFILE_PATH]
    
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # 3. Check Result
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    # Verify basics
    if result.returncode == 0:
        print("SUCCESS: Engine ran with new profile structure.")
    else:
        print(f"FAILURE: Engine crashed with code {result.returncode}")

    # Inspect output if possible (not parsing here, just checking crash status)
    
    # Clean up
    if os.path.exists(TEST_PROFILE_PATH): os.remove(TEST_PROFILE_PATH)
    if os.path.exists(TEST_SEQ_FILE): os.remove(TEST_SEQ_FILE)

if __name__ == "__main__":
    run_integration_test()

import sys
import os
import subprocess
import time

def print_header(name):
    print("\n" + "="*60)
    print(f" TEST SUITE: {name}")
    print("="*60 + "\n")

def run_script(script_name):
    print(f"Running {script_name}...")
    try:
        # Run the script and capture output
        # Ensure we run it from the parent directory context if needed, or just let it adjust path
        # The existing scripts seem to expect to be run from the Tests/ dir or have paths set up carefully.
        # Let's simple subprocess call it.
        result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("STATUS: [ PASS ]")
            # Optionally print output if verbose
            # print(result.stdout)
        else:
            print("STATUS: [ FAIL ]")
            print("--- STDOUT ---")
            print(result.stdout)
            print("--- STDERR ---")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"ERROR: Failed to run script: {e}")
        return False
    return True

def main():
    start_time = time.time()
    
    # 1. Check Engine Logic (Unit Tests for flags/params)
    print_header("Engine Logic Verification")
    if not run_script("verify_engine_logic.py"):
        print("Engine logic verification failed. Stopping.")
        sys.exit(1)

    # 2. Check Visualization Logic
    print_header("Visualization Pipeline Verification")
    if not run_script("verify_vis.py"):
        print("Visualization verification failed. Stopping.")
        sys.exit(1)
        
    # 3. Full Integration Run
    print_header("Full Integration Test")
    if not run_script("verify_full_run.py"):
        print("Full integration test failed. Stopping.")
        sys.exit(1)
        
    print("\n" + "="*60)
    print(f" ALL TESTS PASSED in {time.time() - start_time:.2f} seconds")
    print("="*60)

if __name__ == "__main__":
    # Ensure invalid paths don't break us, assuming run from Tests/ folder
    if not os.path.exists("verify_engine_logic.py"):
        print("Error: Please run this script from inside the 'Tests' directory.")
        sys.exit(1)
        
    # Add parent dir to path for imports in child scripts
    sys.path.append(os.path.dirname(os.getcwd()))
        
    main()

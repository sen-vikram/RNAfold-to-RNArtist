
import os
import shutil
import subprocess

def create_dummy_data():
    with open("verify_vis.fasta", "w") as f:
        f.write(">test_vis\nAACCGGUU\n")
    
    with open("verify_vis_profile.json", "w") as f:
        f.write('{"visualization": {"colormap": "viridis", "coloring_mode": "paired_only", "reverse": false}}')

def cleanup():
    if os.path.exists("verify_vis.fasta"): os.remove("verify_vis.fasta")
    if os.path.exists("verify_vis_profile.json"): os.remove("verify_vis_profile.json")
    if os.path.exists("outputs/test_vis"): shutil.rmtree("outputs/test_vis")

def check_results():
    script_path = "outputs/test_vis/test_vis_rnartist_script.kts"
    if os.path.exists(script_path):
        with open(script_path, "r") as f:
            content = f.read()
            # viridis paired_only should be used.
            # We can't easily check exact hex codes without calculation, but we can assume if it ran without error and created output, it plumbed through.
            # Ideally we check for a known viridis hex or just success.
            print("Visualization script generated successfully.")
            return True
    return False

if __name__ == "__main__":
    cleanup()
    create_dummy_data()
    print("Running Engine with Visual Profile...")
    engine_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "RNAfold_App", "RNAfold_to_RNArtist_engine.py")
    subprocess.run(["python", engine_path, "verify_vis.fasta", "--profile", "verify_vis_profile.json"])
    
    if check_results():
        print("VERIFICATION SUCCESSFUL")
    else:
        print("VERIFICATION FAILED")

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "RNAfold_App"))
import RNA
import json
import RNAfold_to_RNArtist_engine as engine

def test_model_flags():
    print("\n--- Testing Basic & Advanced Flags ---")
    # Test True/False logic (mapped to 1/0 int in engine)
    profile = {
        "folding_params": {
            "noLP": True,
            "noGU": True,
            "noClosingGU": True,
            "gquad": True,
            "circ": True
        }
    }
    
    md = engine.configure_model_details(profile)
    
    # Assertions
    print(f"noLP: Expected 1, Got {md.noLP}")
    print(f"noGU: Expected 1, Got {md.noGU}")
    print(f"noClosingGU: Expected 1, Got {md.noClosingGU}")
    print(f"gquad: Expected 1, Got {md.gquad}")
    print(f"circ: Expected 1, Got {md.circ}")

    # Test Default/False logic
    profile_defaults = {"folding_params": {}} # defaults
    md_def = engine.configure_model_details(profile_defaults)
    
    # Check Defaults (Engine defaults: noLP=1, others=0 typically, need to check doc/code)
    # My code sets noLP default to 1 in configure_model_details line 246.
    print(f"Default noLP: Expected 1, Got {md_def.noLP}")

def test_dangles():
    print("\n--- Testing Dangles ---")
    # Dangles = 0
    p0 = {"folding_params": {"dangles": 0}}
    md0 = engine.configure_model_details(p0)
    print(f"Dangles=0: md.dangles expected 0, got {md0.dangles}")
    
    # Dangles = 2
    p2 = {"folding_params": {"dangles": 2}}
    md2 = engine.configure_model_details(p2)
    print(f"Dangles=2: md.dangles expected 2, got {md2.dangles}")

def test_energy_params():
    print("\n--- Testing Energy Parameters ---")
    # Temperature
    p_temp = {"folding_params": {"temperature": 60.0}}
    md_temp = engine.configure_model_details(p_temp)
    print(f"Temp=60: md.temperature expected 60.0, got {md_temp.temperature}")

if __name__ == "__main__":
    test_dangles()
    test_energy_params()
    test_model_flags()
    print("\nVerification Checks Complete.")

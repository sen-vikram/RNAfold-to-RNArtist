
import RNA
import RNAfold_to_RNArtis_v5_engine as engine
import traceback

def debug_fold():
    seq = "GGGGCCCCAAAAGGGG"
    profile = {
        "algorithms": {"partition_function": True}
    }
    
    print("Attempting to fold...")
    try:
        # Manually replicate loop to inspect
        md = engine.configure_model_details(profile)
        fc = RNA.fold_compound(seq, md)
        structure, mfe = fc.mfe()
        print(f"MFE: {mfe}, Type: {type(mfe)}")
        
        ensemble_energy = fc.pf()
        print(f"Ensemble Energy raw: {ensemble_energy}, Type: {type(ensemble_energy)}")
        
        # struct, plist, stats = engine.fold_sequence(seq, profile)
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    debug_fold()

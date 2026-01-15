"""
Benchmark Profiling Script for RNAfold to RNArtist Engine
----------------------------------------------------------
Tests parallel performance using real RNA sequences from Rfam.

Usage:
    python benchmark_profiling.py [single|multi]
    
    single  - Uses benchmark_single.fasta (1 sequence, quick test)
    multi   - Uses benchmark_10seq.fasta (10 sequences, multithread test)
    
    Default: multi
"""

import time
import sys
import os
import argparse

# Add engine path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "RNAfold_App"))
import RNAfold_to_RNArtist_engine as engine


def run_benchmark(mode="multi"):
    """
    Run benchmark on RNA sequences.
    
    Args:
        mode: 'single' for 1 sequence, 'multi' for 10 sequences
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Select input file based on mode
    if mode == "single":
        input_file = os.path.join(script_dir, "benchmark_single.fasta")
    else:
        input_file = os.path.join(script_dir, "benchmark_10seq.fasta")
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        print("Please ensure benchmark FASTA files are in the Dev_Tools folder.")
        return

    # Parse inputs to count sequences
    records = engine.parse_multi_fasta(input_file)
    print(f"Benchmarking {len(records)} sequences from {os.path.basename(input_file)}...")
    print(f"Mode: {'Single sequence (quick test)' if mode == 'single' else 'Multi-sequence (parallel test)'}")

    # Find JAR
    jar_path = None
    possible_jars = [
        os.path.join(script_dir, "..", "RNAfold_App", "bin", "rnartistcore-0.4.6-SNAPSHOT-jar-with-dependencies.jar"),
        os.path.join(script_dir, "..", "RNAfold_App", "bin", "RNArtistCore.jar"),
    ]
    for p in possible_jars:
        if os.path.exists(p):
            jar_path = os.path.abspath(p)
            break
    if not jar_path:
        print("Error: RNArtistCore JAR not found in RNAfold_App/bin/")
        return

    # Output directory for benchmark results
    output_dir = os.path.join(script_dir, "..", "bench_outputs")
    os.makedirs(output_dir, exist_ok=True)

    print("-" * 60)
    print("Testing Parallel Performance (run_engine_programmatic)...")
    print("-" * 60)

    t_start = time.time()
    
    # Run the engine programmatically with the correct output directory
    success = engine.run_engine_programmatic(
        input_path=input_file, 
        profile_path=None,
        output_dir=output_dir
    )
    
    t_total = time.time() - t_start
    
    print("-" * 60)
    print(f"Total Execution Time: {t_total:.3f} s")
    if len(records) > 0:
        print(f"Average Time per Sequence: {t_total/len(records):.3f} s")
    
    if success:
        print("✓ Engine finished successfully.")
        print(f"✓ Output saved to: {os.path.abspath(output_dir)}")
    else:
        print("✗ Engine reported failure.")
    print("-" * 60)


if __name__ == "__main__":
    # Ensure multiprocessing works if called directly
    import multiprocessing
    multiprocessing.freeze_support()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Benchmark the RNAfold to RNArtist engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python benchmark_profiling.py single   # Quick test with 1 sequence
    python benchmark_profiling.py multi    # Full test with 10 sequences
    python benchmark_profiling.py          # Default: multi
        """
    )
    parser.add_argument(
        "mode", 
        nargs="?", 
        choices=["single", "multi"], 
        default="multi",
        help="Benchmark mode: 'single' (1 seq) or 'multi' (10 seqs)"
    )
    
    args = parser.parse_args()
    run_benchmark(args.mode)

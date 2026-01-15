import os
import sys
import subprocess
import RNA
import numpy as np
import matplotlib
matplotlib.use('Agg') # Force non-interactive backend to avoid GUI/SVG dependency issues
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import yaml
import glob
from collections import defaultdict
import concurrent.futures
import shutil
import json
import argparse

import traceback

# Explicitly import matplotlib backends was removed. 
# We rely on PyInstaller hooks and the Agg backend text above.

# =============================
# YAML CONFIG LOADING
# =============================

# Get the directory where this engine file is located
_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_config(config_path='config.yaml'):
    """Load configuration from YAML file with multiple path resolution."""
    paths_to_check = []
    
    # 1. Check bundled path for frozen apps (PyInstaller)
    if getattr(sys, 'frozen', False):
        paths_to_check.append(os.path.join(sys._MEIPASS, config_path))
    
    # 2. Check relative to the engine file location (most reliable)
    paths_to_check.append(os.path.join(_ENGINE_DIR, config_path))
    
    # 3. Check current working directory (fallback)
    paths_to_check.append(config_path)
    
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Warning: Error parsing config file {path}: {e}")
    
    return {}

CONFIG = load_config()

# Helper to get config value with fallback
def get_config(key, default=None):
    return CONFIG.get(key, default)

# Helper functions to get nested config values with fallback
def get_nested_config(keys, default=None):
    d = CONFIG
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d

# =============================================================================
# COLORMAP CONFIGURATION (from external YAML file)
# =============================================================================
def load_colormaps(colormaps_file='colormaps.yaml'):
    """Load colormaps from external YAML file with multiple path resolution."""
    paths_to_check = []
    
    # 1. Check bundled path for frozen apps (PyInstaller)
    if getattr(sys, 'frozen', False):
        paths_to_check.append(os.path.join(sys._MEIPASS, colormaps_file))
    
    # 2. Check relative to the engine file location (most reliable)
    paths_to_check.append(os.path.join(_ENGINE_DIR, colormaps_file))
    
    # 3. Check current working directory (fallback)
    paths_to_check.append(colormaps_file)
    
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Warning: Error parsing colormaps file {path}: {e}")
    
    print(f"Warning: Colormaps file '{colormaps_file}' not found. Using built-in defaults.")
    return None

def get_all_colormaps(colormaps_data):
    """Extract all colormap names from the loaded data."""
    all_colormaps = {}
    if colormaps_data:
        for category, colormaps in colormaps_data.items():
            if isinstance(colormaps, dict) and category not in ['default', 'categories']:
                all_colormaps.update(colormaps)
    return all_colormaps

def validate_colormap(colormap_name, colormaps_data):
    """Validate if a colormap exists and return description if available."""
    if not colormaps_data:
        # Fallback to matplotlib validation only
        try:
            plt.get_cmap(colormap_name)
            return True, "Colormap available in matplotlib"
        except ValueError:
            return False, "Colormap not found in matplotlib"
    
    all_colormaps = get_all_colormaps(colormaps_data)
    
    if colormap_name in all_colormaps:
        return True, all_colormaps[colormap_name]
    else:
        # Check if it exists in matplotlib as fallback
        try:
            plt.get_cmap(colormap_name)
            return True, "Colormap available in matplotlib (not in config file)"
        except ValueError:
            return False, "Colormap not found in matplotlib or config file"

# Load colormaps from external file
COLORMAPS_DATA = load_colormaps()
ALL_COLORMAPS = get_all_colormaps(COLORMAPS_DATA) if COLORMAPS_DATA else {}

# Get selected colormap with validation
SELECTED_COLORMAP = CONFIG.get('colormap', {}).get('name', 'Spectral_r')
is_valid, description = validate_colormap(SELECTED_COLORMAP, COLORMAPS_DATA)

if not is_valid:
    print(f"Warning: Colormap '{SELECTED_COLORMAP}' not found. Using default 'Spectral_r'.")
    SELECTED_COLORMAP = 'Spectral_r'
    is_valid, description = validate_colormap(SELECTED_COLORMAP, COLORMAPS_DATA)

if is_valid and description:
    print(f"Using colormap: {SELECTED_COLORMAP} - {description}")

def list_available_colormaps(category=None):
    """List available colormaps, optionally filtered by category."""
    if not COLORMAPS_DATA:
        print("Colormaps file not loaded. Using matplotlib defaults.")
        return
    
    if category and category in COLORMAPS_DATA:
        print(f"\nAvailable colormaps in category '{category}':")
        print("=" * 60)
        for name, description in COLORMAPS_DATA[category].items():
            print(f"  {name:<20} - {description}")
    elif category:
        print(f"Category '{category}' not found. Available categories:")
        for cat in COLORMAPS_DATA.keys():
            if cat not in ['default', 'categories']:
                print(f"  - {cat}")
    else:
        print("\nAvailable colormap categories:")
        print("=" * 40)
        for cat, desc in COLORMAPS_DATA.get('categories', {}).items():
            count = len(COLORMAPS_DATA.get(cat, {}))
            print(f"  {cat:<15} ({count} colormaps) - {desc}")
        print(f"\nTotal colormaps available: {len(ALL_COLORMAPS)}")

# =============================================================================
# COLORING MODE CONFIGURATION (from YAML config)
# =============================================================================
COLORING_MODE = CONFIG.get('coloring_mode', {}).get('mode', 'paired_only')
# =============================================================================

def read_fasta(filepath):
    """Read FASTA format from .fasta or .txt files and extract header and sequence."""
    # Check if file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    # Check file extension
    file_ext = os.path.splitext(filepath)[1].lower()
    if file_ext not in ['.fasta', '.fa', '.txt']:
        print(f"Warning: File extension '{file_ext}' is not .fasta, .fa, or .txt")
    with open(filepath, 'r') as f:
        lines = f.readlines()
    header = None
    seq_lines = []
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        if line.startswith('>'):
            if header is None:
                header = line[1:].strip()
            else:
                print(f"Warning: Multiple headers found. Using first header: {header}")
                break
        else:
            seq_lines.append(line)
    if not seq_lines:
        raise ValueError("No sequence found in file")
    seq = ''.join(seq_lines)
    # Validate sequence (should only contain DNA/RNA bases)
    valid_bases = set('ATCGUatcgu')
    invalid_chars = set(seq) - valid_bases
    if invalid_chars:
        print(f"Warning: Invalid characters found in sequence: {invalid_chars}")
    return header, seq

def parse_multi_fasta(filepath):
    """Parse all sequences from a (multi-)FASTA file. Returns list of (header, seq)."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, 'r') as f:
        lines = f.readlines()
    records = []
    header = None
    seq_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            if header is not None and seq_lines:
                records.append((header, ''.join(seq_lines)))
                seq_lines = []
            header = line[1:].strip()
        else:
            seq_lines.append(line)
    if header is not None and seq_lines:
        records.append((header, ''.join(seq_lines)))
    return records

def get_sequence_name(header):
    """Extract clean sequence name from FASTA header."""
    if not header:
        import uuid
        return f"sequence_{uuid.uuid4().hex[:8]}"
    
    # Remove common problematic characters and take first word
    name = header.split()[0]  # Take first word
    name = name.replace('|', '_').replace(' ', '_').replace('\t', '_')
    name = ''.join(c for c in name if c.isalnum() or c in '_-')
    
    # Ensure name is not empty
    if not name:
        import uuid
        return f"sequence_{uuid.uuid4().hex[:8]}"
        
    # Previously we added "seq_" if it started with digit, user requested EXACT match if possible.
    # We will trust the sanitized name.
    
    return name

def create_output_filename(base_name, sequence_name, extension):
    """Create output filename with sequence name prefix."""
    return f"{sequence_name}_{base_name}.{extension}"

def load_profile(profile_path):
    """Load JSON profile for folding configuration."""
    if not profile_path:
        return {}
    if not os.path.exists(profile_path):
        print(f"Warning: Profile file '{profile_path}' not found. Using defaults.")
        return {}
    try:
        with open(profile_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading profile: {e}")
        return {}

def configure_model_details(profile):
    """Configure RNA model details from profile."""
    md = RNA.md()
    folding_params = profile.get('folding_params', {})
    
    # Basic Parameters
    if 'temperature' in folding_params: 
        md.temperature = float(folding_params['temperature'])
    else:
        md.temperature = 37.0 # Default

    if 'dangles' in folding_params: 
        md.dangles = int(folding_params['dangles'])
    else:
        md.dangles = 2 # Default
        
    if 'noLP' in folding_params: 
        md.noLP = int(folding_params['noLP'])
    else:
        md.noLP = 1 # Default

    # Advanced Parameters
    if 'noGU' in folding_params: md.noGU = int(folding_params['noGU'])
    if 'noClosingGU' in folding_params: md.noClosingGU = int(folding_params['noClosingGU'])
    if 'gquad' in folding_params: md.gquad = int(folding_params['gquad'])
    if 'circ' in folding_params: md.circ = int(folding_params['circ'])
    if 'max_bp_span' in folding_params: md.max_bp_span = int(folding_params['max_bp_span'])
    
    return md

def fold_sequence(seq, profile={}):
    """
    Fold sequence using RNAlib with profile-based configuration.
    """
    # Create model details object from profile
    md = configure_model_details(profile)
    
    # helper to apply global params safely
    folding_params = profile.get('folding_params', {})
    
    # Apply Parameter Set (Global State in process)
    param_set = folding_params.get('param_set', 'turner2004')
    if param_set == 'dna_matthews2004':
        RNA.params_load_DNA_Mathews2004()
    elif param_set == 'turner1999':
        RNA.params_load_RNA_Turner1999()
    elif param_set == 'andronescu2007':
        RNA.params_load_RNA_Andronescu2007()
    else:
        # Default Turner 2004 - explicitly load to reset if needed
        # Check if function exists (older versions might not have it exposed as function but is default)
        if hasattr(RNA, 'params_load_RNA_Turner2004'):
            RNA.params_load_RNA_Turner2004()

    # Apply Salt (if supported)
    if 'salt' in folding_params:
        salt_conc = float(folding_params['salt'])
        # Try global loader
        if hasattr(RNA, 'params_load_salt'):
           RNA.params_load_salt(salt_conc)
    
    # Create fold compound with model details
    fc = RNA.fold_compound(seq, md)
    

    # Apply Constraints
    constraints = profile.get('constraints', {})
    constraint_applied = False
    
    # 1. Hard Constraints from String (Dot-Bracket)
    if constraints.get('enforce', True):
        constraint_string = constraints.get('string')
        if constraint_string:
            if len(constraint_string) == len(seq):
                try:
                    # Use default options for dot-bracket parsing
                    fc.hc_add_from_db(constraint_string, RNA.CONSTRAINT_DB_DEFAULT)
                    constraint_applied = True
                except Exception as e:
                    print(f"Warning: Error adding constraints: {e}")
            else:
                print(f"Warning: Constraint string length ({len(constraint_string)}) does not match sequence length ({len(seq)}). Ignoring.")

    # 2. SHAPE Reactivity (Placeholder)
    shape_cfg = profile.get('shape_reactivity', {})
    if shape_cfg.get('file'):
        print("Info: SHAPE data loading requested but requires specific API verification. Skipping for this version.")

    # Compute MFE and Structure
    structure, mfe = fc.mfe()
    
    # Compute Partition Function
    algorithms = profile.get('algorithms', {})
    ensemble_energy = 0.0
    frequency = 0.0
    diversity = 0.0
    
    if algorithms.get('partition_function', True):
        # fc.pf() returns (structure, energy) or [structure, energy]
        pf_result = fc.pf()
        if isinstance(pf_result, (list, tuple)) and len(pf_result) >= 2:
            ensemble_energy = pf_result[1]
        elif isinstance(pf_result, float):
             ensemble_energy = pf_result
        else:
             print(f"Warning: Unexpected return from fc.pf(): {pf_result}")
             ensemble_energy = 0.0
        
        # Get base pair probabilities
        plist = fc.plist_from_probs(0.0)
        
        # Calculate Frequency of MFE structure in ensemble
        # Frequency = exp((E_ensemble - E_mfe) / RT)
        # temperature is in md.temperature already? No, need to check if ViennaRNA exposes calculation helper
        # Or manually: RT = 0.00198717 * (temperature + 273.15)
        kt = 0.00198717 * (md.temperature + 273.15)
        if kt > 0:
            frequency = np.exp((ensemble_energy - mfe) / kt)
            
        # Ensemble Diversity
        # fc.mean_bp_distance() calculates the mean base pair distance in the thermodynamic ensemble
        diversity = fc.mean_bp_distance()
    else:
        plist = []
    
    # Bundle stats
    stats = {
        "mfe": mfe,
        "ensemble_energy": ensemble_energy,
        "frequency": frequency,
        "diversity": diversity,
        "constraint_applied": constraint_applied
    }
    
    return structure, plist, stats

def compute_base_pairing_probabilities(seq, plist):
    length = len(seq)
    pi_values = np.zeros(length)
    for entry in plist:
        if entry.i == 0 and entry.j == 0:
            break
        pi_values[entry.i - 1] += entry.p
        pi_values[entry.j - 1] += entry.p
    return pi_values

def get_paired_status(structure):
    """Returns a boolean list where True means the base is paired in the MFE structure."""
    paired = [False] * len(structure)
    stack = []
    for idx, char in enumerate(structure):
        if char == '(': stack.append(idx)
        elif char == ')':
            i = stack.pop()
            paired[i] = True
            paired[idx] = True
    return paired

def map_probabilities_to_colors(pi_values, paired_status, colormap_name=SELECTED_COLORMAP, coloring_mode=COLORING_MODE):
    # Validate colormap with enhanced error handling
    is_valid, description = validate_colormap(colormap_name, COLORMAPS_DATA)
    
    if not is_valid:
        print(f"Warning: Colormap '{colormap_name}' not found. Using 'viridis' instead.")
        colormap_name = 'viridis'
        is_valid, description = validate_colormap(colormap_name, COLORMAPS_DATA)
    
    try:
        # print(f"Debug: Getting cmap '{colormap_name}' (Type: {type(colormap_name)})")
        cmap = plt.get_cmap(colormap_name)
    except ValueError:
        print(f"Error: Failed to load colormap '{colormap_name}'. Using 'viridis' instead.")
        cmap = plt.get_cmap('viridis')
    
    colors = []
    # print(f"Debug: Mapping {len(pi_values)} probabilities to colors using {coloring_mode}") # Verbose debug
    for pi, is_paired in zip(pi_values, paired_status):
        if coloring_mode == 'paired_only':
            value = min(pi, 1.0) if is_paired else min(1.0 - pi, 1.0)
        elif coloring_mode == 'all_pi':
            value = min(pi, 1.0)
        else:
            value = min(pi, 1.0)  # fallback
        color = cmap(value)
        colors.append(color)
    return colors

def safe_float(val, default):
    try:
        return float(val)
    except (TypeError, ValueError):
        return float(default)

def save_probability_results(seq, pi_values, colors, out_dir, colormap_name=SELECTED_COLORMAP, sequence_name="sequence"):
    # Get output size, font size, line width, and transparency from config
    width = safe_float(get_nested_config(['output', 'width'], 8), 8)
    height = safe_float(get_nested_config(['output', 'height'], 1.5), 1.5)
    font_size = safe_float(get_nested_config(['font', 'size'], 12), 12)
    line_width = safe_float(get_nested_config(['line', 'width'], 2), 2)
    transparency = safe_float(get_nested_config(['transparency'], 1.0), 1.0)
    
    # Get color bar configuration from YAML
    colorbar_cfg = CONFIG.get('colorbar', {})
    cb_formats = colorbar_cfg.get('format', 'png')  # Use PNG by default (SVG has bundling issues)
    
    # Force sanitization of formats to avoid SVG backend trigger
    if isinstance(cb_formats, str):
        cb_formats = [cb_formats]
    
    # Filter out 'svg' check removed - backend is now bundled
    # if 'svg' in cb_formats:
    #    print("Warning: SVG format detected in configuration. Removing it to prevent backend errors.")
    #    cb_formats = [fmt for fmt in cb_formats if fmt != 'svg']
    #    if not cb_formats:
    #        cb_formats = ['png']
    
    # print(f"Debug: Generating Colorbar. Formats: {cb_formats}")
    cb_orientation = colorbar_cfg.get('orientation', 'horizontal')
    # Add colorbar-specific width/height support
    cb_width = safe_float(colorbar_cfg.get('width', get_nested_config(['output', 'width'], 8)), 8)
    cb_height = safe_float(colorbar_cfg.get('height', get_nested_config(['output', 'height'], 1.5)), 1.5)
    # Convert single format to list for consistent processing
    if isinstance(cb_formats, str):
        cb_formats = [cb_formats]
    # Define format settings
    format_settings = {
        'svg': {'facecolor': 'none', 'transparent': True, 'dpi': None},
        'pdf': {'facecolor': 'none', 'transparent': True, 'dpi': None},
        'eps': {'facecolor': 'none', 'transparent': True, 'dpi': None},
        'png': {'facecolor': 'white', 'transparent': False, 'dpi': 300}
    }
    
    with open(os.path.join(out_dir, create_output_filename("base_pairing_probabilities_per_base", sequence_name, "txt")), "w") as f:
        f.write("Position\tBase\tPi\tColor_RGB\n")
        for i, (base, pi, color) in enumerate(zip(seq, pi_values, colors)):
            rgb = tuple(int(c * 255) for c in color[:3])
            f.write(f"{i+1}\t{base}\t{pi:.6f}\t{rgb}\n")
    
    # Adjust figure size for vertical orientation
    if cb_orientation == 'vertical':
        fig, ax = plt.subplots(figsize=(cb_height, cb_width))  # Swap width/height for vertical
        fig.subplots_adjust(right=0.8)  # Adjust for vertical color bar
    else:
        fig, ax = plt.subplots(figsize=(cb_width, cb_height))
    fig.subplots_adjust(bottom=0.5)
    
    # Validate colormap for color bar generation
    is_valid, description = validate_colormap(colormap_name, COLORMAPS_DATA)
    
    if not is_valid:
        print(f"Warning: Colormap '{colormap_name}' not found for color bar. Using 'viridis' instead.")
        colormap_name = 'viridis'
        is_valid, description = validate_colormap(colormap_name, COLORMAPS_DATA)
    
    try:
        cmap = plt.get_cmap(colormap_name)
    except ValueError:
        print(f"Error: Failed to load colormap '{colormap_name}' for color bar. Using 'viridis' instead.")
        cmap = plt.get_cmap('viridis')
    norm = mcolors.Normalize(vmin=0, vmax=1)
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cb1 = plt.colorbar(sm, cax=ax, orientation=cb_orientation)
    cb1.set_label(f'Base-Pairing Probability (Pi) - Colormap: {colormap_name}', fontsize=font_size)
    cb1.set_ticks([0, 0.25, 0.5, 0.75, 1.0])
    cb1.set_ticklabels(['0.0', '0.25', '0.5', '0.75', '1.0'])
    
    # Apply line width and transparency to tick lines
    if cb_orientation == 'horizontal':
        for l in cb1.ax.xaxis.get_ticklines():
            l.set_linewidth(line_width)
            l.set_alpha(transparency)
    else:
        for l in cb1.ax.yaxis.get_ticklines():
            l.set_linewidth(line_width)
            l.set_alpha(transparency)
    
    # Save color bar in all specified formats
    for cb_format in cb_formats:
        if cb_format in format_settings:
            settings = format_settings[cb_format]
            cb_path = os.path.join(out_dir, create_output_filename(f"base_pairing_probability_colorbar_{colormap_name}", sequence_name, cb_format))
            
            # Prepare savefig arguments
            save_args = {
                'fname': cb_path,
                'format': cb_format,
                'bbox_inches': 'tight',
                'facecolor': settings['facecolor'],
                'transparent': settings['transparent']
            }
            
            # Add DPI for raster formats
            if settings['dpi'] is not None:
                save_args['dpi'] = settings['dpi']
            
            plt.savefig(**save_args)
        else:
            print(f"Warning: Unsupported color bar format '{cb_format}'. Skipping.")
    
    plt.close()

def create_vienna_file(seq, structure, output_dir, filename, sequence_name):
    vienna_path = os.path.join(output_dir, filename)
    seq_rna = seq.replace('T', 'U').replace('t', 'u')
    with open(vienna_path, 'w') as f:
        f.write(f">{sequence_name}\n")
        f.write(f"{seq_rna}\n")
        f.write(f"{structure}\n")
    return vienna_path

def get_theme_config():
    theme = CONFIG.get('theme') or {}
    return {
        'details_level': theme.get('details_level'),
        'base_colors': theme.get('base_colors'),
        'base_label_color': theme.get('base_label_color'),
        'background_color': theme.get('background_color'),
        'custom_colors': theme.get('custom_colors'),
        'show': theme.get('show'),
        'hide': theme.get('hide'),
        'line': theme.get('line'),
    }

def create_rnartist_script(vienna_file, basepair_probs_file, output_dir, seq, plist, colormap_name=SELECTED_COLORMAP, sequence_name="sequence", coloring_mode=COLORING_MODE):
    output_dir = os.path.abspath(output_dir).replace('\\', '/')
    vienna_file = os.path.abspath(vienna_file).replace('\\', '/')
    theme_cfg = get_theme_config()
    details_level = theme_cfg['details_level']
    base_label_color = theme_cfg['base_label_color']
    custom_colors = theme_cfg['custom_colors']
    show_list = theme_cfg['show']
    hide_list = theme_cfg['hide']
    line_list = theme_cfg['line']
    # Get the matplotlib colormap with validation
    is_valid, description = validate_colormap(colormap_name, COLORMAPS_DATA)
    
    if not is_valid:
        print(f"Warning: Colormap '{colormap_name}' not found for RNArtist script. Using 'viridis' instead.")
        colormap_name = 'viridis'
        is_valid, description = validate_colormap(colormap_name, COLORMAPS_DATA)
    
    try:
        cmap = plt.get_cmap(colormap_name)
    except ValueError:
        print(f"Error: Failed to load colormap '{colormap_name}' for RNArtist script. Using 'viridis' instead.")
        cmap = plt.get_cmap('viridis')
    seq_len = 0
    structure = None
    with open(vienna_file, 'r') as f:
        for line in f:
            if not line.startswith('>') and not set(line.strip()).issubset({'.', '(', ')'}):
                seq_len = len(line.strip())
            elif set(line.strip()).issubset({'.', '(', ')'}):
                structure = line.strip()
    if structure is None:
        raise ValueError('Could not find structure string in Vienna file')
    paired_status = get_paired_status(structure)
    pi_values = compute_base_pairing_probabilities(seq, plist)
    # Use the same coloring logic as map_probabilities_to_colors
    base_colors = {}
    for i in range(1, seq_len+1):
        pi = pi_values[i-1]
        is_paired = paired_status[i-1] if i-1 < len(paired_status) else False
        if coloring_mode == 'paired_only':
            value = min(pi, 1.0) if is_paired else min(1.0 - pi, 1.0)
        elif coloring_mode == 'all_pi':
            value = min(pi, 1.0)
        else:
            value = min(pi, 1.0)
        color = cmap(value)
        # Use YAML base_colors if provided, else colormap
        base_colors_yaml = theme_cfg['base_colors'] if theme_cfg['base_colors'] is not None else {}
        base = seq[i-1] if i-1 < len(seq) else None
        if base and base in base_colors_yaml:
            hex_color = base_colors_yaml[base]
        else:
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(color[0] * 255), 
                int(color[1] * 255), 
                int(color[2] * 255)
            )
        base_colors[i] = hex_color
    script_content = f'''rnartist {{
  svg {{
    path = "{output_dir}/"
  }}
  png {{
    path = "{output_dir}/"
  }}
  ss {{
    vienna {{
      file = "{vienna_file}"
    }}
  }}
  data {{
'''
    for i in range(1, seq_len+1):
        pi = pi_values[i-1]
        is_paired = paired_status[i-1] if i-1 < len(paired_status) else False
        if coloring_mode == 'paired_only':
            value = pi if is_paired else 1.0 - pi
        elif coloring_mode == 'all_pi':
            value = pi
        else:
            value = pi
        script_content += f'    {float(i):.1f} to {value:.10f}\n'
    script_content += f'''  }}
  theme {{
    details {{
      value = {details_level if details_level is not None else 4}
    }}
'''
    # Add explicit color assignments for each base using location
    for i in range(1, seq_len+1):
        script_content += f'''    color {{
      location {{
        {i} to {i}
      }}
      value = "{base_colors[i]}"
    }}
'''
    # Add custom color assignments from YAML if present
    if custom_colors:
        for color_cfg in custom_colors:
            script_content += f'''    color {{
'''
            if 'type' in color_cfg:
                script_content += f'      type = "{color_cfg["type"]}"\n'
            if 'value' in color_cfg:
                val = color_cfg["value"]
                if isinstance(val, (int, float)):
                    script_content += f'      value = {float(val):.1f}\n'
                else:
                    script_content += f'      value = "{val}"\n'
            if 'to' in color_cfg:
                to_val = color_cfg["to"]
                if isinstance(to_val, (int, float)):
                    script_content += f'      to = {float(to_val):.1f}\n'
                else:
                    script_content += f'      to = "{to_val}"\n'
            if 'location' in color_cfg:
                locs = color_cfg['location']
                if isinstance(locs, list) and len(locs) == 2:
                    script_content += f'      location {{\n        {float(locs[0]):.1f} to {float(locs[1]):.1f}\n      }}\n'
            script_content += f'    }}\n'
    # Add show/hide elements from YAML if present
    if show_list:
        for show_cfg in show_list:
            script_content += f'    show {{\n'
            if 'type' in show_cfg:
                script_content += f'      type = "{show_cfg["type"]}"\n'
            if 'location' in show_cfg:
                locs = show_cfg['location']
                if isinstance(locs, list) and len(locs) == 2:
                    script_content += f'      location {{\n        {float(locs[0]):.1f} to {float(locs[1]):.1f}\n      }}\n'
            script_content += f'    }}\n'
    if hide_list:
        for hide_cfg in hide_list:
            script_content += f'    hide {{\n'
            if 'type' in hide_cfg:
                script_content += f'      type = "{hide_cfg["type"]}"\n'
            if 'location' in hide_cfg:
                locs = hide_cfg['location']
                if isinstance(locs, list) and len(locs) == 2:
                    script_content += f'      location {{\n        {float(locs[0]):.1f} to {float(locs[1]):.1f}\n      }}\n'
            script_content += f'    }}\n'
    # Add line elements from YAML if present
    if line_list:
        for line_cfg in line_list:
            script_content += f'    line {{\n'
            if 'type' in line_cfg:
                script_content += f'      type = "{line_cfg["type"]}"\n'
            if 'value' in line_cfg:
                val = line_cfg["value"]
                if isinstance(val, (int, float)):
                    script_content += f'      value = {float(val):.1f}\n'
                else:
                    script_content += f'      value = "{val}"\n'
            if 'location' in line_cfg:
                locs = line_cfg['location']
                if isinstance(locs, list) and len(locs) == 2:
                    script_content += f'      location {{\n        {float(locs[0]):.1f} to {float(locs[1]):.1f}\n      }}\n'
            script_content += f'    }}\n'
    # Add color for base letters (nucleotides) only if base_label_color is set in config.yaml, otherwise skip
    if base_label_color:
        script_content += f'''    color {{
      type = "n"
      value = "{base_label_color}"
    }}
'''
    script_content += f'''  }}
}}
'''
    script_path = os.path.join(output_dir, create_output_filename("rnartist_script", sequence_name, "kts"))
    with open(script_path, 'w') as f:
        f.write(script_content)
    return script_path

def run_rnartist_visualization(script_path, jar_path):
    try:
        cmd = f'java -jar "{jar_path}" "{script_path}"'
        print(f"Running RNArtistCore command: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Always print stdout/stderr for debugging
        if result.stdout:
            print(f"RNArtist Output:\n{result.stdout}")
        if result.stderr:
            print(f"RNArtist Errors/Warnings:\n{result.stderr}")
            
        if result.returncode == 0:
            print("RNArtistCore visualization completed successfully (process exited with 0).")
            print("Output files generated in the output directory.")
        else:
            print(f"RNArtistCore failed with return code {result.returncode}")
    except Exception as e:
        print(f"Error running RNArtistCore: {e}")
        import traceback
        traceback.print_exc()

def process_sequence(header, seq, jar_path, outputs_dir, errors, profile={}):
    sequence_name = get_sequence_name(header)
    out_dir = os.path.join(outputs_dir, sequence_name)
    os.makedirs(out_dir, exist_ok=True)
    try:
        structure, plist, stats = fold_sequence(seq, profile)
        mfe = stats['mfe']
        
        seq_rna = seq.replace('T', 'U').replace('t', 'u')
        with open(os.path.join(out_dir, create_output_filename("summary", sequence_name, "txt")), "w") as f:
            f.write(f"Sequence: {seq_rna}\n")
            f.write(f"Structure: {structure}\n")
            f.write(f"MFE: {mfe:.2f}\n")
            f.write(f"Ensemble Energy: {stats['ensemble_energy']:.2f}\n")
            f.write(f"Frequency of MFE structure in ensemble: {stats['frequency']*100:.2f} %\n")
            f.write(f"Ensemble Diversity: {stats['diversity']:.2f}\n")
            
        with open(os.path.join(out_dir, create_output_filename("basepair_probabilities", sequence_name, "txt")), "w") as f:
            for entry in plist:
                if entry.i == 0 and entry.j == 0:
                    break
                if entry.p > 0.00001:
                    f.write(f"P({entry.i},{entry.j}) = {entry.p:.10f}\n")
        structure_pairs = []
        stack = []
        for idx, char in enumerate(structure):
            if char == '(': stack.append(idx+1)
            elif char == ')':
                i = stack.pop()
                j = idx+1
                structure_pairs.append((i, j))
        pair_probs = {}
        for entry in plist:
            if entry.i == 0 and entry.j == 0:
                break
            pair_probs[(entry.i, entry.j)] = entry.p
            pair_probs[(entry.j, entry.i)] = entry.p
        with open(os.path.join(out_dir, create_output_filename("structure_basepair_probs", sequence_name, "txt")), "w") as f:
            f.write("i\tj\tP_ij\n")
            for i, j in structure_pairs:
                p = pair_probs.get((i, j), 0.0)
                f.write(f"{i}\t{j}\t{p:.10f}\n")
        pi_values = compute_base_pairing_probabilities(seq, plist)
        paired_status = get_paired_status(structure)
        
        # --- Visualization Settings from Profile ---
        vis_cfg = profile.get('visualization', {})
        # Fallback to config.yaml if not in profile, then default
        selected_colormap = vis_cfg.get('colormap', SELECTED_COLORMAP)
        coloring_mode = vis_cfg.get('coloring_mode', COLORING_MODE)
        
        colors = map_probabilities_to_colors(pi_values, paired_status, selected_colormap, coloring_mode)
        save_probability_results(seq, pi_values, colors, out_dir, selected_colormap, sequence_name)
        with open(os.path.join(out_dir, create_output_filename("structure", sequence_name, "vienna")), "w") as f:
            f.write(f">{sequence_name}\n")
            f.write(f"{seq_rna}\n")
            f.write(f"{structure}\n")
        vienna_file = create_vienna_file(seq, structure, out_dir, create_output_filename("structure", sequence_name, "vienna"), sequence_name)
        basepair_probs_file = os.path.join(out_dir, create_output_filename("structure_basepair_probs", sequence_name, "txt"))
        script_path = create_rnartist_script(vienna_file, basepair_probs_file, out_dir, seq, plist, selected_colormap, sequence_name, coloring_mode)
        run_rnartist_visualization(script_path, jar_path)
        return {
            'sequence_name': sequence_name,
            'out_dir': out_dir,
            'mfe': mfe,
            'length': len(seq),
            'vienna_file': vienna_file,
            'script_path': script_path
        }
    except Exception as e:
        errors.append((sequence_name, str(e)))
        return None

def process_sequence_wrapper(args):
    # Helper for ProcessPoolExecutor: unpack args and call process_sequence
    return process_sequence(*args)


def process_sequence_worker(args):
    """
    Worker function for ProcessPoolExecutor.
    args: (header, seq, jar_path, out_dir, profile)
    Returns: (result_dict, error_list)
    """
    header, seq, jar_path, out_dir, profile = args
    local_errors = []
    try:
        # Errors list is passed but local to the process. We return it.
        result = process_sequence(header, seq, jar_path, out_dir, local_errors, profile)
        return result, local_errors
    except Exception as e:
        return None, [(get_sequence_name(header), str(e))]

def check_java_available(log_callback=print):
    """Check if Java is available in the system path."""
    import shutil
    java_path = shutil.which('java')
    if java_path is None:
        log_callback("ERROR: Java is not installed or not found in your system PATH.")
        log_callback("Please install Java (version 8 or higher) and restart the app.")
        log_callback("Download: https://adoptium.net/ or https://www.java.com/")
        return False
    else:
        log_callback(f"Java found at: {java_path}")
        return True

# =============================================================================
# PROGRAMMATIC ENTRY POINT (For GUI Integration)
# =============================================================================
def run_engine_programmatic(input_path, profile_path=None, output_dir="outputs", callback=None):
    """
    Programmatic entry point for running the engine from Python code.
    
    Args:
        input_path (str): Path to input FASTA file or directory.
        profile_path (str): Path to JSON profile.
        output_dir (str): Root output directory.
        callback (func): Optional callback for logging (message: str).
    """
    def log(msg):
        if callback:
            callback(msg)
        else:
            print(msg)

    log("Debug: Engine started.")
    log("Debug: Checking for Java...")
    if not check_java_available(log):
        log("Debug: Java check FAILED.")
        return False
    log("Debug: Java check passed.")
    
    log("=" * 60)
    log("RNAfold to RNArtist Engine v5 (Profile Enabled)")
    log("=" * 60)
    
    # Load Profile
    log("Debug: Loading profile...")
    profile = load_profile(profile_path)
    if profile:
        log(f"Loaded Profile: {profile_path}")
    else:
        log("No profile loaded. Using default RNAfold settings (T=37, d=2, noLP=1).")

    # Correct JAR path resolution
    # In frozen exe, we look in sys._MEIPASS or current dir
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    # Check multiple locations for JAR
    possible_jars = [
        os.path.join(base_path, "bin", "RNArtistCore.jar"),
        os.path.join(base_path, "bin", "rnartistcore-0.4.6-SNAPSHOT-jar-with-dependencies.jar"),
        os.path.join(os.getcwd(), "bin", "RNArtistCore.jar"), # If running from dist/
    ]
    
    jar_path = None
    for p in possible_jars:
        if os.path.exists(p):
            jar_path = p
            break
            
    if not jar_path:
        log("Error: RNArtistCore.jar not found.")
        return False
        
    log(f"Using RNArtist JAR: {jar_path}")

    # Create Run Folder
    import datetime
    
    # Determine Output Structure from Config
    output_cfg = CONFIG.get('output', {})
    structure_mode = output_cfg.get('structure', 'nested_timestamp') # Default to nested
    
    if structure_mode == 'flat':
        # Simple mode: output/sequence_name (overwrites)
        run_output_dir = output_dir
    elif structure_mode == 'date_group':
        # Date grouped: output/YYYY-MM-DD/sequence_name
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        run_output_dir = os.path.join(output_dir, date_str)
    else: 
        # Default: output/run_TIMESTAMP/sequence_name
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_output_dir = os.path.join(output_dir, f"run_{timestamp}")

    os.makedirs(run_output_dir, exist_ok=True)
    
    all_results = []
    errors = []
    
    # Collect Input Files
    input_files = []
    if os.path.isdir(input_path):
        for ext in ("*.fasta", "*.fa", "*.txt"):
            input_files.extend(glob.glob(os.path.join(input_path, ext)))
        if not input_files:
            log(f"No FASTA files found in directory: {input_path}")
            return False
    else:
        input_files = [input_path]

    # Prepare Jobs
    jobs = []
    for fasta_file in input_files:
        log(f"Reading file: {os.path.basename(fasta_file)}")
        try:
            records = parse_multi_fasta(fasta_file)
            if not records:
                log(f"  No sequences found in {fasta_file}")
                continue
            for header, seq in records:
                seq_name = get_sequence_name(header)
                log(f"  Queued: {seq_name} ({len(seq)} bp)")
                jobs.append((header, seq, jar_path, run_output_dir, [], profile))
        except Exception as e:
            errors.append((os.path.basename(fasta_file), str(e)))

    if not jobs:
        log("No valid sequences to process.")
        return False

    # Determine workers
    # Check profile (from GUI) first
    max_workers = 10
    
    # Try profile first
    if profile:
         prof_perf = profile.get('performance', {})
         if isinstance(prof_perf, dict):
              val = prof_perf.get('max_workers')
              if val is not None:
                  max_workers = val
    else:
        # Fallback to config
        perf_cfg = CONFIG.get('performance', {})
        max_workers = perf_cfg.get('max_workers', 10)
    
    # If 0 or None, use auto-detect
    if not max_workers or max_workers <= 0:
        max_workers = os.cpu_count() or 4
        
    # Execute in Parallel (Multiprocessing)
    log(f"\nProcessing {len(jobs)} sequences using Multiprocessing (Workers: {max_workers})...")
    
    count = 0 
    
    # Ensure workers count is valid for ProcessPoolExecutor (must be > 0 or None)
    # If max_workers is None, it uses default.
    # We already set it to explicit count unless 0.
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Allow passing errors via wrapper? No, wrapper handles it.
        # Prepare arguments for worker (remove 'errors' list from tuple)
        # Job format: (header, seq, j_path, out_dir, errs, prof)
        # New format: (header, seq, j_path, out_dir, prof)
        worker_args = []
        for job in jobs:
            header, seq, j_path, out_dir, _, prof = job
            worker_args.append((header, seq, j_path, out_dir, prof))
            
        # Submit all jobs
        futures = {executor.submit(process_sequence_worker, args): args for args in worker_args}
        
        for future in concurrent.futures.as_completed(futures):
            count += 1
            # Retrieve original args if needed for debugging? No, result usually has info.
            # But if exception occurs in worker BEFORE process_sequence logic, we might not get sequence_name.
            # Actually process_sequence_worker catches top-level exception and returns name from header.
            
            try:
                result, errs = future.result()
                
                # We need sequence name for logging
                # If result is None, errs might have it.
                seq_name = "Unknown"
                if result:
                    seq_name = result['sequence_name']
                elif errs:
                    seq_name = errs[0][0] # (name, msg)
                
                if result:
                    all_results.append(result)
                    log(f"  [OK] {seq_name}")
                else:
                    log(f"  [FAIL] {seq_name}")
                
                if errs:
                    errors.extend(errs)
                    # For verbose errors in main log:
                    for name, msg in errs:
                         log(f"    Error ({name}): {msg}")

            except Exception as e:
                log(f"  [CRITICAL ERROR] A worker process failed: {e}")
                log(traceback.format_exc())
                errors.append(("Unknown", str(e)))

    # Summary
    log("-" * 40)
    log(f"Results saved in: {run_output_dir}")
    log(f"Successfully processed: {len(all_results)}")
    log(f"Errors: {len(errors)}")
    
    if errors:
        log("\nError Details:")
        for name, msg in errors:
            log(f"  {name}: {msg}")
            
    return True

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support() # Crucial for PyInstaller if we ever use ProcessPool
    
    parser = argparse.ArgumentParser(description="RNAfold Engine v5")
    parser.add_argument("input_path", help="Input file (FASTA) or directory")
    parser.add_argument("--profile", type=str, default=None, help="Path to JSON profile configuration")
    parser.add_argument("--workers", type=int, default=None, help="Ignored in v5.1 (Sequential)")
    parser.add_argument("--jar", type=str, default=None, help="Ignored in v5.1 (Auto-detected)")
    
    args = parser.parse_args()
    
    run_engine_programmatic(args.input_path, profile_path=args.profile)

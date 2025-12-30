import os
import sys
import subprocess
import RNA
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import yaml
import glob
from collections import defaultdict
import concurrent.futures
import shutil

# =============================
# YAML CONFIG LOADING
# =============================
def load_config(config_path='config.yaml'):
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
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
    """Load colormaps from external YAML file with validation."""
    try:
        with open(colormaps_file, 'r') as f:
            colormaps_data = yaml.safe_load(f)
        return colormaps_data
    except FileNotFoundError:
        print(f"Warning: Colormaps file '{colormaps_file}' not found. Using built-in defaults.")
        return None
    except yaml.YAMLError as e:
        print(f"Warning: Error parsing colormaps file: {e}. Using built-in defaults.")
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
        return "sequence"
    
    # Remove common problematic characters and take first word
    name = header.split()[0]  # Take first word
    name = name.replace('|', '_').replace(' ', '_').replace('\t', '_')
    name = ''.join(c for c in name if c.isalnum() or c in '_-')
    
    # Ensure name is not empty and starts with letter
    if not name or name[0].isdigit():
        name = "seq_" + name
    
    return name

def create_output_filename(base_name, sequence_name, extension):
    """Create output filename with sequence name prefix."""
    return f"{sequence_name}_{base_name}.{extension}"

def fold_sequence(seq):
    """
    Fold sequence using RNAlib with explicit model parameters.
    Sets dangles=2 and temperature=37.0 to match RNAfold web/CLI defaults.
    """
    # Create model details object
    md = RNA.md()
    
    # Set parameters to match RNAfold defaults
    md.dangles = 2      # Double dangling ends (automatic)
    md.temperature = 37.0  # Standard temperature
    md.noLP = 1         # Avoid isolated base pairs (as per user settings)
    
    # Create fold compound with model details
    fc = RNA.fold_compound(seq, md)
    
    # Compute MFE and Structure
    structure, mfe = fc.mfe()
    
    # Compute Partition Function
    fc.pf()
    
    # Get base pair probabilities
    plist = fc.plist_from_probs(0.0)
    
    return structure, mfe, plist

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
        cmap = plt.get_cmap(colormap_name)
    except ValueError:
        print(f"Error: Failed to load colormap '{colormap_name}'. Using 'viridis' instead.")
        cmap = plt.get_cmap('viridis')
    
    colors = []
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
    cb_formats = colorbar_cfg.get('format', 'svg')
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

def create_rnartist_script(vienna_file, basepair_probs_file, output_dir, seq, plist, colormap_name=SELECTED_COLORMAP, sequence_name="sequence"):
    output_dir = output_dir.replace('\\', '/').replace('\\', '/')
    vienna_file = os.path.abspath(vienna_file).replace('\\', '/').replace('\\', '/')
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
        if COLORING_MODE == 'paired_only':
            value = min(pi, 1.0) if is_paired else min(1.0 - pi, 1.0)
        elif COLORING_MODE == 'all_pi':
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
        if COLORING_MODE == 'paired_only':
            value = pi if is_paired else 1.0 - pi
        elif COLORING_MODE == 'all_pi':
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
        if result.returncode == 0:
            print("RNArtistCore visualization completed successfully!")
            print("Output files generated in the output directory.")
        else:
            print(f"RNArtistCore failed with error: {result.stderr}")
    except Exception as e:
        print(f"Error running RNArtistCore: {e}")

def process_sequence(header, seq, jar_path, outputs_dir, errors):
    sequence_name = get_sequence_name(header)
    out_dir = os.path.join(outputs_dir, sequence_name)
    os.makedirs(out_dir, exist_ok=True)
    try:
        structure, mfe, plist = fold_sequence(seq)
        seq_rna = seq.replace('T', 'U').replace('t', 'u')
        with open(os.path.join(out_dir, create_output_filename("summary", sequence_name, "txt")), "w") as f:
            f.write(f"Sequence: {seq_rna}\n")
            f.write(f"Structure: {structure}\n")
            f.write(f"MFE: {mfe}\n")
        with open(os.path.join(out_dir, create_output_filename("basepair_probabilities", sequence_name, "txt")), "w") as f:
            for entry in plist:
                if entry.i == 0 and entry.j == 0:
                    break
                if entry.p > 0.01:
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
        colors = map_probabilities_to_colors(pi_values, paired_status, SELECTED_COLORMAP, COLORING_MODE)
        save_probability_results(seq, pi_values, colors, out_dir, SELECTED_COLORMAP, sequence_name)
        with open(os.path.join(out_dir, create_output_filename("structure", sequence_name, "vienna")), "w") as f:
            f.write(f">{sequence_name}\n")
            f.write(f"{seq_rna}\n")
            f.write(f"{structure}\n")
        vienna_file = create_vienna_file(seq, structure, out_dir, create_output_filename("structure", sequence_name, "vienna"), sequence_name)
        basepair_probs_file = os.path.join(out_dir, create_output_filename("structure_basepair_probs", sequence_name, "txt"))
        script_path = create_rnartist_script(vienna_file, basepair_probs_file, out_dir, seq, plist, SELECTED_COLORMAP, sequence_name)
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

def check_java_available():
    """Check if Java is available in the system path."""
    java_path = shutil.which('java')
    if java_path is None:
        print("ERROR: Java is not installed or not found in your system PATH.")
        print("Please install Java (version 8 or higher) and ensure 'java' is available in your PATH.")
        print("Download: https://adoptium.net/ or https://www.java.com/")
        sys.exit(1)
    else:
        print(f"Java found at: {java_path}")

def main(input_path, jar_path="rnartistcore-0.4.6-SNAPSHOT-jar-with-dependencies.jar", max_workers=None):
    check_java_available()
    print("=" * 60)
    print("RNAfold to RNArtist Pipeline v4 (Default parameters fix)")
    print("=" * 60)
    outputs_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    all_results = []
    errors = []
    input_files = []
    if os.path.isdir(input_path):
        for ext in ("*.fasta", "*.fa", "*.txt"):
            input_files.extend(glob.glob(os.path.join(input_path, ext)))
        if not input_files:
            print(f"No FASTA files found in directory: {input_path}")
            sys.exit(1)
    else:
        input_files = [input_path]
    # Prepare all sequence jobs
    jobs = []
    for fasta_file in input_files:
        print(f"\nProcessing file: {fasta_file}")
        try:
            records = parse_multi_fasta(fasta_file)
            if not records:
                print(f"  No sequences found in {fasta_file}")
                continue
            for header, seq in records:
                print(f"  Queued sequence: {get_sequence_name(header)} (length {len(seq)})")
                jobs.append((header, seq, jar_path, outputs_dir, []))
        except Exception as e:
            errors.append((os.path.basename(fasta_file), str(e)))
    # Parallel processing
    if max_workers is None:
        max_workers = os.cpu_count() or 2
    print(f"\nRunning parallel processing with {max_workers} workers...")
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_sequence_wrapper, job) for job in jobs]
        for future, job in zip(concurrent.futures.as_completed(futures), jobs):
            try:
                result = future.result()
                if result:
                    all_results.append(result)
            except Exception as e:
                sequence_name = get_sequence_name(job[0])
                errors.append((sequence_name, str(e)))
    # Write master summary
    summary_path = os.path.join(outputs_dir, "master_summary.txt")
    with open(summary_path, "w") as f:
        f.write("Sequence\tLength\tMFE\tOutputDir\n")
        for r in all_results:
            f.write(f"{r['sequence_name']}\t{r['length']}\t{r['mfe']}\t{r['out_dir']}\n")
    # Write error log
    if errors:
        error_path = os.path.join(outputs_dir, "error_log.txt")
        with open(error_path, "w") as f:
            for name, msg in errors:
                f.write(f"{name}: {msg}\n")
        print(f"\nSome errors occurred. See {error_path}")
    print(f"\nAll results saved in: {outputs_dir}")
    print(f"Master summary: {summary_path}")
    if errors:
        print(f"Error log: {error_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python RNAfold_to_RNArtis_v4.py <input_file_or_folder> [max_workers]")
        print("       Input can be a multi-FASTA file or a folder with FASTA files")
        print("       Example: python RNAfold_to_RNArtis_v4.py input.fasta")
        print("                python RNAfold_to_RNArtis_v4.py input_folder/")
        print("                python RNAfold_to_RNArtis_v4.py input.fasta 4")
        sys.exit(1)
    input_path = sys.argv[1]
    max_workers = int(sys.argv[2]) if len(sys.argv) == 3 else None
    main(input_path, max_workers=max_workers)

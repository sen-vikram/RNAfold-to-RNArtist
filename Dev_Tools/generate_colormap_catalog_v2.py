#!/usr/bin/env python3
"""
Simple Colormap Catalog Generator for RNA Analysis Pipeline
Based on matplotlib's clean approach for displaying colormaps.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import yaml
import os

def load_colormaps(colormaps_file='colormaps.yaml'):
    """Load colormaps from external YAML file."""
    try:
        with open(colormaps_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Colormaps file '{colormaps_file}' not found.")
        return None

def get_scientific_favorites():
    """Define colormaps most commonly used in scientific publications."""
    return ['viridis', 'plasma', 'inferno', 'cividis', 'coolwarm', 'RdBu_r', 'Spectral_r', 'seismic']

def filter_non_reverse_colormaps(colormap_dict):
    """Filter out reverse colormaps (those ending with _r) to avoid duplication."""
    filtered = {}
    for name, description in colormap_dict.items():
        if not name.endswith('_r'):
            filtered[name] = description
    return filtered

def plot_color_gradients(category, cmap_list):
    """Plot colormaps in a clean, vertical layout based on matplotlib example."""
    if not cmap_list:
        return None
    
    # Create gradient
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    
    # Create figure and adjust figure height to number of colormaps
    nrows = len(cmap_list)
    figh = 0.35 + 0.15 + (nrows + (nrows - 1) * 0.1) * 0.22
    fig, axs = plt.subplots(nrows=nrows, figsize=(6.4, figh))
    fig.subplots_adjust(top=1 - 0.35 / figh, bottom=0.15 / figh,
                        left=0.2, right=0.99)
    
    # Add category title
    axs[0].set_title(f'{category} colormaps', fontsize=14)
    
    # Plot each colormap
    for ax, name in zip(axs[1:], cmap_list):
        try:
            ax.imshow(gradient, aspect='auto', cmap=mpl.colormaps[name])
            ax.text(-0.01, 0.5, name, va='center', ha='right', fontsize=10,
                    transform=ax.transAxes)
        except Exception as e:
            # If colormap not found, show error
            ax.text(0.5, 0.5, f'{name}\n(not found)', va='center', ha='center', 
                    fontsize=10, transform=ax.transAxes, color='red')
    
    # Turn off *all* ticks & spines, not just the ones with colormaps.
    for ax in axs:
        ax.set_axis_off()
    
    return fig

def create_output_folder():
    """Create output folder for catalogs."""
    folder_name = 'colormap_catalogs'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def generate_scientific_favorites_catalog(output_folder):
    """Generate catalog of scientific favorites."""
    print("Generating Scientific Favorites Catalog...")
    
    cmap_list = get_scientific_favorites()
    fig = plot_color_gradients('Scientific Favorites', cmap_list)
    
    if fig:
        output_file = os.path.join(output_folder, 'scientific_favorites.png')
        fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Scientific favorites catalog saved as: {output_file}")
        plt.close()
        return output_file
    
    return None

def generate_category_catalogs(output_folder):
    """Generate catalogs for each category."""
    print("Generating Category Catalogs...")
    
    # Load colormaps
    colormaps_data = load_colormaps()
    if not colormaps_data:
        print("Error: Could not load colormaps.yaml")
        return []
    
    catalogs = []
    
    # Generate catalog for each category (now dynamic)
    for category_name, category_desc in colormaps_data.get('categories', {}).items():
        if category_name in ['default', 'categories']:
            continue
        colormaps = colormaps_data.get(category_name, {})
        if colormaps:
            print(f"Generating {category_name} catalog...")
            # Filter out reverse colormaps to avoid duplication
            filtered_colormaps = filter_non_reverse_colormaps(colormaps)
            cmap_list = list(filtered_colormaps.keys())
            fig = plot_color_gradients(category_name, cmap_list)
            if fig:
                output_file = os.path.join(output_folder, f'{category_name}.png')
                fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
                print(f"{category_name} catalog saved as: {output_file}")
                catalogs.append((category_name, output_file))
                plt.close()
    # Add legacy_and_specialized if present
    if 'legacy_and_specialized' in colormaps_data:
        print("Generating legacy_and_specialized catalog...")
        colormaps = colormaps_data['legacy_and_specialized']
        filtered_colormaps = filter_non_reverse_colormaps(colormaps)
        cmap_list = list(filtered_colormaps.keys())
        fig = plot_color_gradients('legacy_and_specialized', cmap_list)
        if fig:
            output_file = os.path.join(output_folder, 'legacy_and_specialized.png')
            fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"legacy_and_specialized catalog saved as: {output_file}")
            catalogs.append(('legacy_and_specialized', output_file))
            plt.close()
    return catalogs

if __name__ == "__main__":
    print("Simple Colormap Catalog Generator")
    print("=" * 40)
    
    # Create output folder
    output_folder = create_output_folder()
    
    # Generate scientific favorites catalog
    print("\n1. Generating scientific favorites catalog...")
    favorites_catalog = generate_scientific_favorites_catalog(output_folder)
    
    # Generate category catalogs
    print("\n2. Generating category catalogs...")
    category_catalogs = generate_category_catalogs(output_folder)
    
    print("\nCatalog generation complete!")
    print(f"All catalogs saved in: {output_folder}/")
    
    if favorites_catalog:
        print(f"  - scientific_favorites.png")
    
    print("\nCategory catalogs:")
    for category_name, output_file in category_catalogs:
        print(f"  - {category_name}.png") 
    
    # --- Colormap comparison section ---
    import matplotlib
    import yaml
    import os
    # List all available matplotlib colormaps
    mpl_colormaps = set(matplotlib.colormaps)
    print(f"Total matplotlib colormaps: {len(mpl_colormaps)}")
    # Load colormaps from YAML
    yaml_path = "colormaps.yaml"
    if os.path.exists(yaml_path):
        with open(yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        yaml_colormaps = set()
        # Extract colormap names from all present categories
        for cat in yaml_data:
            group = yaml_data.get(cat, {})
            if isinstance(group, dict):
                yaml_colormaps.update(group.keys())
            elif isinstance(group, list):
                yaml_colormaps.update(group)
        print(f"Total colormaps in YAML: {len(yaml_colormaps)}")
        # Compare
        missing_in_yaml = mpl_colormaps - yaml_colormaps
        missing_in_mpl = yaml_colormaps - mpl_colormaps
        print("\nColormaps in matplotlib but NOT in YAML:")
        print(sorted(missing_in_yaml))
        print(f"Count: {len(missing_in_yaml)}")
        print("\nColormaps in YAML but NOT in matplotlib:")
        print(sorted(missing_in_mpl))
        print(f"Count: {len(missing_in_mpl)}")
    else:
        print("colormaps.yaml not found. Skipping YAML comparison.") 
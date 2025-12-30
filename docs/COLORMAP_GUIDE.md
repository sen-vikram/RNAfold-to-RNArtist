# Colormap Guide for RNA Analysis Pipeline

## Overview

This guide explains how to use the comprehensive colormap system in the RNAfold to RNArtist pipeline, including visual catalogs and reverse colormaps for light-to-dark vs dark-to-light transitions.

## Visual Colormap Catalogs

The pipeline includes visual catalogs of all available colormaps, organized for easy selection:

### 1. Scientific Favorites Catalog

**Note:** Add `_r` suffix to any colormap name to get the reverse version (e.g., `viridis` → `viridis_r`).

![Scientific Favorites](colormap_catalogs/scientific_favorites.png)

**Most commonly used colormaps in scientific publications:**
- `viridis` - Perceptually uniform, colorblind-friendly
- `plasma` - High contrast, great for presentations
- `inferno` - Dramatic, emphasizes high values
- `cividis` - Colorblind-friendly, print-friendly
- `coolwarm` - Excellent for diverging data
- `RdBu_r` - Standard red-blue diverging
- `Spectral_r` - Rainbow-like for multiple levels
- `seismic` - High contrast for structural differences

### 2. Category-Specific Catalogs

#### Sequential Colormaps

**Note:** Add `_r` suffix to any colormap name to get the reverse version.

![Sequential Colormaps](colormap_catalogs/sequential.png)

Single-hue progressions, ideal for probability data and continuous measurements.

#### Diverging Colormaps

**Note:** Add `_r` suffix to any colormap name to get the reverse version.

![Diverging Colormaps](colormap_catalogs/diverging.png)

Two-hue progressions, ideal for data with a meaningful center point.

#### Qualitative Colormaps

**Note:** Add `_r` suffix to any colormap name to get the reverse version.

![Qualitative Colormaps](colormap_catalogs/qualitative.png)

Distinct colors for categorical data.

#### Cyclic Colormaps

**Note:** Add `_r` suffix to any colormap name to get the reverse version.

![Cyclic Colormaps](colormap_catalogs/cyclic.png)

Circular color schemes for periodic data.

#### RNA Analysis Colormaps

**Note:** Add `_r` suffix to any colormap name to get the reverse version.

![RNA Analysis Colormaps](colormap_catalogs/rna_analysis.png)

Curated colormaps specifically selected for RNA structure analysis.

#### Legacy and Specialized Colormaps

**Note:** Add `_r` suffix to any colormap name to get the reverse version.

![Legacy and Specialized Colormaps](colormap_catalogs/legacy_and_specialized.png)

Legacy, technical, and less commonly used colormaps, included for completeness and compatibility. This section contains all remaining base and reverse colormaps from matplotlib not present in the main categories.

## Colormap Categories

- **Sequential**: Single-hue progressions, ideal for probability data and continuous measurements
- **Diverging**: Two-hue progressions, ideal for data with a meaningful center point
- **Qualitative**: Distinct colors for categorical data
- **Cyclic**: Circular color schemes for periodic data
- **RNA Analysis**: Curated selection specifically for RNA structure visualization
- **Legacy and Specialized**: Legacy, technical, and less commonly used colormaps, including all base and reverse variants for completeness. Use for advanced, compatibility, or legacy visualization needs.

## Complete Coverage

- The YAML now includes **all 90 base colormaps** from matplotlib, plus their `_r` reverse variants, for a total of 180 colormaps.
- The `legacy_and_specialized` section contains colormaps that are legacy, technical, or less commonly used, but are available for advanced or compatibility needs.
- All colormaps are organized by category for easy selection in the pipeline.

## How to Use

- Select colormaps by name from any category in your config or scripts.
- Reverse variants are available by appending `_r` to the base name.
- For scientific and publication-ready work, prefer colormaps from the **Sequential**, **Diverging**, and **RNA Analysis** categories.
- Use **Legacy and Specialized** colormaps for compatibility, legacy data, or special visualization needs.

## Reverse Colormap Naming Convention

Reverse colormaps are denoted with the `_r` suffix:

| Colormap | Direction | Description |
|----------|-----------|-------------|
| `viridis` | Dark → Light | Standard perceptually uniform |
| `viridis_r` | Light → Dark | Reversed perceptually uniform |
| `Blues` | Light → Dark | Standard blue progression |
| `Blues_r` | Dark → Light | Reversed blue progression |
| `coolwarm` | Blue → Red | Standard diverging |
| `coolwarm_r` | Red → Blue | Reversed diverging |

## Usage in Configuration

### 1. Basic Usage
Edit your `config.yaml` file:

```yaml
colormap:
  name: viridis_r    # Light to dark progression
  reverse: false     # Not needed when using _r suffix
```

### 2. Common RNA Analysis Scenarios

#### For Base-Pairing Probabilities (Sequential)
```yaml
# High probability = bright colors
colormap:
  name: viridis      # Dark (low prob) to bright (high prob)

# High probability = dark colors  
colormap:
  name: viridis_r    # Bright (low prob) to dark (high prob)
```

#### For Base-Pairing Strength (Diverging)
```yaml
# Weak = blue, Strong = red
colormap:
  name: coolwarm     # Blue (weak) to red (strong)

# Weak = red, Strong = blue
colormap:
  name: coolwarm_r   # Red (weak) to blue (strong)
```

#### For Structure Elements
```yaml
# Paired regions = bright
colormap:
  name: Blues        # Light (unpaired) to dark (paired)

# Paired regions = dark
colormap:
  name: Blues_r      # Dark (unpaired) to light (paired)
```

## Recommended Colormaps for RNA Analysis

### Probability Data (Base-Pairing Probabilities)
- **`viridis`** - Best overall, perceptually uniform, colorblind-friendly
- **`viridis_r`** - Same as viridis but reversed
- **`plasma`** - High contrast, great for presentations
- **`plasma_r`** - High contrast, reversed
- **`inferno`** - Dramatic, emphasizes high values
- **`inferno_r`** - Dramatic, reversed

### Base-Pairing Strength (Diverging)
- **`coolwarm`** - Excellent for base-pairing strength
- **`RdBu_r`** - Standard red-blue diverging
- **`seismic`** - High contrast for structural differences
- **`Spectral_r`** - Rainbow-like for multiple levels

### Structure Elements
- **`Blues`** - Good for paired regions
- **`Blues_r`** - Reversed for paired regions
- **`Greens`** - Good for unpaired regions
- **`Greens_r`** - Reversed for unpaired regions

## Color Bar Output

The pipeline generates color bars in multiple formats:
- **SVG** - Vector format, transparent background
- **PDF** - Publication format, transparent background
- **PNG** - Raster format, white background
- **EPS** - Legacy format, transparent background

Configure in `config.yaml`:
```yaml
colorbar:
  format: [svg, pdf, png, eps]  # Generate all formats
  orientation: vertical          # or horizontal
```

## Quick Selection Guide

### 1. Choose Your Data Type
- **Probability data**: Use sequential colormaps (viridis, plasma, inferno)
- **Data with center point**: Use diverging colormaps (coolwarm, RdBu_r)
- **Categorical data**: Use qualitative colormaps (tab10, Set1)

### 2. Consider Your Audience
- **Colorblind users**: Use viridis, cividis, plasma
- **Printing**: Use cividis (grayscale friendly)
- **Presentations**: Use plasma, inferno (high contrast)

### 3. Choose Direction
- **High values = important**: Use standard progression
- **Low values = important**: Use reverse progression (`_r`)

### 4. Configure in Your Pipeline
```yaml
# In config.yaml
colormap:
  name: viridis_r    # Your chosen colormap
```

## Tips for Choosing Colormaps

### 1. Consider Your Data
- **Sequential data** (probabilities): Use sequential colormaps
- **Data with center point** (strength): Use diverging colormaps
- **Categorical data**: Use qualitative colormaps

### 2. Consider Your Audience
- **Colorblind users**: Use `viridis`, `cividis`, `plasma`
- **Printing**: Use `cividis` (grayscale friendly)
- **Presentations**: Use `plasma`, `inferno` (high contrast)

### 3. Consider Your Interpretation
- **High values = important**: Use standard progression
- **Low values = important**: Use reverse progression (`_r`)
- **Neutral center**: Use diverging colormaps

### 4. Consider Your Publication
- **Journal requirements**: Some journals prefer specific colormaps
- **Figure clarity**: Choose high contrast for small figures
- **Consistency**: Use same colormap across related figures

## Troubleshooting

### Colormap Not Found
If you get a warning about a colormap not being found:
1. Check the spelling in `config.yaml`
2. Verify the colormap exists in `colormaps.yaml`
3. The script will automatically fall back to `viridis`

### Color Bar Issues
- **SVG not transparent**: Check that `facecolor: 'none'` is set
- **PNG too large**: Adjust DPI settings in the script
- **Wrong orientation**: Change `orientation` in colorbar config

## Available Colormaps

The pipeline includes **180+ colormaps** organized by category:

- **Sequential**: ~56 colormaps (including reverse versions)
- **Diverging**: ~20 colormaps (including reverse versions)
- **Qualitative**: ~15 colormaps (including reverse versions)
- **Cyclic**: ~3 colormaps
- **Legacy and Specialized**: ~60 colormaps (including all remaining base and reverse variants)
- **RNA Analysis**: ~30 curated colormaps

For a complete visual reference, see the catalog images above or examine `colormaps.yaml` directly.

## Examples

### Example 1: Probability Visualization
```yaml
colormap:
  name: viridis_r    # Light (low prob) to dark (high prob)
coloring_mode:
  mode: all_pi       # Color all bases by probability
```

### Example 2: Structure Strength
```yaml
colormap:
  name: coolwarm     # Blue (weak) to red (strong)
coloring_mode:
  mode: paired_only  # Different coloring for paired/unpaired
```

### Example 3: Publication Ready
```yaml
colormap:
  name: cividis      # Colorblind-friendly, print-friendly
colorbar:
  format: [pdf, svg] # Vector formats for publication
```

## Generating New Catalogs

To regenerate the catalogs with updated colormaps:

```bash
python generate_colormap_catalog_v2.py
```

This will create all catalog images in the `colormap_catalogs/` folder.

## Support

If you need help choosing a colormap:
1. Check the scientific favorites catalog first
2. Look at the category-specific catalogs
3. Use the quick selection guide above
4. Refer to the detailed examples in this guide 
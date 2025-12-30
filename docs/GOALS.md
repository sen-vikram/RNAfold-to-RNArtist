# RNAfold to RNArtist Pipeline - Goals and Progress

## Current Version: v1 (Fixed Explicit Color Mapping)

### ✅ **COMPLETED ACHIEVEMENTS**

#### **Core Pipeline Functionality**

- ✅ **RNA/DNA Sequence Processing**: Reads FASTA files and converts DNA (T) to RNA (U) format
- ✅ **ViennaRNA Integration**: Uses ViennaRNA Python API for MFE structure prediction and partition function calculation
- ✅ **Base-Pair Probability Computation**: Calculates P(i,j) for all significant base pairs and per-base probabilities
- ✅ **Multiple Output Formats**: Generates comprehensive analysis files (summary, Vienna format, probability files, color bar)

#### **Color Mapping System (v1)**

- ✅ **Default Colormap**: Changed from 'RdYlBu_r' to 'Spectral_r' for better rainbow-like visualization
- ✅ **Matplotlib Integration**: Uses full matplotlib colormap for accurate color representation
- ✅ **Explicit Color Assignment**: Each base gets its exact color from the full matplotlib colormap
- ✅ **Perfect Color Consistency**: Color bar and RNArtist visualization use identical color mapping
- ✅ **Pi-Based Coloring**: Uses Pi values (sum of base-pairing probabilities) for consistent coloring
- ✅ **Location-Based Assignment**: Uses `location { i to i }` syntax for precise base coloring
- ✅ **Visible Base Letters**: Base letters (A, U, G, C) are colored black for clear visibility

#### **File Outputs**

- ✅ **Summary File**: Sequence, structure, and MFE information
- ✅ **Vienna Format**: Standard Vienna format for structure representation
- ✅ **Base-Pair Probabilities**: All significant P(i,j) values (>0.01)
- ✅ **Structure Base-Pairs**: MFE structure base pairs with their probabilities
- ✅ **Per-Base Probabilities**: Pi values for each nucleotide with RGB colors
- ✅ **Color Bar Image**: Matplotlib-generated color bar matching RNArtist output
- ✅ **RNArtist Script**: Kotlin script for structure visualization
- ✅ **SVG/PNG Outputs**: High-quality structure visualizations

#### **Technical Improvements**

- ✅ **Error Handling**: Robust error handling for missing colormaps and file operations
- ✅ **Cross-Platform Compatibility**: Proper path handling for Windows/Linux
- ✅ **Modular Design**: Clean, maintainable code structure
- ✅ **Documentation**: Comprehensive inline comments and usage instructions

### 🎯 **CURRENT STATUS**

#### **Working Features**

1. **Complete Pipeline**: From FASTA input to colored structure visualization
2. **Accurate Color Mapping**: Spectral_r colormap with full gradient support
3. **ViennaRNA Compatibility**: Matches ViennaRNA's coloring logic and output format
4. **Publication Ready**: High-quality outputs suitable for scientific publications

#### **Tested and Verified**

- ✅ Color bar generation matches RNArtist output
- ✅ RNArtist script syntax is correct and functional
- ✅ All output files are generated successfully
- ✅ Cross-platform path handling works correctly
- ✅ Error handling for edge cases

### 📋 **USAGE INSTRUCTIONS**

```bash
python RNAfold_to_RNArtis_v1.py <fasta_file>
```

**Example:**

```bash
python RNAfold_to_RNArtis_v1.py test_sequence.fasta
```

### 📁 **OUTPUT STRUCTURE**

```
output_folder/
├── summary.txt                           # Basic sequence and structure info
├── structure.vienna                      # Vienna format structure file
├── basepair_probabilities.txt            # All significant P(i,j) values
├── structure_basepair_probs.txt          # MFE structure base pairs
├── base_pairing_probabilities_per_base.txt # Per-base Pi values with colors
├── base_pairing_probability_colorbar_Spectral_r.png # Color bar image
├── rnartist_script.kts                   # RNArtist visualization script
├── structure.png                         # Final colored structure (PNG)
└── structure.svg                         # Final colored structure (SVG)
```

### 🎨 **COLORMAP OPTIONS**

**Current Default**: `Spectral_r` (Rainbow-like, shows multiple levels clearly)

**Available Options**:

- `viridis`: Perceptually uniform, colorblind-friendly
- `plasma`: High contrast, great for highlighting differences
- `inferno`: Dramatic, good for presentations
- `magma`: Smooth transitions, professional appearance
- `cividis`: Colorblind-friendly, good for grayscale printing
- `RdBu_r`: Red-Blue, good contrast
- `coolwarm`: Blue-Red, smooth transitions
- `seismic`: Blue-Red, high contrast
- `bwr`: Blue-White-Red, classic choice
- `PiYG`: Pink-Green, alternative to red-blue
- `PRGn`: Purple-Green, modern alternative
- `RdYlBu_r`: Red-Yellow-Blue, good for base-pairing strength

### 🔧 **TECHNICAL DETAILS**

#### **Color Mapping Logic**

- **Paired Bases**: Colored by their base-pairing probability P(i,j)
- **Unpaired Bases**: Colored by their unpaired probability 1-sum_j P(i,j)
- **Gradient**: Full matplotlib colormap gradient from 0.0 to 1.0
- **Consistency**: Identical color mapping between color bar and RNArtist output

#### **RNArtist Script Features**

- Uses `type = "N"` for nucleotide coloring
- Uses `data between 0.0..1.0` for probability range
- Supports both SVG and PNG output formats
- Configurable detail level (currently set to 4)

### 🚀 **FUTURE ENHANCEMENTS & CUSTOMIZATION OPTIONS**

#### **📊 Input & Processing Enhancements**

1. **Batch Processing**: Process multiple FASTA files simultaneously with progress tracking
2. **Directory Processing**: Process all FASTA files in a directory recursively
3. **Custom Sequence Input**: Support for direct sequence input (not just FASTA files)
4. **Multiple Sequence Formats**: Support for GenBank, EMBL, and other sequence formats
5. **Sequence Validation**: Validate input sequences and provide warnings for unusual characters
6. **Memory Optimization**: Efficient processing for very long sequences (>1000 nt)
7. **Parallel Processing**: Multi-threading for batch operations

#### **🎨 Visualization & Color Customization**

8. **Custom Colormap Selection**: Command-line option to choose colormap (`--colormap`)
9. **Custom Color Range**: Set custom min/max values for color scaling (`--min-value`, `--max-value`)
10. **Multiple Colormap Options**: Add more colormaps (Reds, Blues, Greens, etc.)
11. **Colorblind-Friendly Options**: Automatic colormap selection for accessibility
12. **Custom Base Colors**: Override default black color for base letters
13. **Background Color Options**: Customize structure background color
14. **Line Color Customization**: Customize helix and junction line colors
15. **Gradient Direction**: Option to reverse colormap direction
16. **Discrete Color Levels**: Option to use discrete color levels instead of continuous gradient

#### **📐 RNArtist Layout & Style Customization**

1. **Detail Level Selection**
   - Allow users to select the rendering detail level (1–5) via command-line or config, affecting how much structural detail is shown (from minimal to maximal: helix, junction, single strand, residue, interaction symbol, etc.).

2. **Custom Layout Algorithms**
   - Support for different layout algorithms for structure positioning (e.g., circular, radial, force-directed, or user-defined).
   - Allow users to override default junction layouts (e.g., set compass directions for helices leaving a junction).

3. **Output Size Control**
   - Allow customization of PNG/SVG output dimensions (e.g., `--width`, `--height`).

4. **Font Size Control**
   - Allow users to set the font size for base letters and labels.

5. **Line Width Control**
   - Allow customization of line thickness for helices, junctions, and other elements.

6. **Junction Style Options**
   - Provide options for different visual styles for junctions (e.g., circle, polygon, custom shapes).
   - Allow per-junction customization (e.g., color, size, rendering style).

7. **Helix Style Options**
   - Provide options for different helix visualizations (e.g., straight, curved, shaded, with/without axis).
   - Allow per-helix customization (e.g., color, thickness, rendering style).

8. **Custom Themes**
   - Support pre-defined and user-defined theme packages (e.g., “publication”, “presentation”, “dark mode”, etc.).
   - Allow easy switching between themes.

9. **Transparency Options**
   - Allow users to set transparency (alpha) for structure elements (bases, lines, backgrounds, etc.).

10. **Show/Hide/Highlight Specific Elements**
    - Allow users to show/hide or highlight specific types of elements (e.g., only show helices, hide single strands, highlight specific residues or regions).
    - Support for `show` and `hide` DSL elements with type/location/data selectors.

11. **Custom Color Gradients and Schemes**
    - Allow users to define custom color gradients for quantitative data (e.g., reactivity, probability).
    - Support for built-in color schemes (e.g., “Pumpkin Vegas”, “Celeste Olivine”, etc.) and user-defined schemes.

12. **Per-Element Location-Based Customization**
    - Allow color, line, and style customization for specific locations or ranges (e.g., `location { 5 to 20 }`).

13. **Interactive/Scriptable Layout Adjustments**
    - Allow users to specify layout overrides for specific junctions or regions (e.g., set out_ids for a particular 3-way junction).

14. **Export/Import of Custom Layouts and Themes**
    - Allow saving and loading of custom layout/theme configurations for reuse.

15. **Support for Advanced Layout Features**
    - Allow users to specify layout for multi-way junctions, pseudoknots, or non-canonical elements.

#### **📈 Analysis & Statistics Enhancements**

26. **Statistical Analysis**: Comprehensive probability statistics and summaries
27. **Base-Pair Strength Analysis**: Identify strong vs weak base pairs
28. **Structural Motif Detection**: Identify common RNA structural motifs
29. **Conservation Analysis**: Compare structures across multiple sequences
30. **Energy Landscape Analysis**: Additional energy calculations and visualizations
31. **Base-Pair Distance Analysis**: Analyze spatial relationships between base pairs
32. **Accessibility Analysis**: Calculate base accessibility metrics
33. **Thermodynamic Analysis**: Detailed thermodynamic parameter calculations

#### **💾 Output & File Management**

34. **Output Format Options**: Additional formats (PDF, EPS, TIFF, etc.)
35. **Compressed Output**: Option to compress output files
36. **Custom File Naming**: Flexible output file naming conventions
37. **Output Directory Structure**: Organized output with subdirectories
38. **Report Generation**: Generate comprehensive HTML/PDF reports
39. **Data Export Options**: Export data in various formats (CSV, JSON, XML)
40. **Metadata Files**: Include analysis metadata and parameters
41. **Version Control**: Track analysis versions and parameters

#### **🔧 Advanced Configuration**

42. **Configuration Files**: YAML/JSON configuration files for custom settings
43. **Command-Line Interface**: Full CLI with argument parsing and help
44. **Environment Variables**: Support for environment variable configuration
45. **Plugin System**: Extensible plugin architecture for custom analyses
46. **API Mode**: Run as a library/API for integration with other tools
47. **Docker Support**: Containerized version for reproducible environments
48. **Logging System**: Comprehensive logging with different verbosity levels

#### **🌐 User Interface & Accessibility**

49. **Web Interface**: Simple web-based interface for non-technical users
50. **GUI Application**: Desktop GUI application with drag-and-drop
51. **Jupyter Integration**: Jupyter notebook integration and widgets
52. **Progress Indicators**: Real-time progress bars and status updates
53. **Error Handling**: Comprehensive error messages and recovery options
54. **Help System**: Built-in help and documentation
55. **Tutorial Mode**: Interactive tutorial for new users
56. **Accessibility Features**: Screen reader support and keyboard navigation

#### **🔬 Scientific & Research Features**

57. **Comparative Analysis**: Compare multiple structures side-by-side
58. **Mutation Analysis**: Analyze impact of sequence mutations on structure
59. **Evolutionary Analysis**: Track structural changes across evolution
60. **Functional Annotation**: Integrate with functional annotation databases
61. **Literature Integration**: Link to relevant scientific literature
62. **Citation Generation**: Generate proper citations for publications
63. **Reproducibility**: Ensure reproducible results with seed setting
64. **Validation Tools**: Validate results against known structures

#### **📱 Integration & Compatibility**

65. **BioPython Integration**: Seamless integration with BioPython ecosystem
66. **Galaxy Integration**: Galaxy tool integration for workflow systems
67. **Conda/Pip Support**: Easy installation via package managers
68. **Cloud Deployment**: Support for cloud-based processing
69. **Database Integration**: Connect to RNA structure databases
70. **API Integrations**: Connect to external RNA analysis services
71. **Workflow Integration**: Integration with bioinformatics workflows
72. **Version Compatibility**: Support for different ViennaRNA versions

#### **🎯 Performance & Optimization**

73. **Caching System**: Cache intermediate results for faster re-analysis
74. **Memory Management**: Optimize memory usage for large datasets
75. **Speed Optimization**: Profile and optimize slow operations
76. **GPU Acceleration**: GPU support for large-scale computations
77. **Distributed Processing**: Support for distributed computing
78. **Incremental Updates**: Update only changed parts of analysis
79. **Resource Monitoring**: Monitor CPU, memory, and disk usage

#### **📋 Quality Assurance & Testing**

80. **Unit Tests**: Comprehensive test suite for all functions
81. **Integration Tests**: Test complete pipeline workflows
82. **Performance Tests**: Benchmark performance across different scenarios
83. **Regression Tests**: Ensure new features don't break existing functionality
84. **User Acceptance Testing**: Test with real user scenarios
85. **Documentation Tests**: Ensure documentation matches code
86. **Code Quality**: Implement code quality checks and standards

#### **📚 Documentation & Education**

87. **API Documentation**: Comprehensive API documentation
88. **User Manual**: Detailed user manual with examples
89. **Video Tutorials**: Screen-cast tutorials for common tasks
90. **Example Datasets**: Provide example datasets for testing
91. **Best Practices Guide**: Guide for optimal usage patterns
92. **Troubleshooting Guide**: Common problems and solutions
93. **FAQ Section**: Frequently asked questions and answers
94. **Community Support**: User forum and community resources

#### **🔒 Security & Reliability**

95. **Input Validation**: Comprehensive input validation and sanitization
96. **Error Recovery**: Graceful error handling and recovery
97. **Backup Systems**: Automatic backup of important data
98. **Version Control**: Track changes and enable rollbacks
99. **Security Audits**: Regular security reviews and updates
100. **Compliance**: Ensure compliance with data protection regulations

### 📊 **PERFORMANCE**

- **Speed**: Fast processing for sequences up to several hundred nucleotides
- **Memory**: Efficient memory usage for large datasets
- **Accuracy**: Matches ViennaRNA's probability calculations exactly
- **Reliability**: Robust error handling and validation

---

**Last Updated**: Current session
**Version**: v1 (Explicit Color Mapping Fixed)
**Status**: ✅ Production Ready

### 🎯 **PRIORITY LEVELS FOR FUTURE ENHANCEMENTS**

#### **🔥 HIGH PRIORITY** (Next Version - v2.0)

- **Batch Processing** (#1): Essential for processing multiple sequences
- **Custom Colormap Selection** (#8): Most requested feature
- **Detail Level Selection** (#17): Important for different use cases
- **Output Size Control** (#19): Critical for publication quality
- **Command-Line Interface** (#43): Essential for automation
- **Error Handling** (#53): Critical for reliability

#### **⚡ MEDIUM PRIORITY** (v2.1 - v2.5)

- **Custom Color Range** (#9): Useful for data-specific scaling
- **Statistical Analysis** (#26): Important for research applications
- **Report Generation** (#38): Valuable for documentation
- **Configuration Files** (#42): Important for reproducibility
- **Web Interface** (#49): Useful for non-technical users
- **Jupyter Integration** (#51): Important for research workflows

#### **🌟 LOW PRIORITY** (v3.0+)

- **Advanced Layout Algorithms** (#18): Nice-to-have feature
- **Plugin System** (#45): Future extensibility
- **GPU Acceleration** (#76): Performance optimization
- **Comparative Analysis** (#57): Advanced research feature
- **Cloud Deployment** (#68): Enterprise feature

#### **🔬 RESEARCH & DEVELOPMENT** (Long-term)

- **Structural Motif Detection** (#28): Advanced analysis
- **Evolutionary Analysis** (#59): Research application
- **Database Integration** (#69): Data integration
- **Machine Learning Integration**: AI-powered structure prediction
- **Real-time Collaboration**: Multi-user editing capabilities

---

### 1. **Primary Approach for Customization**
- **Use a YAML or JSON config file** for all layout, style, and theme options.
- **Support command-line overrides** for the most common parameters (e.g., detail level, output size, theme).

### 2. **Future Goal**
- **Add a GUI or web form** for generating config files, making it easy for non-technical users to customize visualization settings without editing files manually.

---

#### **How this will look in your workflow:**
- Users edit a `config.yaml` or `config.json` file to set all advanced options.
- For quick changes, users can override specific settings via command-line arguments.
- In the future, a GUI/web form will let users generate config files visually.

---

### **GOALS.md Update**

Here’s how to update your goals to reflect this:

```markdown
#### **🛠️ Customization & User Experience**

- **Config File Customization**: All layout, style, and theme options can be set in a user-editable YAML or JSON config file.
- **Command-Line Overrides**: Most common parameters (e.g., detail level, output size, theme) can be overridden via command-line arguments for convenience and automation.
- **[Future] GUI/Web Config Generator**: Provide a graphical or web-based interface for non-technical users to generate config files easily, with live previews and export options.

# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules

datas = [
    ('colormaps.yaml', '.'),
    ('config.yaml', '.'),
    ('profile_schema.json', '.'),
    ('rna_icon.ico', '.'),
    ('colormap_catalogs', 'colormap_catalogs'),
    ('bin/rnartistcore-0.4.6-SNAPSHOT-jar-with-dependencies.jar', 'bin'),
]
binaries = []
hiddenimports = ['RNA', 'yaml', 'PIL', 'numpy', 'customtkinter']

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Explicitly include necessary backends to avoid missing module errors without collecting 'tests'
hiddenimports += [
    'matplotlib.backends.backend_svg',
    'matplotlib.backends.backend_agg',
    'matplotlib.backends.backend_pdf',
    'matplotlib.backends.backend_ps',
    'matplotlib.pyplot'
]

# Collect matplotlib data (mpl-data, fonts, etc)
datas += collect_data_files('matplotlib')

# Collect CustomTkinter assets
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RNAfold_to_RNArtist',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements=None,
    icon='rna_icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RNAfold_to_RNArtist',
)

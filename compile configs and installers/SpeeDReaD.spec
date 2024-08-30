# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['..\\src\\SpeeDReaD.py'],
    pathex=[],
    binaries=[],
    datas=[('X:/Documents/Python Workspace/SpeeDReaD/src/resources', 'resources/'), ('X:/Documents/Python Workspace/SpeeDReaD/src', 'src/')],
    hiddenimports=[],
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
    name='SpeeDReaD',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['X:\\Documents\\Python Workspace\\SpeeDReaD\\src\\resources\\icons.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SpeeDReaD',
)

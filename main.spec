# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\PythonProject\\Vanction-Minecraft-Archive-Viewer\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\PythonProject\\Vanction-Minecraft-Archive-Viewer\\icons\\mc_icon.ico', '.')],
    hiddenimports=['nbtlib'],
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
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\PythonProject\\Vanction-Minecraft-Archive-Viewer\\icons\\mc_icon.ico'],
)

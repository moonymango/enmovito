# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['enmovito.py'],
    pathex=[],
    binaries=[('C:\\Users\\moonymango\\anaconda3\\envs\\enmovito\\Library\\bin\\msvcp140.dll', '.'), 
              ('C:\\Users\\moonymango\\anaconda3\\envs\\enmovito\\Library\\bin\\msvcp140_1.dll', '.'), 
              ('C:\\Users\\moonymango\\anaconda3\\envs\\enmovito\\Library\\bin\\msvcp140_2.dll', '.'), 
              ('C:\\Users\\moonymango\\anaconda3\\envs\\enmovito\\Library\\bin\\msvcp140_atomic_wait.dll', '.'), 
              ('C:\\Users\\moonymango\\anaconda3\\envs\\enmovito\\Library\\bin\\msvcp140_codecvt_ids.dll', '.'), 
              ('C:\\Users\\moonymango\\anaconda3\\envs\\enmovito\\Library\\bin\\vcruntime140.dll', '.'), 
              ('C:\\Users\\moonymango\\anaconda3\\envs\\enmovito\\Library\\bin\\vcruntime140_1.dll', '.'), 
              ('C:\\Users\\moonymango\\anaconda3\\envs\\enmovito\\Library\\bin\\vcruntime140_threads.dll', '.'), 
              ('C:\\Users\\moonymango\\anaconda3\\envs\\enmovito\\Lib\\site-packages\\pandas.libs\\msvcp140-0f2ea95580b32bcfc81c235d5751ce78.dll', '.')],
    datas=[('themes', 'themes')],  # Only include themes, not example logs
    hiddenimports=['pandas', 'pandas._libs.window.aggregations', 'pandas._libs.window'],
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
    name='enmovito',
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
)

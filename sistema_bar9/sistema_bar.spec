# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('layout_botoes.json', '.'),
        ('modules', 'modules'),
        ('interfaces', 'interfaces'),
        ('scripts', 'scripts'),
        ('recibos', 'recibos'),
        ('recibos_pdf', 'recibos_pdf'),
        ('logs', 'logs')
    ],
    hiddenimports=[
        'mysql.connector',
        'win32print',
        'win32api',
        'decimal',
        'datetime'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SistemaBar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Mude para True se quiser ver o console para debug
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SistemaBar'
)
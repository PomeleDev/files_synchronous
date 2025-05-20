# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['synchronous.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('favicon.ico', '.'),                  # 图标文件打包进根目录
        ('resources_rc.py', '.')               # 资源模块打包进根目录
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='文件同步工具v0.3.exe',
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
    icon='favicon.ico',                       # 设置任务栏和可执行文件图标
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
)

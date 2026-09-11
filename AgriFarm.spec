# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('C:\\Users\\rafay.ahmed7\\Desktop\\AgriFarm\\AgriFarm\\_internal\\Logo', 'Logo'), ('C:\\Users\\rafay.ahmed7\\Desktop\\AgriFarm\\AgriFarm\\_internal\\config.yaml', '.')]
binaries = []
hiddenimports = ['pyodbc', 'yaml', 'darkdetect']
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\rafay.ahmed7\\Desktop\\AgriFarm\\AgriFarm\\launcher.py'],
    pathex=['C:\\Users\\rafay.ahmed7\\Desktop\\AgriFarm\\AgriFarm\\_internal'],
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
    a.binaries,
    a.datas,
    [],
    name='AgriFarm',
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
    icon=['C:\\Users\\rafay.ahmed7\\Desktop\\AgriFarm\\AgriFarm\\_internal\\Logo\\1F33E_color.ico'],
)

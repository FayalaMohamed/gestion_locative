# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

block_cipher = None

a = Analysis(
    ['D:\\code\\locations\\main.py'],
    pathex=['D:\\code\\locations'],
    binaries=[],
    datas=[
        ('D:\\code\\locations\\config.yaml', '.'),
        ('D:\\code\\locations\\app\\data\\google_drive_token.json', 'app\\data'),
        ('D:\\code\\locations\\app\\ui\\icon.png', 'app\\ui'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.ext.declarative',
        'alembic',
        'jinja2',
        'reportlab',
        'reportlab.lib',
        'reportlab.pdfgen',
        'pandas',
        'openpyxl',
        'google_auth_httplib2',
        'google_auth_oauthlib',
        'googleapiclient',
        'yaml',
        'dateutil',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GestionLocativePro',
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
    icon='D:\\code\\locations\\app\\ui\\icon.png',
)

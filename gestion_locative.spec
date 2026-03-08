# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

block_cipher = None

spec_dir = SPECPATH

a = Analysis(
    [os.path.join(spec_dir, 'main.py')],
    pathex=[spec_dir],
    binaries=[],
    datas=[
        (os.path.join(spec_dir, 'config.yaml'), '.'),
        (os.path.join(spec_dir, 'app', 'ui', 'icon.png'), os.path.join('app', 'ui')),
        (os.path.join(spec_dir, 'alembic.ini'), '.'),
        (os.path.join(spec_dir, 'alembic'), 'alembic'),
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
    excludes=[
        'IPython',
        'ipython',
        'ipykernel',
        'nbformat',
        'nbconvert',
        'jedi',
        'parso',
        'prompt_toolkit',
        'wcwidth',
    ],
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
    icon=os.path.join(spec_dir, 'app', 'ui', 'icon.png'),
)

# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for AI Ergonomics & Digital-Wellness Backend.
Generates a standalone onedir bundle: dist/wellness_backend/
"""
import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

block_cipher = None

SPEC_ROOT = Path(SPECPATH).resolve()

# Collect full package data, binaries, and hidden imports for complex native packages
mp_datas, mp_binaries, mp_hidden = collect_all('mediapipe')
aiortc_datas, aiortc_binaries, aiortc_hidden = collect_all('aiortc')
av_datas, av_binaries, av_hidden = collect_all('av')
reportlab_datas, reportlab_binaries, reportlab_hidden = collect_all('reportlab')

# Project specific asset folders to bundle
datas = [
    (str(SPEC_ROOT / 'models'), 'models'),
    (str(SPEC_ROOT / 'calibration'), 'calibration'),
    (str(SPEC_ROOT / 'config'), 'config'),
    (str(SPEC_ROOT / '.env'), '.'),
    (str(SPEC_ROOT / 'frontend' / 'build'), 'frontend_build'),
]
datas += mp_datas + aiortc_datas + av_datas + reportlab_datas

binaries = mp_binaries + aiortc_binaries + av_binaries + reportlab_binaries

hiddenimports = [
    'engineio.async_drivers.threading',
    'dns',
    'dns.resolver',
    'dns.asyncresolver',
    'pymongo',
    'pymongo.srv_resolver',
    'bcrypt',
    'jwt',
    'plyer',
    'plyer.platforms',
    'plyer.platforms.win',
    'plyer.platforms.win.notification',
    'winsound',
    'matplotlib',
    'matplotlib.backends.backend_agg',
    'reportlab',
    'reportlab.platypus',
    'reportlab.lib',
    'reportlab.lib.colors',
    'reportlab.lib.styles',
    'google.generativeai',
    'generate_ai_pdf_report',
    'backend',
    'backend.paths',
    'backend.vision.pipeline',
    'backend.vision.face',
    'backend.vision.pose',
    'backend.vision.distance',
    'backend.vision.blink',
    'backend.vision.squint',
    'backend.vision.gaze_fixation',
    'backend.vision.forward_lean',
    'backend.vision.brightness',
    'backend.safety.engine',
    'backend.safety.rules',
    'backend.safety.temporal',
    'backend.app.annotator',
    'backend.app.notifier',
    'backend.app.reporter',
    'backend.telemetry.logger',
    'backend.auth.routes',
    'backend.auth.auth_utils',
    'backend.db.mongo',
    'backend.api.sessions_routes',
    'backend.config.loader',
    'backend.calibration.manager',
] + mp_hidden + aiortc_hidden + av_hidden + reportlab_hidden

a = Analysis(
    [str(SPEC_ROOT / 'backend' / 'api' / 'server.py')],
    pathex=[str(SPEC_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'IPython', 'notebook', 'pytest'],
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
    name='wellness_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,  # Keep console=True during development for clean error logs and debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(SPEC_ROOT / 'frontend' / 'public' / 'favicon.ico') if (SPEC_ROOT / 'frontend' / 'public' / 'favicon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='wellness_backend',
)

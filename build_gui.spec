# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[('鲸鱼.ico', '.'), ('README.md', '.')],
    hiddenimports=['requests', 'tkinter', 'selenium'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'PIL', 'scipy',
        'pytest', 'setuptools', 'wheel', 'pip'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 过滤不需要的文件
a.datas = [x for x in a.datas if not any([
    '功能总和.md' in x[0],
    '问题总和.md' in x[0],
    '技术问题记录.md' in x[0],
    'build.spec' in x[0],
    'saved_cookie.json' in x[0],
    'saved_cookies.json' in x[0],
    'gui_settings.json' in x[0],
    'cyforkk.bat' in x[0],
    'cyforkk.ps1' in x[0],
    'cyforkk.py' in x[0],
    '__pycache__' in x[0],
    '.pyc' in x[0],
    '.git' in x[0],
    '.ruff_cache' in x[0],
])]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='学习通图片爬取工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='鲸鱼.ico',  # 设置程序图标
)

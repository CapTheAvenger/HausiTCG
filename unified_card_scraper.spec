# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['scripts\\unified_card_scraper.py', 'scripts\\city_league_archetype_scraper.py', 'scripts\\limitless_online_scraper.py'],
    pathex=['scripts'],
    binaries=[],
    datas=[],
    hiddenimports=['html.parser', 'urllib.request', 'urllib.parse', 'csv', 'json', 'datetime', 'collections', 'city_league_archetype_scraper', 'limitless_online_scraper'],
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
    name='unified_card_scraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='unified_card_scraper',
)

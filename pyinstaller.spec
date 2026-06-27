# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.building.datastruct import Tree


project_root = Path(SPECPATH)

# PyInstaller 6 places non-executable COLLECT entries under contents_directory.
# Keep support files in _deps, but collect user-visible release assets at the
# bundle root so the extracted folder stays easy to understand.
root_visible_assets = Tree(str(project_root / "templates"), prefix="templates", typecode="PKG") + [
    ("cv.yml.example", str(project_root / "cv.yml.example"), "PKG"),
]

a = Analysis(
    [str(project_root / "scripts" / "generate.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    name="cv-generator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory="_deps",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    root_visible_assets,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="cv-generator",
)

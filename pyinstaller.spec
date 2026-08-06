# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

from PyInstaller.building.datastruct import Tree


project_root = Path(SPECPATH)


def windows_native_root():
    if sys.platform != "win32":
        return None

    configured_dirs = os.environ.get("WEASYPRINT_DLL_DIRECTORIES", "").split(os.pathsep)
    dll_dir = next((Path(path) for path in configured_dirs if path and Path(path).is_dir()), None)
    if dll_dir is None:
        raise SystemExit(
            "Windows builds require WEASYPRINT_DLL_DIRECTORIES to point to an "
            "MSYS2 mingw64/bin directory containing the WeasyPrint native DLLs."
        )
    return dll_dir.parent


native_root = windows_native_root()


def windows_native_binaries():
    if native_root is None:
        return []

    dll_dir = native_root / "bin"
    binaries = [(str(path), ".") for path in dll_dir.glob("*.dll")]
    if not binaries:
        raise SystemExit(f"No native DLLs found in WEASYPRINT_DLL_DIRECTORIES: {dll_dir}")
    return binaries


def windows_native_data():
    if native_root is None:
        return []

    fontconfig_dir = native_root / "etc" / "fonts"
    if not (fontconfig_dir / "fonts.conf").is_file():
        raise SystemExit(f"Fontconfig configuration not found: {fontconfig_dir}")
    return [(str(fontconfig_dir), "etc/fonts")]

# PyInstaller 6 places non-executable COLLECT entries under contents_directory.
# Keep support files in _deps, but collect user-visible release assets at the
# bundle root so the extracted folder stays easy to understand.
root_visible_assets = Tree(str(project_root / "templates"), prefix="templates", typecode="PKG") + [
    ("cv.yml.example", str(project_root / "cv.yml.example"), "PKG"),
    ("README.txt", str(project_root / "README.txt"), "PKG"),
]

a = Analysis(
    [str(project_root / "scripts" / "generate.py")],
    pathex=[str(project_root)],
    binaries=windows_native_binaries(),
    datas=windows_native_data(),
    hiddenimports=[],
    hookspath=[str(project_root / "hooks")],
    hooksconfig={},
    runtime_hooks=[str(project_root / "scripts" / "pyinstaller_runtime_hook.py")],
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

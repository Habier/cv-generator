import os
import sys
from pathlib import Path


if sys.platform == "win32" and getattr(sys, "frozen", False):
    dependency_dir = Path(sys.executable).resolve().parent / "_deps"
    os.environ["WEASYPRINT_DLL_DIRECTORIES"] = str(dependency_dir)
    fontconfig_dir = dependency_dir / "etc" / "fonts"
    os.environ["FONTCONFIG_PATH"] = str(fontconfig_dir)
    os.environ["FONTCONFIG_FILE"] = str(fontconfig_dir / "fonts.conf")
    _dll_directory_handle = os.add_dll_directory(str(dependency_dir))

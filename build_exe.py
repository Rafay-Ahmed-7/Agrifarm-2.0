"""Build standalone AgriFarm.exe with PyInstaller."""
import sys
from pathlib import Path
import PyInstaller.__main__

base_dir = Path(__file__).resolve().parent
icon_path = base_dir / "_internal" / "Logo" / "1F33E_color.ico"
internal_path = base_dir / "_internal"

print(f"Building AgriFarm executable with icon: {icon_path}")

PyInstaller.__main__.run([
    str(base_dir / "launcher.py"),
    "--name=AgriFarm",
    "--onefile",
    "--noconsole",
    f"--icon={icon_path}",
    f"--paths={internal_path}",
    "--collect-all=customtkinter",
    "--hidden-import=pyodbc",
    "--hidden-import=yaml",
    "--hidden-import=darkdetect",
    f"--add-data={internal_path / 'Logo'};Logo",
    f"--add-data={internal_path / 'config.yaml'};.",
    "--clean",
    "-y",
])

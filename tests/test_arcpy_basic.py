# to run '''python -m pytest tests/test_arcpy_basic.py -v'''
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))
import os
import pytest
import arcpy_basic
from dotenv import load_dotenv


load_dotenv()
license_path = os.getenv("LIC_PATH")

def test_arcgis_license_levels_change():
    results = arcpy_basic.change_license_level() #when testing on the vdi inster varibable license_path
    assert len(results) == 3, "Did not run all 3 license scripts"  
    for i, result in enumerate(results):
            assert result.returncode == 0, f"License script #{i+1} failed"
            assert "error" not in (result.stderr or "").lower(), f"Script #{i+1} produced an error"
            assert result.stdout is not None

# to run '''python -m pytest tests/test_arcpy_basic.py -v'''
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))
import os
import pytest
import arcpy_basic
from dotenv import load_dotenv

pytestmark = pytest.mark.integration

load_dotenv()
license_dir = os.getenv("LIC_PATH")

ext_list=['3D','DataReviewer','GeoStats','ImageAnalyst','Network','Publisher','Spatial']

@pytest.mark.integration
def test_arcgis_license_levels_change():
    results = arcpy_basic.change_license_level(license_path=license_dir) #when testing on the vdi inster varibable license_path
    assert len(results) == 3, "Did not run all 3 license scripts"  
    for i, result in enumerate(results):
            assert result.returncode == 0, f"License script #{i+1} failed"
            assert "error" not in (result.stderr or "").lower(), f"Script #{i+1} produced an error"
            assert result.stdout is not None


@pytest.mark.integration
def test_check_out_extensions_real(require_arcgis_pro_env, license_guard, capfd):
    """
    Integration test that uses real arcpy + real licenses.
    IMPORTANT:
      - Run inside ArcGIS Pro Python env.
      - Ensure the extensions listed are licensed & reachable in this environment.
    """
    import arcpy
    ext_list = os.environ.get("ARCPY_TEST_EXTENSIONS", "Spatial,3D").split(",")
    product = arcpy.GetInstallInfo().get("ProductName", "")
    assert "ArcGIS Pro" in product, f"Unexpected product: {product}"
    for ext in ext_list:
        ext = ext.strip()
        with license_guard(ext):
            status = arcpy.CheckExtension(ext)
            if status not in ("Available", "CheckedOut", "AlreadyInitialized"):
                pytest.xfail(f"Extension {ext} not available here (status={status}).")

            arcpy_basic.check_out_extensions([ext])
            out, err = capfd.readouterr()
            assert f"{ext} checked out" in out
            assert f"{ext} checked in" in out
            post_status = arcpy.CheckExtension(ext)
            assert post_status in ("Available", "NotLicensed", "Unavailable", "CheckedOut") \
                or post_status.startswith("Available"), \
                f"Unexpected post-status for {ext}: {post_status}"


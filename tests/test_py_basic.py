 #to run '''python -m pytest tests/test_py_basic.py -v'''
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))
import os
import pytest
import py_basic
from dotenv import load_dotenv

load_dotenv()

def _env_paths():
    # explicitly check the same drives your script checks
    return [
        os.getenv("W_DRIVE"),
        os.getenv("O_DRIVE"),
        os.getenv("GDWUTS"),
        os.getenv("GSS_SHARE"),
        r"T:",
    ]


@pytest.mark.integration
def test_drives_are_accessible():
    """
    Fail if any of the configured drives/paths are missing.
    This ensures the network shares / mapped drives are available.
    """
    paths = [p for p in _env_paths() if p]  # skip unset envs
    if not paths:
        pytest.skip("No drive env vars are set; set W_DRIVE/O_DRIVE/GDWUTS/GSS_SHARE to run this test")
    missing = [p for p in paths if not os.path.exists(p)]
    assert not missing, f"The following drives/paths are not accessible: {missing}"


@pytest.mark.integration
def test_check_write_permissions_runs_and_cleans_up():
    """
    Run your check_write_persmissons() function end-to-end.
    Requires:
      - TEST_PROJECT env var pointing to a project that contains source_data/unit_testing.gdb
      - GSS_SHARE env var reachable
      - T: must be mapped (or module.folder_dir patched to a writable path)
    """
    test_project = os.getenv("TEST_PROJECT")
    if not test_project:
        pytest.skip("TEST_PROJECT not set; set it to run write-permissions test")

    gdb_path = os.path.join(test_project, "source_data", "unit_testing.gdb")
    if not os.path.exists(gdb_path):
        pytest.fail(f"Required file for test missing: {gdb_path} - create this file to run the test")

    # Ensure target folder exists (py_basic.folder_dir is expected to be something like "T:\\gr_2025_1508_gss_test")
    if not os.path.exists(py_basic.folder_dir):
        try:
            os.makedirs(py_basic.folder_dir, exist_ok=True)
        except Exception as exc:
            pytest.fail(f"Cannot create folder_dir {py_basic.folder_dir}: {exc}")

    # Run the function (this will zip, copy to T:, copy to GSS share and clean up)
    py_basic.check_write_persmissons()

    # confirm the test zip in TEST_PROJECT was removed by the function
    test_zip = os.path.join(test_project, "source_data", "unit_testing.zip")
    assert not os.path.exists(test_zip), f"{test_zip} should have been removed by check_write_persmissons()"


@pytest.mark.integration
def test_bcgw_test_con_can_connect_and_query():
    """
    Run the Oracle connectivity and example query. Skips if credentials are not provided.
    """
    if not os.getenv("BCGW_USERNAME") or not os.getenv("BCGW_PASSWORD"):
        pytest.skip("BCGW_USERNAME/BCGW_PASSWORD not set; skipping DB integration test")

    # This will attempt to connect to bcgw.bcgov:1521 and run the query in your function.
    py_basic.bcgw_test_con()
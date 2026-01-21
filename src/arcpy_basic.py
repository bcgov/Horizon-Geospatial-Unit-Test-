from pathlib import Path
import arcpy
from dotenv import load_dotenv
import logging
import os 
import subprocess 
import time
import ctypes


def close_vbs_popup(title="Information message", wait_seconds=5):
    """
    Closes WScript popup windows by title using WinAPI.
    """
    user32 = ctypes.windll.user32

    for _ in range(wait_seconds * 2):  # check twice per second
        hwnd = user32.FindWindowW(None, title)
        if hwnd:
            # WM_CLOSE = 0x0010
            user32.PostMessageW(hwnd, 0x0010, 0, 0)
            return True
        time.sleep(0.5)

    return False


def change_license_level(license_path=r"E:\apps_nt\bcgov\wsh\vbscript\Start_Menu\ArcGIS"):
    scripts = [
        os.path.join(license_path, "Set_ArcProEditor_license_type.vbs"),
        os.path.join(license_path, "Set_ArcProInfo_license_type.vbs"),
        os.path.join(license_path, "Set_ArcProView_license_type.vbs"),
    ]

    results = []

    for script in scripts:
        result = subprocess.run(
            ["cscript.exe", "//Nologo", script],
            capture_output=True,
            text=True
        )
        close_vbs_popup()
        results.append(result)

    return results


def check_out_extensions(extension_list):
    class LicenseError(Exception):
        pass
    for ext in extension_list:
        try:
            if arcpy.CheckExtension(ext) == "Available":
                arcpy.CheckOutExtension(ext)
                print(f"{ext} checked out")
            else:
                # raise a custom exception
                raise LicenseError
            arcpy.CheckInExtension(ext)
            print(f"{ext} checked in")
        except LicenseError:
            print(f"{ext} license is unavailable")
        except arcpy.ExecuteError:
            print(arcpy.GetMessages(2))

# def create_sde(output_folder,bcgw_username,bcgw_password):
#     arcpy.CreateDatabaseConnection_management(out_folder_path=output_folder, out_name='bcgw.bcgov.sde',database_platform='ORACLE', instance='bcgw.bcgov/idwprod1.bcgov',
#                 account_authentication='DATABASE_AUTH', username=bcgw_username, password=bcgw_password, save_user_pass='DO_NOT_SAVE_USERNAME')
#     logging.info(' new SDE connection')

# def creat_gdb(temp_dir):
#     current_workspace=os.path.join(temp_dir,'source_data','arcpy_basic.gdb')
#     arcpy.management.CreateFeatureDataset(current_workspace,'network',3005)

# def basic_intersect(temp_dir,sdeloc):
#     current_workspace=current_workspace=os.path.join(temp_dir,'source_data','arcpy_basic.gdb')
    
#     watersehd=os.path.join(sdeloc,'WHSE_BASEMAPPING.FWA_NAMED_WATERSHEDS_POLY')
#     arcpy.conversion.FeatureClassToFeatureClass(in_features = watersehd, out_path=current_workspace,
#                                                  out_name = named_watershed_file, where_clause= named_watershed_sql)


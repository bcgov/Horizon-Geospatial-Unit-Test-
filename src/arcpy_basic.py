from pathlib import Path
import arcpy
from dotenv import load_dotenv
import logging
import os 
import subprocess 


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
        results.append(result)

    return results





# def check_out_extensions():

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

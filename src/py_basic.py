
import pathlib
import os
from dotenv import load_dotenv
import logging
from sqlalchemy.engine import create_engine
import oracledb
import shutil
import zipfile


load_dotenv()
BCGW_USERNAME = os.getenv('BCGW_USERNAME')
BCGW_PASSWORD = os.getenv('BCGW_PASSWORD')
W_DRIVE = os.getenv('W_DRIVE')
O_DRIVE = os.getenv('O_DRIVE')
GDWUTS = os.getenv('GDWUTS')
TEST_PROJECT=os.getenv('TEST_PROJECT')
GSS_SHARE=os.getenv('GSS_SHARE')

test_directories=[W_DRIVE,O_DRIVE,GDWUTS,GSS_SHARE,r"T:"]

logging.basicConfig(level=logging.DEBUG)

t_drive=r"T:"
folder_dir=os.path.join(t_drive,'gr_2025_1508_gss_test')


def gss_dir():
    if not os.path.exists(folder_dir):
        os.mkdir(folder_dir)
    
    folders = [
        "deliverables/data",
        "documents",
        "source_data",
        "tools",
        "work",
    ]
    for f in folders:
        os.makedirs(os.path.join(folder_dir, f), exist_ok=True)

def check_drives(paths):
    # paths=[W_DRIVE,O_DRIVE,GDWUTS,GSS_SHARE,r"T:"]
    existing = []
    for p in paths:
        if os.path.exists(p):
            logging.debug(f"access to {p} successful")
            existing.append(p)
    return existing

def check_write_persmissons():
    gdb_name="unit_testing"
    test_file=os.path.join(TEST_PROJECT,"source_data",f"{gdb_name}.gdb")
    test_zip=os.path.join(TEST_PROJECT,"source_data",f"{gdb_name}.zip")
    temp_zip_out=os.path.join(folder_dir,"source_data",f"{gdb_name}.zip")
    share_folder=os.path.join(GSS_SHARE,'projects','gr_2025_1508_gss_test')
    share_copy=os.path.join(share_folder,f"{gdb_name}.zip")

    #zip file
    with zipfile.ZipFile(test_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(test_file, arcname=os.path.basename(test_file))
        logging.debug('file zipped')
    #copy to t drive 
    shutil.copyfile(test_zip,temp_zip_out)
    #delete zip file 
    os.remove(test_zip)
    logging.info('write access to w drive')
    #check zip integrity 
    with zipfile.ZipFile(temp_zip_out, 'r') as z:
            bad = z.testzip()
            if bad:
                logging.error(f"Corrupted file in zip: {bad}")
            else:
                logging.info("ZIP integrity OK")

    if not os.path.exists(share_folder):
        os.makedirs(share_folder)
    shutil.copyfile(temp_zip_out,share_copy)
    os.remove(share_copy)
    os.rmdir(share_folder)
    logging.info('write access to gss share location')

    assert not os.path.exists(test_zip)

def bcgw_test_con(): 
    USERNAME = BCGW_USERNAME
    PASSWORD = BCGW_PASSWORD
    HOST = "bcgw.bcgov"
    PORT = 1521
    SERVICE = "idwprod1.bcgov" 

    conn=oracledb.connect(user=USERNAME, password= PASSWORD, host=HOST, port=PORT,
                            service_name=SERVICE)
    
    engine= create_engine('oracle+oracledb://', creator=lambda: conn)
    logging.debug("oracle engine created")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM WHSE_LAND_USE_PLANNING.RMP_STRGC_LAND_RSRCE_PLAN_SVW")
    logging.info(f"query sucsseful, {cursor.fetchone()[0]} records returned")
    assert isinstance(cursor, oracledb.Cursor)



# def main():
#     gss_dir()
#     check_drives()
#     check_write_persmissons()
#     bcgw_test_con()

# if __name__ == "__main__":
#     main()


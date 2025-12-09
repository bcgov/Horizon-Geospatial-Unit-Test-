# Basic unit testing module with logging and environment variable loading


import logging 
from dotenv import load_dotenv
import os
import time 
import getpass
import datetime
import shutil 

# import the timing utilities you added to your project
from timing_utils_jsonl import timeit, Timer, set_run_context

#logger prefrences
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#logger.debug("")
#logger.info("")
#logger.warning("")
#logger.error(")
#logger.critical("")


# load dotenv variables
load_dotenv()
BCGW_USERNAME = os.getenv('BCGW_USERNAME')
BCGW_PASSWORD = os.getenv('BCGW_PASSWORD')
W_DRIVE = os.getenv('W_DRIVE_TEST_LOC')
O_PATH = os.getenv('O_PATH')
MOVE_GDB= os.getenv('MOVE_GDB')
MOVE_LAS_FILE= os.getenv('MOVE_LAS_FILE')
MOVE_DEM = os.getenv('MOVE_DEM')
logger.info("load env file")

_run_id = f"manual-{getpass.getuser()}-{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
set_run_context(_run_id)
TIMINGS_DIR = os.path.join(os.getcwd(), "timings")
os.makedirs(TIMINGS_DIR, exist_ok=True)
TIMING_JSONL = os.path.join(TIMINGS_DIR, f"session-{_run_id}.jsonl")


class basic_tests:
    def __init__(self):
        self.bcgw_username = BCGW_USERNAME
        self.bcgw_password = BCGW_PASSWORD
        self.w_drive = W_DRIVE
        self.o_path = O_PATH
        self.las= MOVE_LAS_FILE
        self.dem=MOVE_DEM
        self.test_gdb = MOVE_GDB
        self.w_test_path = os.path.join(self.w_drive, "unit_test_folder")
        self.user=os.getlogin()
        self.gdb_out=os.path.join(self.w_test_path,'source_data','unit_testing.gdb.zip')

    @timeit(jsonl_path=TIMING_JSONL)

    def create_structure(self):
        start = time.perf_counter()  
        deliverables_loc = os.path.join(self.w_test_path, "deliverables")
        documents_loc= os.path.join(self.w_test_path, "documents")
        restricted_loc = os.path.join(self.w_test_path, "restricted")
        source_data_loc = os.path.join(self.w_test_path, "source_data")
        tools_loc = os.path.join(self.w_test_path, "tools")
        work_loc = os.path.join(self.w_test_path, "work")
        if os.path.exists(self.w_test_path):
            logger.info("Test folder already exists at %s", self.w_test_path)
        else:
            os.makedirs(self.w_test_path, exist_ok=True)
            logger.info("Created test folder at %s", self.w_test_path) 
        os.makedirs(deliverables_loc, exist_ok=True)
        os.makedirs(documents_loc, exist_ok=True)
        os.makedirs(restricted_loc, exist_ok=True)
        os.makedirs(source_data_loc, exist_ok=True)
        os.makedirs(tools_loc, exist_ok=True)
        os.makedirs(work_loc, exist_ok=True)
        stop = time.perf_counter()
        logger.info("Created folder structure in %.4f seconds", stop - start)   

    @timeit(jsonl_path=TIMING_JSONL)
    def create_txt(self):
        start = time.perf_counter()
        txt_path = os.path.join(self.w_test_path, "documents", "test_file.txt")
        with open(txt_path, 'w') as f:
            f.write('''"Three Rings for the Elven-kings under the sky,
                        Seven for the Dwarf-lords in their halls of stone,
                        Nine for Mortal Men, doomed to die,
                        One for the Dark Lord on his dark throne
                        In the Land of Mordor where the Shadows lie.
                        One Ring to rule them all, One Ring to find them,
                        One Ring to bring them all and in the darkness bind them.
                        In the Land of Mordor where the Shadows lie."''')
        stop = time.perf_counter()
        logger.info("Created test text file in %.4f seconds", stop - start)

    @timeit(jsonl_path=TIMING_JSONL)
    def move_gdb(self):
        shutil.copytree(self.test_gdb,self.gdb_out)

    @timeit(jsonl_path=TIMING_JSONL)
    def move_las(self):
        las_out=os.path.join(self.w_test_path,'source_data','bc_102i080_3_4_4_xyes_8_utm9_20240316_20240316.laz')
        shutil.copyfile(self.las,las_out)
    
    @timeit(jsonl_path=TIMING_JSONL)
    def move_dem(self):
        dem_out=os.path.join(self.w_test_path,'source_data','bc_102i080_3_4_4_xli1m_utm9_20240316_20240316.tif')
        shutil.copyfile(self.dem,dem_out)

    @timeit(jsonl_path=TIMING_JSONL)
    def unzip_it(self):
        zip_out=os.path.join(self.w_test_path,'source_data',)
        shutil.unpack_archive(self.gdb_out, zip_out)


    @timeit(jsonl_path=TIMING_JSONL)
    def list_files(self, root_dir):
        for root, dirs, files in os.walk(root_dir):
            logger.info(f" Current directory: {root}")
            
        for d in dirs:
            logger.info(f"  - Subdirectory: {d}")
        
        for f in files:
            logger.info(f"  - File: {f}")

    @timeit(jsonl_path=TIMING_JSONL)
    def delete_all(self):
        shutil.rmtree(self.w_test_path)

if __name__ == "__main__":
    bt = basic_tests()
    bt.create_structure()
    bt.create_txt()
    bt.move_gdb()
    bt.unzip_it
    bt.move_las()
    bt.move_dem()
    bt.list_files(os.path.join(W_DRIVE,"unit_test_folder"))
    # bt.delete_all()
    logger.info("Timings written to %s", TIMING_JSONL)
# Basic unit testing module with logging and environment variable loading


import logging 
from dotenv import load_dotenv
import os
import time 
import csv
import getpass
import datetime

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
        self.w_test_path = os.path.join(self.w_drive, "unit_test_folder")
        self.user=os.getlogin()

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
    

    
if __name__ == "__main__":
    bt = basic_tests()
    bt.create_structure()
    bt.create_txt()
    logger.info("Timings written to %s", TIMING_JSONL)
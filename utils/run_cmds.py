import logging
import subprocess as sp
from multiprocessing import Pool
from tqdm import tqdm

logger = logging.getLogger(__name__)

def execute_cmd(cmd):
    ret = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    try:
        assert ret.returncode == 0
    except AssertionError as err:
        logger.info("Set logging level DEBUG to get more error messages")
        logger.debug(f"\n {ret.stdout.decode('utf-8')}")
        logger.debug(f"\n {ret.stderr.decode('utf-8')}")
        return False
    else:
        return True

def parallel(func, filelist):
    with Pool as pool:
        list(tqdm(pool.imap_unordered(func, filelist), total=len(filelist)))
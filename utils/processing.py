import time
import logging
import subprocess as sp
from multiprocessing import Pool
from tqdm import tqdm

logger = logging.getLogger(__name__)

def timer(func, *args, **kwargs):
    start_time = time.time()
    func(*args, **kwargs)
    return time.time() - start_time

def execute_cmd(cmd):
    ret = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    try:
        assert ret.returncode == 0
    except AssertionError as err:
        logger.info(f"The stdout and stderr of executed command: {''.join(str(s)+' ' for s in cmd)}")
        print(f"\n {ret.stdout.decode('utf-8')}")
        print(f"\n {ret.stderr.decode('utf-8')}")
        return False
    else:
        return True

def parallel(func, filelist):
    '''
    Parallel processing with multiprocessing.Pool(). (Works better with functools.partial())

    Parameters:
        func (function): The target function for parallel processing.
        filelist (list): The list of files to process with the input function.
    '''
    with Pool() as pool:
        list(tqdm(pool.imap_unordered(func, filelist), total=len(filelist)))
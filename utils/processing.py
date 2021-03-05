import time
import logging
from typing import List, Iterable
import subprocess as sp
from multiprocessing import Pool
from tqdm import tqdm

logger = logging.getLogger(__name__)

def timer(func, *args, **kwargs) -> float:
    """Calculate function execution time.

    Args:
        func (function): Executed function.

    Returns:
        float: Execution time in seconds.
    """
    start_time = time.time()
    func(*args, **kwargs)
    return time.time() - start_time

def execute_cmd(cmd: List[str]) -> bool:
    """Wrapper for executing a command with subprocess.

    Args:
        cmd (List[str]): Command to execute.

    Returns:
        bool: successful execute or not.
    """
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

def parallel(func, filelist: Iterable[str]) -> None:
    """Parallel processing with multiprocessing.Pool(). (Works better with functools.partial().)

    Args:
        func (function): The target function for parallel processing.
        filelist (iterable): The file list to process with the input function.
    """
    with Pool() as pool:
        list(tqdm(pool.imap_unordered(func, filelist), total=len(filelist)))
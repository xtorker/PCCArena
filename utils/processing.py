import logging
from functools import partial
from typing import Callable, Iterable
from multiprocessing import Pool, Manager

import GPUtil
from tqdm import tqdm

logger = logging.getLogger(__name__)

def parallel(
        func: Callable,
        filelist:Iterable,
        use_gpu: bool = False,
        nbprocesses: int = None
    ) -> None:
    """Parallel processing with multiprocessing.Pool(), works better 
    with functools.partial().
    
    If ``use_gpu`` is True, ``gpu_queue`` will be passed to ``func`` as 
    a keyword argument. The input ``func`` needs to handle the keyword
    parameter ``gpu_queue`` and select the GPU with gpu_queue.get(). 
    Don't forget to put the GPU id back to the gpu_queue at the end of
    ``func``.
    
    Parameters
    ----------
    func : `Callable`
        The target function for parallel processing.
    filelist : `Iterable`
        The file list to process with the input function.
    use_gpu : `bool`, optional
        True for running NN-based PCC algs., False otherwise. 
        Defaults to False.
    nbprocesses : `int`, optional
        Specify the number of cpu parallel processes. If None, it will 
        equal to the cpu count. Defaults to None.
    
    Raises
    ------
    `ValueError`
        No available GPU.
    """
    if use_gpu is True:
        # Get the number of available GPUs
        deviceIDs = GPUtil.getAvailable(
            order = 'first',
            limit = 8,
            maxLoad = 0.5,
            maxMemory = 0.2,
            includeNan=False,
            excludeID=[],
            excludeUUID=[]
        )
        process = len(deviceIDs)
        
        if process <= 0:
            logger.error(
                "No available GPU. Check with the threshold parameters "
                "of ``GPUtil.getAvailable()``"
            )
            raise ValueError
        
        manager = Manager()
        gpu_queue = manager.Queue()
        for id in deviceIDs:
            gpu_queue.put(id)
        pfunc = partial(func, gpu_queue=gpu_queue)
    else:
        process = nbprocesses
        pfunc = func
    
    with Pool(process) as pool:
        list(tqdm(pool.imap_unordered(pfunc, filelist), total=len(filelist)))
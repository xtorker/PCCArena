# @inproceedings{h-pacdp-01,
#    author    = "S.~{Har-Peled}",
#    booktitle = SOCG_2001,
#    title     = "A Practical Approach for Computing the Diameter
#                 of a Point-Set",
#    year      = 2001,
#    pages     = {177--186},
# }
# 
# [ref.] https://sarielhp.org/research/papers/00/diameter/diam_prog.html

import re
import os
import logging
import numpy as np
import subprocess as sp
from pathlib import Path
from typing import Union

from pyntcloud import PyntCloud

logger = logging.getLogger(__name__)

def findMaxNNdistance(pc_file: Union[str, Path]) -> str:
    """A wrapper of libgdiam-1.0.3, calculating the max NN distance in 
    the point cloud ``pc_file``.
    
    Parameters
    ----------
    pc_file : `Union[str, Path]`
        Input point cloud.
    
    Returns
    -------
    `str`
        Max NN distance found in the point cloud.
    
    Raises
    ------
    `RuntimeError`
        Failed to calculate the max NN distance.
    """
    gdiam_bin = (
        Path(__file__).parent
        .joinpath('libgdiam-1.0.3/build/gdiam_test').resolve()
    )
    tmp_file = Path(pc_file).with_suffix('.xyz')
    pc = PyntCloud.from_file(str(pc_file))
    coords = ['x', 'y', 'z']
    points = pc.points[coords].values
    num_points = len(points)
    np.savetxt(tmp_file, points, header=str(num_points), comments='')
    cmd = [gdiam_bin, tmp_file]
    ret = sp.run(cmd, capture_output=True, universal_newlines=True)
    os.remove(tmp_file)
    for line in ret.stdout.splitlines():
        m = re.search(f'(?<=Diameter distance: ).*', line)
        if m:
            return m.group()
    logger.warning(f"Failed to find diameter in {pc_file}")
    raise RuntimeError
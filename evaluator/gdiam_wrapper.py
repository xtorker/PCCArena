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
import numpy as np
from pathlib import Path
from pyntcloud import PyntCloud
import subprocess as sp

def findMaxNNdistance(pc_file):
    gdiam_bin = Path(__file__).parent.joinpath('libgdiam-1.0.3/gdiam_test').resolve()
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
    print("Failed to find diameter.")
    return False

if __name__ == '__main__':
    findMaxNNdistance("/mnt/data6/chenghao/MPEG_dataset/8i/8iVFBv2/longdress/Ply/longdress_vox10_1051.ply")
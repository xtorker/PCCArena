import argparse
import logging
import numpy as np
from pathlib import Path
from pyntcloud import PyntCloud
import subprocess as sp
from multiprocessing import Pool
from functools import partial
from tqdm import tqdm

def work(filepath, args):
    infile = Path(args.src_dir).joinpath(filepath)
    outfile = Path(args.dest_dir).joinpath(filepath)
    outfile.parent.mkdir(parents=True, exist_ok=True)

    with open(infile, 'rb') as f:
        pc = PyntCloud.from_file(str(infile))
        coords = ['x', 'y', 'z']
        points = pc.points[coords].values
        points[:,0] = points[:,0] - np.min(points[:,0])
        points[:,1] = points[:,1] - np.min(points[:,1])
        points[:,2] = points[:,2] - np.min(points[:,2])
        points = points / np.max(points) * (args.scale - 1)
        pc.points[coords] = points

        pc.to_file(str(outfile))
    return

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s',
        datefmt='%Y%m%d %H:%M:%S',
    )


    parser = argparse.ArgumentParser(
        description='Normalize point cloud (.ply) to certain scale.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "src_dir",
        help="input point cloud (.ply) directory."
    )
    parser.add_argument(
        "dest_dir",
        help="output point cloud (.ply) directory."
    )
    parser.add_argument(
        "-s",
        "--scale",
        help="Scale factor, equal to max. bounding box. (default=1)",
        type=int,
        default=1,
    )
    args = parser.parse_args()

    # glob for filename only
    pc_files = [path.relative_to(args.src_dir) for path in Path(args.src_dir).rglob("*.ply")]

    files_len = len(pc_files)
    logging.info(f"Found {files_len} point clouds (.ply) in {args.src_dir}.")
    assert files_len > 0

    pfunc = partial(work, args=args)
    with Pool() as p:
        list(tqdm(p.imap_unordered(pfunc, pc_files), total=files_len))
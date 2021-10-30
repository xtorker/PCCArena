import argparse
import logging
import time
import os
import numpy as np
from pathlib import Path
import subprocess as sp
from multiprocessing import Pool
from functools import partial
from tqdm import tqdm

def work(filepath, args):
    # workaround for using xvfb with subprocess
    # ref:https://stackoverflow.com/a/41276014
    env = {
        **os.environ,
        "DISPLAY": ":90",
    }

    infile = Path(args.src_dir).joinpath(filepath)
    outfile_geo = Path(args.dest_dir).joinpath("geo", filepath).with_suffix('.ply')
    outfile_geo_normal = Path(args.dest_dir).joinpath("geo_normal", filepath).with_suffix('.ply')
    outfile_color = Path(args.dest_dir).joinpath("color", filepath).with_suffix('.ply')
    outfile_color_normal = Path(args.dest_dir).joinpath("color_normal", filepath).with_suffix('.ply')
    # outfile_geo.parent.mkdir(parents=True, exist_ok=True)
    # outfile_geo_normal.parent.mkdir(parents=True, exist_ok=True)
    outfile_color.parent.mkdir(parents=True, exist_ok=True)
    outfile_color_normal.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        'cloudcompare.CloudCompare',
        '-SILENT',
        '-AUTO_SAVE', 'OFF',
        '-O', infile,
        '-SAMPLE_MESH', 'POINTS', str(args.num),
        '-OCTREE_NORMALS', 'auto',
        '-CLEAR_MESHES',
    ]

    # save color_normal
    cmd = cmd + [
        '-ORIENT_NORMS_MST', str(args.knn),
        '-C_EXPORT_FMT', 'PLY',
        '-NO_TIMESTAMP',
        '-SAVE_CLOUDS', 'FILE', outfile_color_normal
    ]

    # save color
    cmd = cmd + [
        '-CLEAR_NORMALS',
        '-C_EXPORT_FMT', 'PLY',
        '-NO_TIMESTAMP',
        '-SAVE_CLOUDS', 'FILE', outfile_color
    ]

    # save geo
    # cmd = cmd + [
    #     '-CLEAR_NORMALS',
    #     # '-REMOVE_RGB',
    #     '-C_EXPORT_FMT', 'PLY',
    #     '-NO_TIMESTAMP',
    #     '-SAVE_CLOUDS', 'FILE', outfile_geo
    # ]

    # # python 3.6
    # output = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, env=env)
    # assert output.returncode == 0, output.stderr.decode("utf-8") + output.stdout.decode("utf-8")
    # # python 3.7 up
    # # output = sp.run(cmd, capture_output=True)
    # # assert output.returncode == 0, output.stderr.decode("utf-8") + output.stdout.decode("utf-8")

    # cmd = [
    #     'cloudcompare.CloudCompare',
    #     '-SILENT',
    #     '-AUTO_SAVE', 'OFF',
    #     '-O', outfile_color_normal,
    #     '-REMOVE_RGB',
    #     '-C_EXPORT_FMT', 'PLY',
    #     '-NO_TIMESTAMP',
    #     '-SAVE_CLOUDS', 'FILE', outfile_geo_normal
    # ]

    output = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, env=env)
    assert output.returncode == 0, output.stderr.decode("utf-8") + output.stdout.decode("utf-8")

    return

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s',
        datefmt='%Y%m%d %H:%M:%S',
    )


    parser = argparse.ArgumentParser(
        description='A wrapper for CloudCompare to sample the mesh (.obj) to point cloud (.ply), output three type of dataset: geo_only, w_color, and w_color_normal.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "src_dir",
        help="input mesh directory."
    )
    parser.add_argument(
        "dest_dir",
        help="output point cloud directory."
    )
    parser.add_argument(
        "-n",
        "--sample_point",
        help="number of points to sample.",
        type=int,
        default=500000,
        dest="num"
    )
    parser.add_argument(
        "-k",
        "--knn",
        help="max NN of KDTree search for orienting the normals.",
        type=int,
        default=10,
        dest="knn"
    )
    args = parser.parse_args()

    # workaround of xvfb-run working with multiprocessing
    # os.system("Xvfb :99 &")

    # glob for mesh filename only
    mesh_files = [path.relative_to(args.src_dir) for path in Path(args.src_dir).rglob("*.obj")]

    files_len = len(mesh_files)
    logging.info(f"Found {files_len} mesh files (.off) in {args.src_dir}.")
    assert files_len > 0

    pfunc = partial(work, args=args)

    with Pool(os.cpu_count()) as p:
        list(tqdm(p.imap_unordered(pfunc, mesh_files), total=files_len))
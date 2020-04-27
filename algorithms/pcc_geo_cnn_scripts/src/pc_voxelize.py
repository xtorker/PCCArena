#!/usr/bin/env python

################################################################################
### Init
################################################################################
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

import os
from os.path import join, basename, split, splitext
from os import makedirs
from glob import glob
from pyntcloud import PyntCloud
import numpy as np
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
import argparse
import functools

################################################################################
### Definitions
################################################################################
def process(path, args):
    ori_path = join(args.source, path)
    target_path, _ = splitext(join(args.dest, path))
    target_path += '.ply'
    target_folder, _ = split(target_path)
    makedirs(target_folder, exist_ok=True)

    logger.debug(f"Writing PC {ori_path} to {target_path}")

    with open(ori_path, 'rb') as f:
        pc = PyntCloud.from_file(ori_path)
        coords = ['x', 'y', 'z']
        points = pc.points.values

        if(args.mode==0):
            points = points * (args.vg_size - 1)
            points = np.round(points)
        else:
            points = points / (args.vg_size - 1)

        pc.points[coords] = points

        if(args.mode==0):
            if len(set(pc.points.columns) - set(coords)) > 0:
                pc.points = pc.points.groupby(by=coords, sort=False).mean()
            else:
                pc.points = pc.points.drop_duplicates()

        pc.to_file(target_path)

################################################################################
### Script
################################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'source', 
        help='Source directory')
    parser.add_argument(
        'input_pattern',
        help='File detection pattern.')
    parser.add_argument(
        'dest', 
        help='Destination directory')
    parser.add_argument(
        '--mode', type=int, default=0,
        help='Execution mode (0: extend scale to vg_size; 1: shrink scale back to [0-1])')
    parser.add_argument(
        '--vg_size', type=int, default=64,
        help='Voxel Grid resolution for x, y, z dimensions')

    args = parser.parse_args()

    assert os.path.exists(args.source), f'{args.source} does not exist'
    # assert not os.path.exists(args.dest), f'{args.dest} already exists'
    assert args.vg_size > 0, f'vg_size must be positive'

    paths = glob(join(args.source, args.input_pattern), recursive=True)
    files = [x[len(args.source) + 1:] for x in paths]
    files_len = len(files)
    assert files_len > 0
    logger.info(f'Found {files_len} models in {args.source}')

    with Pool() as p:
        process_f = functools.partial(process, args=args)
        list(tqdm(p.imap(process_f, files), total=files_len)) 
 
    logger.info(f'{files_len} models written to {args.dest}')

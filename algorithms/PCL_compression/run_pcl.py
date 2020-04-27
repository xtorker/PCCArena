#Process level parallelism for shell commands
import os
from os.path import join, basename, split, splitext
import sys
from os import makedirs
from glob import glob
import subprocess as sp
import time
import logging
import argparse
from multiprocessing import Pool
import functools
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

def work(path, args):
    source_path = join(args.source, path)
    bin_path, _ = splitext(join(args.dest, 'bin', path))
    bin_path += '.bin'
    bin_folder, _ = split(bin_path)
    makedirs(bin_folder, exist_ok=True)
    dec_path, _ = splitext(join(args.dest, 'dec', path))
    dec_path += '_dec.ply'
    dec_folder, _ = split(dec_path)
    makedirs(dec_folder, exist_ok=True)
    evl_path, _ = splitext(join(args.dest, 'evl', path))
    evl_path += '_evl.log'
    evl_folder, _ = split(evl_path)
    makedirs(evl_folder, exist_ok=True)

    ## Encode ##
    enc_start = time.time()
    sp.call(['./build/PCL_compression', 
             source_path,
             bin_path,
             '0', # encode mode
             str(args.pointRes),
             str(args.octreeRes),
             str(args.doVoxel),
             str(args.doColor),
             str(args.colorRes)], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    enc_end = time.time()
    enc_time = enc_end - enc_start #shows in sec

    ## Decode ##
    dec_start = time.time()
    sp.call(['./build/PCL_compression', 
             bin_path,
             dec_path,
             '1', # decode mode
             str(args.pointRes),
             str(args.octreeRes),
             str(args.doVoxel),
             str(args.doColor),
             str(args.colorRes)], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    dec_end = time.time()
    dec_time = dec_end - dec_start #shows in sec

    with open(evl_path, 'w') as f:
        lines = [f'PCL Compression execution time\n\n',
                 f'original point cloud: {source_path}\n',
                 f'compressed bitstream: {bin_path}\n',
                 f'decompressed point cloud: {dec_path}\n\n',
                 f'Encoding time (sec)    : {enc_time}\n',
                 f'Decoding time (sec)    : {dec_time}\n',
                 '======================================\n\n\n']
        f.writelines(lines)

    ## Evaluate ##
    sys.path.append('../../evaluator')
    from evaluate_pc import evaluate
    evaluate(source_path, bin_path, dec_path, evl_path)
    
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('source', help='Source point cloud directory.')
    parser.add_argument('dest', help='Directory for compressed bitstream/decompressed point cloud/evaluation log.')
    parser.add_argument('octreeRes', type=float,
                        help='Define the voxel size of the octree during encoding. This enables a trade-off between high frame/update rates and compression efficiency.')
    parser.add_argument('--pointRes', type=float, default=0.0001,
                        help='Define the coding precision for point coordinates, should be lower than sampling noise. (default: 0.0001)')
    parser.add_argument('--colorRes', type=int, default=8,
                        help='Define the amount of bits per color component to be encoded. (default: 8)')
    parser.add_argument('--doVoxel', type=int, default=1,
                        help='Drop the duplicate points during voxelization. (default: 1))')
    parser.add_argument('--doColor', type=int, default=0,
                        help='Enable color attribute encoding. (default: 0)')

    args = parser.parse_args()

    assert os.path.exists(args.source), f'{args.source} does not exist'
    # assert not os.path.exists(args.dest), f'{args.dest} already exists'


    paths = glob(join(args.source, '**', 'test', '*.ply'), recursive=True)
    files = [x[len(args.source) + 1:] for x in paths]
    files_len = len(files)
    assert files_len > 0
    logger.info(f'Found {files_len} models in {args.source}')

    with Pool() as p:
        work_f = functools.partial(work, args=args)
        list(tqdm(p.imap(work_f, files), total=files_len))

    ## Statisticize ##
    sp.call(['python', '../../evaluator/cal_avg_std.py', join(args.dest, 'evl')], stdout=sp.DEVNULL)

    logger.info(f'{files_len} models compressed to {args.dest}/bin')
    logger.info(f'{files_len} models decompressed to {args.dest}/dec')
    logger.info(f'{files_len} evaluation log stored to {args.dest}/evl')
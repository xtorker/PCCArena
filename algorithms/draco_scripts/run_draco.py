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
    """Defines the work unit on an input file"""
    source_path = join(args.source, path)
    bin_path, _ = splitext(join(args.dest, 'bin', path))
    bin_path += '.drc'
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

    if args.pc:
        pc_arg = '-point_cloud'
    else:
        pc_arg = ''

    ## Encode ##
    enc_start = time.time()
    sp.call(['./build/draco_encoder', '-i', source_path, '-o', bin_path, 
            '-qp', str(args.qp), '-qt', str(args.qt), '-qn', str(args.qn), 
            '-qg', str(args.qg), '-cl', str(args.cl), pc_arg], stdout=sp.DEVNULL)
    enc_end = time.time()
    enc_time = enc_end - enc_start #shows in sec

    ## Decode ##
    dec_start = time.time()
    sp.call(['./build/draco_decoder', '-i', bin_path, '-o', dec_path], stdout=sp.DEVNULL)
    dec_end = time.time()
    dec_time = dec_end - dec_start #shows in sec
    
    with open(evl_path, 'w') as f:
        lines = [f'Google Draco execution time\n\n',
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
    parser.add_argument('dest', help='Directory for compressed bitstream/decompressed point cloud/evaluation log')
    parser.add_argument('--qp', type=int, default=14,
                        help='Quantization bits for the position attribute.')
    parser.add_argument('--qt', type=int, default=12,
                        help='Quantization bits for the texture coordinate attribute.')
    parser.add_argument('--qn', type=int, default=10,
                        help='Quantization bits for the normal vector attribute.')
    parser.add_argument('--qg', type=int, default=8,
                        help='Quantization bits for the generic attribute.')
    parser.add_argument('--cl', type=int, default=7,
                        help='Compression level [0-10], most=10, least=0.')
    parser.add_argument('--pc', type=bool, default=True,
                        help='Forces the input to be encoded as a point cloud.')

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

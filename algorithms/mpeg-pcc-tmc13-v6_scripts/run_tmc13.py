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
    sp.call(['./build/tmc3/tmc3', 
             '--mode=0', 
             '--uncompressedDataPath='+source_path, 
             '--compressedStreamPath='+bin_path, 
             '--mergeDuplicatedPoints='+str(args.merge),
             '--positionQuantizationScale='+str(args.scale_factor),
             '--inferredDirectCodingMode=1'
             ], stdout=sp.DEVNULL)
    enc_end = time.time()
    enc_time = enc_end - enc_start #shows in sec

    ## Decode ##
    dec_start = time.time()
    sp.call(['./build/tmc3/tmc3', 
             '--mode=1', 
             '--compressedStreamPath='+bin_path, 
             '--reconstructedDataPath='+dec_path], stdout=sp.DEVNULL)
    dec_end = time.time()
    dec_time = dec_end - dec_start #shows in sec

    with open(evl_path, 'w') as f:
        lines = [f'MPEG G-PCC TMC13 execution time\n\n',
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
    parser.add_argument('--scale_factor', type=int, default=1,
                        help='Scale factor to be applied to point positions during quantization process. (default:1)')
    '''
    Scale Factor:
    Prior to encoding, scale the point cloud geometry by multiplying each co-ordinate by the real FACTOR and rounding to integer precision. The scale factor is written to the bitstream and a decoder may use it to provide output at the original scale.
    '''
    parser.add_argument('--merge', type=int, default=1,
                        help='Enables removal of duplicated points (default:1)')

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
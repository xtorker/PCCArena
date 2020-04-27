#Process level parallelism for shell commands
import os
from os.path import join, basename, split, splitext
import sys
from os import makedirs
from glob import glob
import subprocess as sp
import time
import re
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

def work(args):
    
    scaled_folder = join(args.dest, 'scaled')
    makedirs(scaled_folder, exist_ok=True)
    bin_folder = join(args.dest, 'bin')
    makedirs(bin_folder, exist_ok=True)
    dec_folder = join(args.dest, 'dec')
    makedirs(dec_folder, exist_ok=True)
    evl_folder = join(args.dest, 'evl')
    makedirs(evl_folder, exist_ok=True)
    rescale_folder = join(args.dest, 'rescale')
    makedirs(rescale_folder, exist_ok=True)
    files_len = len(glob(join(args.source, '**', 'test', '*.ply'), recursive=True))

    start_time = time.time()
    ### Scale to args.resolution ###
    sp.call(['python', 'src/pc_voxelize.py',
             args.source, '**/test/*.ply', scaled_folder,
             '--mode', '0',
             '--vg_size', str(args.resolution)])

    ### Divide point cloud into 8 sub-point cloud to increase the voxel resolution of input point cloud ###
    if args.divide_oct == 1:
        divided_folder = join(args.dest, 'divided')
        makedirs(divided_folder, exist_ok=True)
        sp.call(['python', 'src/pc_divide_oct.py',
                scaled_folder, '**/test/*.ply', divided_folder,
                '--mode', '0'])
        scaled_folder = divided_folder
        # change the resolution of enc/dec
        divided_resolution = int(args.resolution / 2)
    else:
        divided_resolution = args.resolution

    preprocessing_time = (time.time() - start_time) / files_len
    ### Encode ###
    compress = sp.run(['python', './src/compress.py', 
                        scaled_folder, '**/test/*.ply', bin_folder, args.checkpoint_dir,
                        '--batch_size', str(args.batch_size),
                        '--read_batch_size', str(args.read_batch_size),
                        '--resolution', str(divided_resolution),
                        '--num_filters', str(args.num_filters),
                        '--preprocess_threads', str(args.preprocess_threads)], stdout=sp.PIPE, universal_newlines=True)
    for line in compress.stdout.splitlines():
        m = re.search('(?<=Loading model time: ).*', line)
        if (m):
            load_model_time = m.group()
        m = re.search('(?<=avg. Encoding time: ).*', line)
        if (m):
            enc_time = m.group()
        m = re.search('(?<=stdev. Encoding time: ).*', line)
        if (m):
            std_enc_time = m.group()

    ### Decode ###
    decompress = sp.run(['python', './src/decompress.py', 
                          bin_folder, '**/test/*.ply.bin', dec_folder, args.checkpoint_dir,
                          '--batch_size', str(args.batch_size),
                          '--read_batch_size', str(args.read_batch_size),
                          '--num_filters', str(args.num_filters),
                          '--preprocess_threads', str(args.preprocess_threads),
                          '--output_extension', args.output_extension], stdout=sp.PIPE, universal_newlines=True)
    for line in decompress.stdout.splitlines():
        # m = re.search('(?<=Loading model time: ).*', line)
        # if (m):
        #     load_model_time = m.group()
        m = re.search('(?<=avg. Decoding time: ).*', line)
        if (m):
            dec_time = m.group()
        m = re.search('(?<=stdev. Decoding time: ).*', line)
        if (m):
            std_dec_time = m.group()

    start_time = time.time()
    ### Merge 8 sub-point cloud back to one original point cloud ###
    if args.divide_oct == 1:
        merged_folder = join(args.dest, 'merged')
        makedirs(merged_folder, exist_ok=True)
        sp.call(['python', 'src/pc_divide_oct.py',
                dec_folder, '**/test/*_sub0.ply.bin.ply', merged_folder, # only input _sub0 for representation
                '--mode', '1'])
        dec_folder = merged_folder

    ### Rescale back ###
    sp.call(['python', 'src/pc_voxelize.py',
             dec_folder, '**/test/*.ply', rescale_folder,
             '--mode', '1',
             '--vg_size', str(args.resolution)])

    ### Merge bin files in order to calculate the compressed file size ###
    if args.divide_oct == 1:
        bin_files = glob(join(bin_folder, '**', 'test', '*_sub0.ply.bin'), recursive=True)
        bin_files_len = len(bin_files)
        assert bin_files_len > 0
        logger.info(f'Found {bin_files_len * 8} compressed files in {bin_folder}')
        for bin_file in tqdm(bin_files):
            bin_file = bin_file.replace('_sub0.', '.')
            with open(bin_file, 'wb') as f:
                for idx in range(8):
                    [filename, ext] = bin_file.split(os.extsep, 1)
                    sub_bin_file = f'{filename}_sub{idx}.{ext}'
                    with open(sub_bin_file, 'rb') as sub:
                        f.write(sub.read())

    postprocessing_time = (time.time() - start_time) / files_len

    with open(args.dest+'_avg_evl.txt', 'w') as f:
        lines = [f'Geo-CNN execution time\n\n',
                 f'Pre-processing time (sec)   : {preprocessing_time}\n',
                 f'Model loading time (sec)    : {load_model_time}\n',
                 f'avg. Encoding time (sec)    : {enc_time}\n',
                 f'avg. Decoding time (sec)    : {dec_time}\n',
                 f'Post-processing time (sec)  : {postprocessing_time}\n',
                 '===============================================\n',
                 f'stdev. Encoding time (sec)  : {std_enc_time}\n',
                 f'stdev. Decoding time (sec)  : {std_dec_time}\n',
                 '===============================================\n\n']
        f.writelines(lines)
    return 0

def evaluate_geocnn(path, args):
    sys.path.append('../../evaluator')
    from evaluate_pc import evaluate

    path, _ = splitext(path) # get the file path without extension
    source_path = join(args.source, path+'.ply')
    bin_path = join(args.dest, 'bin', path+'.ply.bin')
    evl_path = join(args.dest, 'evl', path+'.log')
    rescale_path = join(args.dest, 'rescale', path+'.ply.bin.ply')
    evl_folder, _ = split(evl_path)
    makedirs(evl_folder, exist_ok=True)
    evaluate(source_path, bin_path, rescale_path, evl_path)

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'source', 
        help='Source point cloud directory.')
    parser.add_argument(
        'dest', 
        help='Directory for compressed bitstream/decompressed point cloud/evaluation log')
    parser.add_argument(
        'checkpoint_dir',
        help='Directory where to load model checkpoints.')
    parser.add_argument(
        '--batch_size', type=int, default=1,
        help='Batch size.')
    parser.add_argument(
        '--read_batch_size', type=int, default=1,
        help='Batch size for parallel reading.')
    parser.add_argument(
        '--resolution', type=int, default=64,
        help='Scale to which voxel resolution.')
    parser.add_argument(
        '--num_filters', type=int, default=32,
        help='Number of filters per layer.')
    parser.add_argument(
        '--preprocess_threads', type=int, default=16,
        help='Number of CPU threads to use for parallel decoding.')
    parser.add_argument(
        '--output_extension', default='.ply',
        help='Output extension.')
    parser.add_argument(
        '--divide_oct', type=int, default=0,
        help='Divide into 8 sub point cloud to prevent the bugs in tf.Conv3D(). (default: 0)')
        ## ref: https://github.com/tensorflow/tensorflow/issues/25760 ##

    args = parser.parse_args()

    assert os.path.exists(args.source), f'{args.source} does not exist'
    # assert not os.path.exists(args.dest), f'{args.dest} already exists'

    work(args)

    ### Evaluate ###
    paths = glob(join(args.source, '**', 'test', '*.ply'), recursive=True)
    files = [x[len(args.source) + 1:] for x in paths]
    files_len = len(files)
    assert files_len > 0

    with Pool() as p:
        evaluate_geocnn_f = functools.partial(evaluate_geocnn, args=args)
        list(tqdm(p.imap(evaluate_geocnn_f, files), total=files_len))

    ## Statisticize ##
    sp.call(['python', '../../evaluator/cal_avg_std.py', join(args.dest, 'evl')], stdout=sp.DEVNULL)
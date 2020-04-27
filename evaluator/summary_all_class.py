#Process level parallelism for shell commands
import os
from os.path import join, basename, split, splitext
import sys
import re
import numpy as np
from os import makedirs
from glob import glob
import logging
import argparse
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

def work(path, args):

    log_files = glob(join(args.log_dir, '**', '*.log'), recursive=True)

    enc_t=[]
    dec_t=[]
    mse=[]
    psnr=[]
    hausdorff=[]
    h_psnr=[]
    cd=[]
    emd=[]
    bin_size=[]
    comp_ratio=[]

    for log in log_files:
        with open(log, 'r') as f:
            for line in f:
                m = re.search('(?<=avg. Encoding time          : ).*', line)
                if(m):
                    enc_t.append(float(m.group()))
                m = re.search('(?<=avg. Decoding time          : ).*', line)
                if(m):
                    dec_t.append(float(m.group()))
                m = re.search('(?<=avg. MSE                    : ).*', line)
                if(m):
                    mse.append(float(m.group()))
                m = re.search('(?<=avg. PSNR                   : ).*', line)
                if(m):
                    psnr.append(float(m.group()))
                m = re.search('(?<=avg. Hausdorff distance     : ).*', line)
                if(m):
                    hausdorff.append(float(m.group()))
                m = re.search('(?<=avg. H. PSNR                : ).*', line)
                if(m):
                    h_psnr.append(float(m.group()))
                m = re.search('(?<=avg. Chamfer distance       : ).*', line)
                if(m):
                    cd.append(float(m.group()))
                m = re.search('(?<=avg. Earth Mover\'s distance : ).*', line)
                if(m):
                    emd.append(float(m.group()))
                m = re.search('(?<=avg. bin_file size \(kB\)   : ).*', line)
                if(m):
                    bin_size.append(float(m.group()))
                m = re.search('(?<=avg. compression ratio      : ).*', line)
                if(m):
                    comp_ratio.append(float(m.group()))

    summary_path = join(args.log_dir, 'summary.md')
    with open(summary_path, 'w') as summary:
        lines = [f'Point Cloud Compression Evaluation\n\n',
                 f'Summary for all classes\n\n',
                 f'avg. Encoding time          : {np.mean(enc_t)}\n',
                 f'avg. Decoding time          : {np.mean(dec_t)}\n\n',
                 f'avg. MSE                    : {np.mean(mse)}\n',
                 f'avg. PSNR                   : {np.mean(psnr)}\n',
                 f'avg. Hausdorff distance     : {np.mean(hausdorff)}\n',
                 f'avg. H. PSNR                : {np.mean(h_psnr)}\n',
                 f'avg. Chamfer distance       : {np.mean(cd)}\n',
                 f'avg. Earth Mover\'s distance : {np.mean(emd)}\n',
                 f'avg. bin_file size (kB)     : {np.mean(bin_size)}\n',
                 f'avg. compression ratio      : {np.mean(comp_ratio)}\n\n',
                 f'stdev. of Encoding time          : {np.std(enc_t)}\n',
                 f'stdev. of Decoding time          : {np.std(dec_t)}\n\n',
                 f'stdev. of MSE                    : {np.std(mse)}\n',
                 f'stdev. of PSNR                   : {np.std(psnr)}\n',
                 f'stdev. of Hausdorff distance     : {np.std(hausdorff)}\n',
                 f'stdev. of H. PSNR                : {np.std(h_psnr)}\n',
                 f'stdev. of Chamfer distance       : {np.std(cd)}\n',
                 f'stdev. of Earth Mover\'s distance : {np.std(emd)}\n',
                 f'stdev. of bin_file size (kB)     : {np.std(bin_size)}\n',
                 f'stdev. of compression ratio      : {np.std(comp_ratio)}\n',]
        summary.writelines(lines)
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('log_dir', help='Evaluation log directory.')
    args = parser.parse_args()

    paths = glob(join(args.log_dir, '**', 'test'), recursive=True)
    class_paths = [x[len(args.log_dir) + 1:] for x in paths]
    paths_len = len(class_paths)
    assert paths_len > 0
    
    # for class_path in tqdm(class_paths):
    work(class_paths, args)
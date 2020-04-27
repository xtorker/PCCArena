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

    class_name, _ = split(path)
    log_files = glob(join(path, '**', '*.log'), recursive=True)

    enc_t=[]
    dec_t=[]
    acd_p2pt=[]
    cd_p2pt=[]
    cdpsnr_p2pt=[]
    hausdorff_p2pt=[]
    acd_p2pl=[]
    cd_p2pl=[]
    cdpsnr_p2pl=[]
    hausdorff_p2pl=[]
    emd=[]
    bin_size=[]
    compress_ratio=[]
    bpp=[]

    for log in log_files:
        with open(log, 'r') as f:
            for line in f:
                m = re.search('(?<=Encoding time \(sec\)    : ).*', line)
                if(m):
                    enc_t.append(float(m.group()))
                m = re.search('(?<=Decoding time \(sec\)    : ).*', line)
                if(m):
                    dec_t.append(float(m.group()))
                m = re.search('(?<=Asym. Chamfer dist. \(1->2\) p2pt: ).*', line)
                if(m):
                    acd_p2pt.append(float(m.group()))
                m = re.search('(?<=Chamfer dist.              p2pt: ).*', line)
                if(m):
                    cd_p2pt.append(float(m.group()))
                m = re.search('(?<=CD-PSNR                    p2pt: ).*', line)
                if(m):
                    cdpsnr_p2pt.append(float(m.group()))
                m = re.search('(?<=Hausdorff distance         p2pt: ).*', line)
                if(m):
                    hausdorff_p2pt.append(float(m.group()))
                m = re.search('(?<=Asym. Chamfer dist. \(1->2\) p2pl: ).*', line)
                if(m):
                    acd_p2pl.append(float(m.group()))
                m = re.search('(?<=Chamfer dist.              p2pl: ).*', line)
                if(m):
                    cd_p2pl.append(float(m.group()))
                m = re.search('(?<=CD-PSNR                    p2pl: ).*', line)
                if(m):
                    cdpsnr_p2pl.append(float(m.group()))
                m = re.search('(?<=Hausdorff distance         p2pl: ).*', line)
                if(m):
                    hausdorff_p2pl.append(float(m.group()))
                m = re.search('(?<=Earth Mover\'s dist.            : ).*', line)
                if(m):
                    emd.append(float(m.group()))
                m = re.search('(?<=bin_file size \(kB\)  : ).*', line)
                if(m):
                    bin_size.append(float(m.group()))
                m = re.search('(?<=compression ratio   : ).*', line)
                if(m):
                    compress_ratio.append(float(m.group()))
                m = re.search('(?<=bpp \(bits per point\): ).*', line)
                if(m):
                    bpp.append(float(m.group()))

    avg_log_path = class_name+'_avg_evl.txt'

    with open(avg_log_path, 'w') as avg_log:
        lines = [f'Point Cloud Compression Evaluation\n\n',
                 f'Log directory: {class_name}\n\n',
                 f'avg. Encoding time                    : {np.mean(enc_t)}\n',
                 f'avg. Decoding time                    : {np.mean(dec_t)}\n',
                 f'========================================================\n',
                 f'avg. Asym. Chamfer dist. (1->2)   p2pt: {np.mean(acd_p2pt)}\n',
                 f'avg. Chamfer dist.                p2pt: {np.mean(cd_p2pt)}\n',
                 f'avg. CD-PSNR                      p2pt: {np.mean(cdpsnr_p2pt)}\n',
                 f'avg. Hausdorff dist.              p2pt: {np.mean(hausdorff_p2pt)}\n',
                 f'========================================================\n',
                 f'avg. Asym. Chamfer dist. (1->2)   p2pl: {np.mean(acd_p2pl)}\n',
                 f'avg. Chamfer dist.                p2pl: {np.mean(cd_p2pl)}\n',
                 f'avg. CD-PSNR                      p2pl: {np.mean(cdpsnr_p2pl)}\n',
                 f'avg. Hausdorff dist.              p2pl: {np.mean(hausdorff_p2pl)}\n',
                 f'========================================================\n',
                 f'avg. Earth Mover\'s distance           : {np.mean(emd)}\n',
                 f'========================================================\n',
                 f'avg. bin_file size (kB)               : {np.mean(bin_size)}\n',
                 f'avg. compression ratio                : {np.mean(compress_ratio)}\n',
                 f'avg. bpp (bits per point)             : {np.mean(bpp)}\n\n\n',

                 f'stdev. of Encoding time               : {np.std(enc_t)}\n',
                 f'stdev. of Decoding time               : {np.std(dec_t)}\n',
                 f'========================================================\n',
                 f'stdev. Asym. Chamfer dist. (1->2) p2pt: {np.std(acd_p2pt)}\n',
                 f'stdev. Chamfer dist.              p2pt: {np.std(cd_p2pt)}\n',
                 f'stdev. CD-PSNR                    p2pt: {np.std(cdpsnr_p2pt)}\n',
                 f'stdev. Hausdorff dist.            p2pt: {np.std(hausdorff_p2pt)}\n',
                 f'========================================================\n',
                 f'stdev. Asym. Chamfer dist. (1->2) p2pl: {np.std(acd_p2pl)}\n',
                 f'stdev. Chamfer dist.              p2pl: {np.std(cd_p2pl)}\n',
                 f'stdev. CD-PSNR                    p2pl: {np.std(cdpsnr_p2pl)}\n',
                 f'stdev. Hausdorff dist.            p2pl: {np.std(hausdorff_p2pl)}\n',
                 f'========================================================\n',
                 f'stdev. Earth Mover\'s distance         : {np.std(emd)}\n',
                 f'========================================================\n',
                 f'stdev. bin_file size (kB)             : {np.std(bin_size)}\n',
                 f'stdev. compression ratio              : {np.std(compress_ratio)}\n',
                 f'stdev. bpp (bits per point)           : {np.std(bpp)}']
        avg_log.writelines(lines)
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('log_dir', help='Evaluation log directory.')
    args = parser.parse_args()

    paths = glob(join(args.log_dir, '**', 'test'), recursive=True)
    paths_len = len(paths)
    assert paths_len > 0
    
    # per class
    for class_path in tqdm(paths):
        work(class_path, args)
    
    # summary all
    work(args.log_dir, args)

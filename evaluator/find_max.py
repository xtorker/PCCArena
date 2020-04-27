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
    # log_files = glob(join(path, '*_pc500k_0-1_random100_vg*_avg_evl.txt'), recursive=True)
    print(len(log_files))
    enc_t=[]
    dec_t=[]
    pre_t=[]
    post_t=[]

    for log in log_files:
        with open(log, 'r') as f:
            for line in f:
                m = re.search('(?<=Encoding time \(sec\)    : ).*', line)
                if(m):
                    enc_t.append(float(m.group()))
                m = re.search('(?<=Decoding time \(sec\)    : ).*', line)
                if(m):
                    dec_t.append(float(m.group()))
                # m = re.search('(?<=avg. Encoding time \(sec\)    : ).*', line)
                # if(m):
                #     enc_t.append(float(m.group()))
                # m = re.search('(?<=avg. Decoding time \(sec\)    : ).*', line)
                # if(m):
                #     dec_t.append(float(m.group()))
                # m = re.search('(?<=Pre-processing time \(sec\)   : ).*', line)
                # if(m):
                #     pre_t.append(float(m.group()))
                # m = re.search('(?<=Post-processing time \(sec\)  : ).*', line)
                # if(m):
                #     post_t.append(float(m.group()))

    # avg_log_path = class_name+'_max_encT_decT.txt'
    avg_log_path = class_name+'_max_preT_postT.txt'

    # with open('max_encT_decT.txt', 'w') as avg_log:
    #     lines = [f'Point Cloud Compression Evaluation\n\n',
    #              f'Log directory: {class_name}\n\n',
    #              f'max. Encoding time                    : {np.max(enc_t)}\n',
    #              f'max. Decoding time                    : {np.max(dec_t)}\n']
    #             #  f'avg. Encoding time                    : {np.mean(enc_t)}\n',
    #             #  f'avg. Decoding time                    : {np.mean(dec_t)}\n',
    #             #  f'max. Pre-processing time                    : {np.max(pre_t)}\n',
    #             #  f'max. Post-processing time                    : {np.max(post_t)}\n',
    #             #  f'avg. Pre-processing time                    : {np.mean(pre_t)}\n',
    #             #  f'avg. Post-processing time                    : {np.mean(post_t)}\n']
    #     avg_log.writelines(lines)

    print(f'max. Enc. T: {np.max(enc_t)}')
    print(f'max. Dec. T: {np.max(dec_t)}')
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('log_dir', help='Evaluation log directory.')
    args = parser.parse_args()

    work(args.log_dir, args)

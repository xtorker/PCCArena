import os
import sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'Chamfer-Distance-API'))
import chamfer_distance_api
from pyemd import emd_samples
import numpy as np
import subprocess as sp
import tensorflow as tf
import re
import logging
import argparse
from plyfile import PlyData, PlyElement


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

def evaluate(ori_path, bin_path, dec_path, log_path):
    ### mse, psnr, hausdorff, h.psnr ###
    pc_error = sp.run([os.path.join(BASE_DIR, 'pc_error/build/pc_error'), '-a', ori_path, '-b', dec_path, '-d'], 
                        stdout=sp.PIPE, universal_newlines=True)
    for line in pc_error.stdout.splitlines():
        m = re.search('(?<=mseF      \(p2point\): ).*', line)
        if (m):
            mse = m.group()
        m = re.search('(?<=mseF,PSNR \(p2point\): ).*', line)
        if (m):
            psnr = m.group()
        m = re.search('(?<=h.        \(p2point\): ).*', line)
        if (m):
            hausdorff = m.group()
        m = re.search('(?<=h.,PSNR   \(p2point\): ).*', line)
        if (m):
            h_psnr = m.group()

    # for line in pc_error.stdout.splitlines():
    #     m = re.search('(?<=mse2      \(p2point\): ).*', line)
    #     if (m):
    #         mse = m.group()
    #     m = re.search('(?<=mse2,PSNR \(p2point\): ).*', line)
    #     if (m):
    #         psnr = m.group()
    #     m = re.search('(?<=h.       2\(p2point\): ).*', line)
    #     if (m):
    #         hausdorff = m.group()
    #     m = re.search('(?<=h.,PSNR  2\(p2point\): ).*', line)
    #     if (m):
    #         h_psnr = m.group()

    ### Chamfer distance, EMD ###
    ori_ply = PlyData.read(ori_path)
    ori_pc = np.array([ori_ply['vertex']['x'], ori_ply['vertex']['y'], ori_ply['vertex']['z']])
    ori_pc = np.transpose(ori_pc)
    ori_pc = np.expand_dims(ori_pc, axis=0)

    dec_ply = PlyData.read(dec_path)
    dec_pc = np.array([dec_ply['vertex']['x'], dec_ply['vertex']['y'], dec_ply['vertex']['z']])
    dec_pc = np.transpose(dec_pc)
    dec_pc = np.expand_dims(dec_pc, axis=0)

    cd_api = chamfer_distance_api.Chamfer_distance()
    cd = cd_api.get_chamfer_distance(ori_pc, dec_pc)
    emd = emd_samples(ori_pc, dec_pc)

    ### compressed file size ###
    bin_size = (os.stat(bin_path).st_size)/1000 # kB

    with open(log_path, 'a') as f:
        lines = [f'Point Cloud Compression Evaluation\n\n',
                 f'ply1: {ori_path}\n',
                 f'ply2: {dec_path}\n\n',
                 f'MSE                    : {mse}\n',
                 f'PSNR                   : {psnr}\n',
                 f'Hausdorff distance     : {hausdorff}\n',
                 f'H. PSNR                : {h_psnr}\n',
                 f'Chamfer distance       : {cd}\n',
                 f'Earth Mover\'s distance : {emd}\n\n',
                 f'bin_file size (kB)  : {bin_size}\n']
        f.writelines(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('ori_path', help='Path to ground turth point cloud')
    parser.add_argument('bin_path', help='Path to compressed bin_file')
    parser.add_argument('dec_path', help='Path to decompressed point cloud')
    parser.add_argument('log_path', help='Path to evaluation results log')

    args = parser.parse_args()

    assert os.path.exists(args.ori_path), f'{args.ori_path} does not exist'
    assert os.path.exists(args.dec_path), f'{args.dec_path} does not exist'
    assert not os.path.exists(args.log_path), f'{args.log_path} already exists'

    evaluate(args.ori_path, args.bin_path, args.dec_path, args.log_path)
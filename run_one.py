import subprocess as sp
import os
from os.path import join, abspath
import time
CWD = os.getcwd()
CPUs = str(os.cpu_count())

def run_one(source_path, args):
    codingParameters = []
    while(len(codingParameters) < args.M){
        C = (args.Cmin + args.Cmax) / 2


        if args.alg == 'pcl':
            pcl(source_path, args, C)
            bpp = parse_bpp(f'{args.dest}/{args.dataset}_octreeRes{octreeRes}/evl')
        elif args.alg == 'draco':
            draco(source_path, args, C)
            bpp = parse_bpp(f'{args.dest}/{args.dataset}_qp{qp}/evl')
        elif args.alg == 'gpcc':
            draco(source_path, args, C)
            bpp = parse_bpp(f'{args.dest}/{args.dataset}_sf{scale_factor}/evl')
        elif args.alg == 'geocnn':
            draco(source_path, args, C)
            bpp = parse_bpp(f'{args.dest}/{args.dataset}_vg{resolution}/evl')
        else:
            print('Undefined algorithm')
            break


        if (bpp < args.Bmin or bpp > args.Bmax):
            continue
        else if bpp - args.Bmin < (args.Bmin + args.Bmax) / 2:
            codingParameters.append((args.Cmin + C) / 2)
        else:
            codingParameters.append((C + args.Cmax) / 2)
    }

def pcl(source_path, args, octreeRes):
    ############################################
    # PCL Compression
    # octreeRes: Quantization bits for the position attribute.
    ############################################
    pcl_script = 'run_pcl.py'
    pcl_wd = 'algorithms/PCL_compression'

    sp.run(['python', pcl_script,
            source_path, f'{args.dest}/{args.dataset}_octreeRes{octreeRes}',
            octreeRes], cwd=pcl_wd)

def draco(source_path, args, qp):
    # ############################################
    # # Draco
    # # qp: Quantization bits for the position attribute.
    # # cl: Compression level [0-10], most=10, least=0.
    # ############################################
    draco_script = 'run_draco.py'
    draco_wd = 'algorithms/draco'
    cl = str(10)

    sp.run(['python', draco_script,
            source_path, f'{args.dest}/{args.dataset}_qp{qp}',
            '--qp', qp,
            '--cl', cl], cwd=draco_wd)

def gpcc(source_path, args, scale_factor):
    # ############################################
    # # G-PCC tmc13
    # # scale_factor: Scale factor to be applied to point positions during quantization process.
    # #               (Prior to encoding, scale the point cloud geometry by multiplying each 
    # #               co-ordinate by the real FACTOR and rounding to integer precision. 
    # #               The scale factor is written to the bitstream and a decoder may use it 
    # #               to provide output at the original scale.)
    # # merge: Drop the duplicate points during voxelization. (0: false, 1: true)
    # ############################################
    tmc13_script = 'run_tmc13.py'
    tmc13_wd = 'algorithms/mpeg-pcc-tmc13-v6'
    merge = '1'

    sp.run(['python', tmc13_script,
            source_path, f'{args.dest}/{args.dataset}_sf{scale_factor}',
            '--scale_factor', scale_factor,
            '--merge', merge], cwd=tmc13_wd)

def geocnn(source_path, args, resolution):
    ############################################
    # Geo-CNN
    # resolution: Scale to which voxel resolution.
    # divide_oct: Divide to 8 sub point cloud. (0: false, 1: true)
    ############################################
    geocnn_script = 'run_geo_cnn.py'
    geocnn_wd = 'algorithms/pcc_geo_cnn'
    model_path = 'models/ModelNet40_vox64_00001'
    divide_oct = '0'

    sp.run(['python', geocnn_script,
            source_path, f'{args.dest}/{args.dataset}_vg{resolution}', model_path,
            '--resolution', resolution,
            '--preprocess_threads', CPUs,
            '--divide_oct', divide_oct], cwd=geocnn_wd)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('dataset', help='Source point cloud directory.')
    parser.add_argument('dest', help='Directory for compressed bitstream/decompressed point cloud/evaluation log')
    parser.add_argument('alg', help='Algorithm for evaluation. (pcl, draco, gpcc, geocnn)')
    parser.add_argument('--Bmin', type=float,
                        help='Minimum bpp.')
    parser.add_argument('--Bmax', type=float,
                        help='Maximum bpp.')
    parser.add_argument('--Cmin', type=float,
                        help='Corresponding minimum coding parameter of Bmin.')
    parser.add_argument('--Cmax', type=float,
                        help='Corresponding maximum coding parameter of Bmax.')
    parser.add_argument('--M', type=int, default=4,
                        help='Target number of R-D samples.')

    args = parser.parse_args()

    assert os.path.exists(args.source), f'{args.source} does not exist'
    # assert not os.path.exists(args.dest), f'{args.dest} already exists'

    source_path = abspath(join('datasets', dataset))

    run_one(source_path, args)
import re
from pathlib import Path
import subprocess as sp

from pyntcloud import PyntCloud

from _version import __version__
from utils.processing import execute_cmd

def log_initializer(ref_pc, target_pc, log_path):
    lines = [
        f'PCC-Arena Evaluator {__version__}\n',
        f'ref_pc: {ref_pc}',
        f'target_pc: {target_pc}',
    ]
    with open(log_path, 'w') as f:
        f.writelines(lines)

def log_time_and_filesize(pre_t, enc_t, dec_t, post_t, src_pcfile, bin_files):

    cloud = PyntCloud.from_file(src_pcfile)
    num_points = len(cloud.points['x'])

    src_pcfile_size = Path(src_pcfile).stat().st_size / 1000 # kB
    total_bin_size = sum(Path(bin_f).stat().st_size for bin_f in bin_files) / 1000 # kB
    compression_ratio = total_bin_size / src_pcfile_size # kB
    bpp = (total_bin_size * 1000 * 8) / num_points

    lines = [
        f"========== Time & Binary Size =========="
        f"Pre-processing time:          {pre_time:0.4f}",
        f"Encoding time:                {enc_time:0.4f}",
        f"Decoding time:                {dec_time:0.4f}",
        f"Post-processing time:         {post_time:0.4f}",
        f"Source point cloud size (kB): {}",
        f"Total binary files size (kB): {total_size}",
        f"bpp (bits per point):         {bpp}"
    ]

    with open(evl_log, 'w') as f:
        f.writelines(lines)

def objective_quality(ref_pc, target_pc, color=0, resolution=1024):
    ret = pc_error_wrapper(ref_pc, target_pc, color, resolution)
    
    chosen_metrics = [
        'ACD1      \(p2point\): ',
        'ACD1      \(p2plane\): ',
        'ACD2      \(p2point\): ',
        'ACD2      \(p2plane\): ',
        'CD        \(p2point\): ',
        'CD,PSNR   \(p2point\): ',
        'CD        \(p2plane\): ',
        'CD,PSNR   \(p2plane\): ',
        'h.        \(p2point\): ',
        'h.,PSNR   \(p2point\): ',
        'h.        \(p2plane\): ',
        'h.,PSNR   \(p2plane\): ',
        'c\[0\],PSNRF         : ',
        'c\[1\],PSNRF         : ',
        'c\[2\],PSNRF         : ',
        'hybrid geo-color   : '
    ]

    for metric in chosen_metrics:
        for line in ret.splitlines():
            if
        

    ret.find(list[])

def pc_error_wrapper(ref_pc, target_pc, color=0, resolution=1024):
    '''
    Wrapper of the metric software, modified based on mpeg-pcc-dmetric.

    Parameters:
        ref_pc (str or PosixPath): Reference (source) point cloud.
        target_pc (str or PosixPath): Target (reconstructed/decoded) point cloud.
    
    Optionals:
        color (int): Calculate color distortion or not. (0: false, 1: true)
        resolution (int): Resolution (scale) of the point cloud.
    
    Returns:
        string : Logs of objective quality.
    '''

    # metric software modified based on mpeg-pcc-dmetric
    evl_bin = Path(__file__).parent.joinpath("mpeg-pcc-dmetric-master/test/pc_error").resolve()

    cmd = [
        evl_bin,
        f'--fileA={ref_pc}',
        f'--fileB={target_pc}',
        f'--color={color}',
        f'--resolution={resolution}',
        '--hausdorff=1'
    ]

    ret = sp.run(cmd, stdout=sp.PIPE, stderr=sp.DEVNULL, universal_newlines=True)

    return ret.stdout
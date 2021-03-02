
from utils.processing import execute_cmd

def evaluate(
        ref_pc,
        target_pc,
        log_file=None,
        color=0,
        resolution=1024
    ):
    '''
    Wrapper of the metric software, modified based on mpeg-pcc-dmetric.

    Parameters:
        ref_pc (str or PosixPath): Reference (source) point cloud.
        target_pc (str or PosixPath): Target (reconstructed/decoded) point cloud.
    
    Optionals:
        log_file (str or PosixPath): Log file. (default will write to stdout)
        color (int): Calculate color distortion or not. (0: false, 1: true)
        resolution (int): Resolution (scale) of the point cloud.
    
    Returns:
        list (PosixPath): Files that match the glob pattern.
    '''


    # if log_file is None, print to stdout instead
    
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

    assert execute_cmd(cmd)
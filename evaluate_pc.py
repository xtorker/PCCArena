import argparse
import logging.config

import open3d as o3d
from xvfbwrapper import Xvfb

from utils.file_io import get_logging_config
from evaluator.evaluator import Evaluator

def evaluate_pc(args):
    o3d_vis = o3d.visualization.Visualizer()
    evaluator = Evaluator(
        args.ref_pc,
        args.target_pc,
        o3d_vis=o3d_vis
    )
    ret = evaluator.evaluate()
    print(ret)
    
if __name__ == '__main__':
    LOGGING_CONFIG = get_logging_config('utils/logging.conf')
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(
        description="Wrapper for user to evaluate point clouds.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        'ref_pc',
        help="The reference point cloud. Use point cloud with normal "
             "to calculate the p2plane metrics."
    )
    parser.add_argument(
        'target_pc',
        help="The target point cloud."
    )
    parser.add_argument(
        '--color',
        type=bool,
        default=False,
        help="True for calculating color metric, false otherwise."
    )
    parser.add_argument(
        '--resolution',
        type=int,
        default=None,
        help="Maximum NN distance of the ``ref_pc``. If the resolution "
             "is not specified, it will be calculated on the fly."
    )
    
    args = parser.parse_args()
    
    disp = Xvfb()
    disp.start()
    evaluate_pc(args)
    disp.stop()
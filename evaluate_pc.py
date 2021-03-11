import argparse
import logging.config

from utils.file_io import get_logging_config
from evaluator.metrics import ViewIndependentMetrics

def evaluate_pc(args):
    VIMetrics = ViewIndependentMetrics()
    ret = VIMetrics.evaluate(
        args.ref_pc, args.target_pc, 
        color=args.color, resolution=args.resolution
    )
    print(ret)
    
if __name__ == '__main__':
    LOGGING_CONFIG = get_logging_config('logging.conf')
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
        type=int,
        default=0,
        help="1 for calculating color metric, 0 otherwise."
    )
    parser.add_argument(
        '--resolution',
        type=int,
        default=None,
        help="Maximum NN distance of the ``ref_pc``. If the resolution "
             "is not specified, it will be calculated on the fly."
    )
    
    args = parser.parse_args()
    
    evaluate_pc(args)
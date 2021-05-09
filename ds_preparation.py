import logging
import argparse
import logging.config
from pathlib import Path
from functools import partial
from multiprocessing import Pool

from tqdm import tqdm

from utils.file_io import glob_file
from utils.processing import parallel
from utils.file_io import get_logging_config
from utils.pc_utils import paint_uni_color_on_pc

def from_mesh_ds():
    pass
def from_pc_ds():
    pass

def work():
    pass


if __name__ == '__main__':
    LOGGING_CONFIG = get_logging_config('utils/logging.conf')
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(
        description="Script to generate point cloud datasets.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        'src_dir',
        help=""
    )
    parser.add_argument(
        'dest_dir',
        help=""
    )
    parser.add_argument(
        'glob_pattern',
        help=""
    )
    parser.add_argument(
        '-c',
        '--color',
        nargs='+',
        help=""
    )
    args = parser.parse_args()
    
    files = glob_file(args.src_dir, args.glob_pattern, verbose=True)
    pfunc = partial(
        paint_uni_color_on_pc,
        src_dir=args.src_dir,
        dest_dir=args.dest_dir,
        color=args.color
    )
    
    parallel(pfunc, files)
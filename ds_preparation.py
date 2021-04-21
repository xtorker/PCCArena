import logging
import argparse
from pathlib import Path
from functools import partial
from multiprocessing import Pool

from tqdm import tqdm

from utils.file_io import get_logging_config

def from_mesh_ds():

def from_pc_ds():

def work():
    return


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
        'dest_dir',
        help=""
    )
    parser.add_argument(
        'dest_dir',
        help=""
    )
    parser.add_argument(
        'dest_dir',
        help=""
    )
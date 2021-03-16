import re
import getpass
import argparse
import fileinput
import logging.config
from pathlib import Path

from utils.file_io import get_logging_config, glob_file

def find_and_replace(filename, pattern, string):
    for line in fileinput.input(filename, inplace=True):
        print(re.sub(f'(?<={pattern}).*', string, line), end='')

def setup_config(args):
    algs_cfg_files = glob_file(
        'cfgs/algs', '*.yml', fullpath=True, verbose=True
    )
    ds_cfg_file = 'cfgs/datasets.yml'

    # Set dataset root directory
    find_and_replace(
        ds_cfg_file, 'ds_rootdir: &ds_rootdir ', args.ds_rootdir
    )
    
    for cfg in algs_cfg_files:
        # If the PCC algorithm have specified environments setup, set 
        # the python path to corresponding conda environments.
        find_and_replace(
            str(cfg), 'python: ',
            f"/home/{getpass.getuser()}/anaconda3/envs/{Path(cfg).stem}/bin/python"
        )
    


if __name__ == '__main__':
    LOGGING_CONFIG = get_logging_config('logging.conf')
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(
        description="Setup the experiment environments, including conda env., "
                    "compile binaries, setup config files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        'ds_rootdir',
        help="root directory of the datasets."
    )

    args = parser.parse_args()
    
    setup_config(args)
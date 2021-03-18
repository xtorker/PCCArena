import os
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
    Path(args.ds_rootdir).mkdir(parents=True, exist_ok=True)
    
    isDefaultPath = (args.ds_rootdir == 'datasets')
    if isDefaultPath:
        pass
    else:
        os.symlink(args.ds_rootdir, 'datasets')

    Path(args.exp_rootdir).mkdir(parents=True, exist_ok=True)
    
    isDefaultPath = (args.exp_rootdir == 'experiments')
    if isDefaultPath:
        pass
    else:
        os.symlink(args.exp_rootdir, 'experiments')
    
    algs_cfg_files = glob_file(
        'cfgs/algs', '*.yml', fullpath=True, verbose=True
    )
    ds_cfg_file = 'cfgs/datasets.yml'

    # Set dataset root directory
    find_and_replace(
        ds_cfg_file, 'ds_rootdir: &ds_rootdir ', 
        f'{Path(args.ds_rootdir).resolve()}/'
    )
    
    for cfg in algs_cfg_files:
        # Set root directory for each PCC algorithms
        find_and_replace(
            str(cfg), 'rootdir: ', 
            str(Path(__file__).parent.resolve()
                .joinpath(f'algs/{Path(cfg).stem}'))
        )
        # If the PCC algorithm have specified environments setup, also set 
        # the python path to corresponding conda environments.
        find_and_replace(
            str(cfg), 'python: ',
            f"/home/{getpass.getuser()}/anaconda3/envs/"
            + f"{Path(cfg).stem}/bin/python"
        )
    


if __name__ == '__main__':
    LOGGING_CONFIG = get_logging_config('utils/logging.conf')
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(
        description="Setup the experiment environments, including conda env., "
                    "compile binaries, setup config files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--ds_rootdir',
        type=str,
        help="root directory of the datasets.",
        default='datasets'
    )
    parser.add_argument(
        '--exp_rootdir',
        type=str,
        help="root directory of the experiments data.",
        default='experiments'
    )

    args = parser.parse_args()
    
    setup_config(args)
    
    logger.info("Setup completed.")
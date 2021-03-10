import re
import fileinput
import logging.config
from pathlib import Path

import yaml
import GPUtil

from utils.file_io import get_logging_config
from algs_wrapper.draco import Draco
from algs_wrapper.geocnn_v2 import GeoCNNv2

from evaluator.metrics import MetricLogger

def main():
    LOGGING_CONFIG = get_logging_config('logging.conf')
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)

    draco = Draco('r7')
    draco.run_dataset('Test_SNCC', 'experiments/draco/Test_SNCC')
    
    geocnn_v2 = GeoCNNv2('r4')
    geocnn_v2.run_dataset('Test_SNC', 'experiments/geocnn_v2/Test_SNCC', use_gpu=True)

if __name__ == '__main__':
    main()

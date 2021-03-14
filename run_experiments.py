import logging.config

from utils.file_io import get_logging_config
from algs_wrapper.gpcc import GPCC
from algs_wrapper.draco import Draco
from algs_wrapper.pcgc_v1 import PCGCv1
from algs_wrapper.pcgc_v2 import PCGCv2
from algs_wrapper.geocnn_v2 import GeoCNNv2

def main():
    LOGGING_CONFIG = get_logging_config('logging.conf')
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)

    # [TODO]
    # change 'experiments/draco/Test_SNC' to 'experiments'
    # assign the directory in the base.py

    draco = Draco()
    # draco.rate = 'r1'
    # draco.run_dataset('Test_SNC', 'experiments/draco/Test_SNC')
    for rate in range(8):
       draco.rate = f'r{rate+1}'
       draco.run_dataset('SNC', 'experiments/draco/SNC')
       draco.run_dataset('SNCC', 'experiments/draco/SNCC')
    
    gpcc = GPCC()
    # gpcc.rate = 'r1'
    # gpcc.run_dataset('Test_SNC', 'experiments/gpcc/Test_SNC')
    for rate in range(8):
        gpcc.rate = f'r{rate+1}'
        gpcc.run_dataset('SNC', 'experiments/gpcc/SNC')
        gpcc.run_dataset('SNCC', 'experiments/gpcc/SNCC')
    
    pcgc_v1 = PCGCv1()
    # pcgc_v1.rate = 'r1'
    # pcgc_v1.run_dataset('Test_SNC', 'experiments/pcgc_v1/Test_SNC')
    # for rate in range(6):
    #     pcgc_v1.rate = f'r{rate+1}'
    #     pcgc_v1.run_dataset('SNC', 'experiments/pcgc_v1/SNC', use_gpu=True)
    
    pcgc_v2 = PCGCv2()
    pcgc_v2.rate = 'r1'
    pcgc_v2.run_dataset('Test_SNC', 'experiments/pcgc_v2/Test_SNC')
    # for rate in range(4):
    #     pcgc_v2.rate = f'r{rate+1}'
    #     pcgc_v2.run_dataset('SNC', 'experiments/pcgc_v2/SNC')


if __name__ == '__main__':
    main()

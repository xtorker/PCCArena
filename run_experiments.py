import logging.config

from utils.file_io import get_logging_config
from algs_wrapper.Draco import Draco
from algs_wrapper.GPCC import GPCC
from algs_wrapper.VPCC import VPCC
from algs_wrapper.GeoCNNv1 import GeoCNNv1
from algs_wrapper.GeoCNNv2 import GeoCNNv2
from algs_wrapper.PCGCv1 import PCGCv1
from algs_wrapper.PCGCv2 import PCGCv2

def main():
    LOGGING_CONFIG = get_logging_config('utils/logging.conf')
    logging.config.dictConfig(LOGGING_CONFIG)

    # GPCC/SNCC/r4 start

    # draco = Draco()
    # for rate in range(8):
    #    draco.rate = f'r{rate+1}'
    #    draco.run_dataset('Debug_SNC', 'experiments')
    #    draco.run_dataset('Debug_SNCC', 'experiments')
    
    # gpcc = GPCC()
    # for rate in range(5):
    #     gpcc.rate = f'r{rate+4}'
    #     # gpcc.run_dataset('Debug_SNC', 'experiments')
    #     # gpcc.run_dataset('Debug_SNCC', 'experiments')
    #     gpcc.run_dataset('SNC', 'experiments')
    #     gpcc.run_dataset('SNCC', 'experiments')

    # vpcc = VPCC()
    # for rate in range(5):
    #     vpcc.rate = f'r{rate+1}'
    #     # vpcc.run_dataset('Debug_SNCC', 'experiments')
    #     vpcc.run_dataset('SNCC', 'experiments')

    # [TODO]
    # Wait for training the models
    # fix about paralllel running
    geocnn_v1 = GeoCNNv1()
    for rate in range(3):
        geocnn_v1.rate = f'r{rate+1}'
        geocnn_v1.run_dataset('Debug_SNC', 'experiments')

    # geocnn_v2 = GeoCNNv2()
    # for rate in range(4):
    #     geocnn_v2.rate = f'r{rate+1}'
    #     geocnn_v2.run_dataset('Debug_SNC', 'experiments')

    # pcgc_v1 = PCGCv1()
    # # pcgc_v1.rate = 'r1'
    # # pcgc_v1.run_dataset('Debug_SNC', 'experiments')
    # for rate in range(6):
    #     pcgc_v1.rate = f'r{rate+1}'
    #     pcgc_v1.run_dataset('Debug_SNC', 'experiments')
    
    # pcgc_v2 = PCGCv2()
    # pcgc_v2.rate = 'r1'
    # pcgc_v2.run_dataset('Debug_SNCC', 'experiments')
    # for rate in range(4):
    #     pcgc_v2.rate = f'r{rate+1}'
    #     pcgc_v2.run_dataset('Debug_SNCC', 'experiments')


if __name__ == '__main__':
    main()

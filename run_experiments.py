import logging.config

from xvfbwrapper import Xvfb

from utils.file_io import get_logging_config
from algs_wrapper.Draco import Draco
from algs_wrapper.GPCC import GPCC
from algs_wrapper.VPCC import VPCC
from algs_wrapper.GeoCNNv1 import GeoCNNv1
from algs_wrapper.GeoCNNv2 import GeoCNNv2
from algs_wrapper.PCGCv1 import PCGCv1
from algs_wrapper.PCGCv2 import PCGCv2
from evaluator.summary import summarize_all_to_csv

def main():
    LOGGING_CONFIG = get_logging_config('utils/logging.conf')
    logging.config.dictConfig(LOGGING_CONFIG)

    draco = Draco()
    for rate in range(1):
        draco.rate = f'r{rate+1}'
        draco.run_dataset('Sample_SNC', 'experiments')
        draco.run_dataset('Debug_SNC', 'experiments')
        draco.run_dataset('Debug_SNCC', 'experiments')
        # draco.run_dataset('SNC_Test100', 'experiments')
        # draco.run_dataset('SNCC_Test100', 'experiments')
        # draco.run_dataset('MN40_Test100', 'experiments')
        # draco.run_dataset('CAPOD_100', 'experiments')
        # draco.run_dataset('8i_longdress_25', 'experiments')
        # draco.run_dataset('8i_loot_25', 'experiments')
        # draco.run_dataset('8i_soldier_25', 'experiments')
        # draco.run_dataset('8i_redandblack_25', 'experiments')
        # draco.run_dataset('8i_longdress_geo_25', 'experiments')
        # draco.run_dataset('8i_loot_geo_25', 'experiments')
        # draco.run_dataset('8i_soldier_geo_25', 'experiments')
        # draco.run_dataset('8i_redandblack_geo_25', 'experiments')
        
    gpcc = GPCC()
    for rate in range(1):
        gpcc.rate = f'r{rate+1}'
        gpcc.run_dataset('Sample_SNC', 'experiments')
        gpcc.run_dataset('Debug_SNC', 'experiments')
        gpcc.run_dataset('Debug_SNCC', 'experiments')
        # gpcc.run_dataset('SNC_Test100', 'experiments')
        # gpcc.run_dataset('SNCC_Test100', 'experiments')
        # gpcc.run_dataset('MN40_Test100', 'experiments')
        # gpcc.run_dataset('CAPOD_100', 'experiments')
        # gpcc.run_dataset('8i_longdress_25', 'experiments')
        # gpcc.run_dataset('8i_loot_25', 'experiments')
        # gpcc.run_dataset('8i_soldier_25', 'experiments')
        # gpcc.run_dataset('8i_redandblack_25', 'experiments')
        # gpcc.run_dataset('8i_longdress_geo_25', 'experiments')
        # gpcc.run_dataset('8i_loot_geo_25', 'experiments')
        # gpcc.run_dataset('8i_soldier_geo_25', 'experiments')
        # gpcc.run_dataset('8i_redandblack_geo_25', 'experiments')

    vpcc = VPCC()
    for rate in range(1):
        vpcc.rate = f'r{rate+1}'
        # vpcc.run_dataset('Sample_SNC', 'experiments')
        # vpcc.run_dataset('Debug_SNC', 'experiments')
        vpcc.run_dataset('Debug_SNCC', 'experiments')
        # vpcc.run_dataset('SNCC_Test100', 'experiments')
        # vpcc.run_dataset('8i_longdress_25', 'experiments')
        # vpcc.run_dataset('8i_loot_25', 'experiments')
        # vpcc.run_dataset('8i_soldier_25', 'experiments')
        # vpcc.run_dataset('8i_redandblack_25', 'experiments')

    geocnn_v1 = GeoCNNv1()
    for rate in range(1):
        geocnn_v1.rate = f'r{rate+1}'
        # `nbprocesses` depends on your available memory
        # 1 process may cost up to 51 GB memory
        geocnn_v1.run_dataset('Sample_SNC', 'experiments', nbprocesses=1)
        geocnn_v1.run_dataset('Debug_SNC', 'experiments', nbprocesses=1)
        # geocnn_v1.run_dataset('SNC_Test100', 'experiments', nbprocesses=1)
        # geocnn_v1.run_dataset('MN40_Test100', 'experiments', nbprocesses=1)
        # geocnn_v1.run_dataset('CAPOD_100', 'experiments', nbprocesses=1)
        # geocnn_v1.run_dataset('8i_longdress_geo_25', 'experiments', nbprocesses=1)
        # geocnn_v1.run_dataset('8i_loot_geo_25', 'experiments', nbprocesses=1)
        # geocnn_v1.run_dataset('8i_soldier_geo_25', 'experiments', nbprocesses=1)
        # geocnn_v1.run_dataset('8i_redandblack_geo_25', 'experiments', nbprocesses=1)

    geocnn_v2 = GeoCNNv2()
    for rate in range(1):
        geocnn_v2.rate = f'r{rate+1}'
        geocnn_v2.run_dataset('Sample_SNC', 'experiments')
        geocnn_v2.run_dataset('Debug_SNC', 'experiments')
        # geocnn_v2.run_dataset('SNC_Test100', 'experiments')
        # geocnn_v2.run_dataset('MN40_Test100', 'experiments')
        # geocnn_v2.run_dataset('CAPOD_100', 'experiments')
        # geocnn_v2.run_dataset('8i_longdress_geo_25', 'experiments')
        # geocnn_v2.run_dataset('8i_loot_geo_25', 'experiments')
        # geocnn_v2.run_dataset('8i_soldier_geo_25', 'experiments')
        # geocnn_v2.run_dataset('8i_redandblack_geo_25', 'experiments')

    pcgc_v1 = PCGCv1()
    for rate in range(1):
        pcgc_v1.rate = f'r{rate+1}'
        pcgc_v1.run_dataset('Sample_SNC', 'experiments')
        pcgc_v1.run_dataset('Debug_SNC', 'experiments')
        # pcgc_v1.run_dataset('SNC_Test100', 'experiments')
        # pcgc_v1.run_dataset('MN40_Test100', 'experiments')
        # pcgc_v1.run_dataset('CAPOD_100', 'experiments')
        # pcgc_v1.run_dataset('8i_longdress_geo_25', 'experiments')
        # pcgc_v1.run_dataset('8i_loot_geo_25', 'experiments')
        # pcgc_v1.run_dataset('8i_soldier_geo_25', 'experiments')
        # pcgc_v1.run_dataset('8i_redandblack_geo_25', 'experiments')
    
    pcgc_v2 = PCGCv2()
    for rate in range(1):
        pcgc_v2.rate = f'r{rate+1}'
        pcgc_v2.run_dataset('Sample_SNC', 'experiments')
        pcgc_v2.run_dataset('Debug_SNC', 'experiments')
        # pcgc_v2.run_dataset('SNC_Test100', 'experiments')
        # pcgc_v2.run_dataset('MN40_Test100', 'experiments')
        # pcgc_v2.run_dataset('CAPOD_100', 'experiments')
        # pcgc_v2.run_dataset('8i_longdress_geo_25', 'experiments')
        # pcgc_v2.run_dataset('8i_loot_geo_25', 'experiments')
        # pcgc_v2.run_dataset('8i_soldier_geo_25', 'experiments')
        # pcgc_v2.run_dataset('8i_redandblack_geo_25', 'experiments')

if __name__ == '__main__':
    # [TODO]
    # Workaround for using open3d visualizer with multithreading.
    # Create an virtual display and set the env var. for all the 
    # threads. If we move back to multiprocessing in the future, 
    # then this should be set in 
    # `evaluator/metrics/ProjectionBasedMetrics.py` evaluate().
    disp = Xvfb()
    disp.start()
    main()
    disp.stop()
    
    summarize_all_to_csv('experiments')
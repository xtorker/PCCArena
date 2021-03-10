import logging
from logging import config as logging_config
from utils.file_io import glob_filename, glob_filepath
from algs_wrapper.draco import Draco
from algs_wrapper.gpcc import GPCC
from algs_wrapper.geocnn_v2 import GeoCNNv2
from algs_wrapper.pcgc_v1 import PCGCv1
from evaluator.metrics import MetricLogger
from pathlib import Path
import GPUtil


LOGGING_CONFIG = { 
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": { 
        "default": {
            "format": "%(levelname).1s %(asctime)s [%(module)s] %(funcName)s():   %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": { 
        "default": { 
            "level": "INFO",
            "formatter": "default",
            "class": "logging.StreamHandler"
        }
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO"
        }
    }
}


def main():
    logging_config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info('Hey, that was easy.')

    #gpcc = GPCC('cfgs/gpcc/gpcc_r1.yml')
    # draco.run(
    #     '02691156/test/1a9b552befd6306cc8f2d5fe7449af61.ply',
    #     '/mnt/data6/chenghao/PCC_datasets/ShapeNet/color_scale1024',
    #     '/mnt/data6/chenghao/PCC_datasets/ShapeNet/color_normal_scale1024',
    #     '/home/chenghao/PCC_Arena/test',
    #     color = 1
    # )

    # mLogger = MetricLogger(
    #     "/mnt/data6/chenghao/PCC_datasets/ShapeNet/color_normal_scale1024/02691156/test/1a9b552befd6306cc8f2d5fe7449af61.ply",
    #     "/home/chenghao/PCC_Arena/test/dec/02691156/test/1a9b552befd6306cc8f2d5fe7449af61.ply",
    #     "/home/chenghao/PCC_Arena/test_single.log",
    #     color = 1
    # )
    # mLogger.evaluate_all()
    #gpcc.run_dataset('TestMPEG', '/home/chenghao/PCC_Arena/test')
    
    # draco = Draco('r1')
    # draco.run_dataset('Test', '/home/chenghao/PCC_Arena/test')
    
    # geocnn_v2 = GeoCNNv2('r1')
    # geocnn_v2.run_dataset('Test', '/home/chenghao/PCC_Arena/test/geocnn_v2', use_gpu=True)

    draco_r1 = Draco('r1')
    draco_r1.run_dataset('SNCC', '/mnt/data5/chenghao/experiments/draco/SNCC1024/r1')
    
    draco_r2 = Draco('r2')
    draco_r2.run_dataset('SNCC', '/mnt/data5/chenghao/experiments/draco/SNCC1024/r2')
    
    draco_r3 = Draco('r3')
    draco_r3.run_dataset('SNCC', '/mnt/data5/chenghao/experiments/draco/SNCC1024/r3')
    
    draco_r4 = Draco('r4')
    draco_r4.run_dataset('SNCC', '/mnt/data5/chenghao/experiments/draco/SNCC1024/r4')
    
    draco_r5 = Draco('r5')
    draco_r5.run_dataset('SNCC', '/mnt/data5/chenghao/experiments/draco/SNCC1024/r5')
    

if __name__ == '__main__':
    main()

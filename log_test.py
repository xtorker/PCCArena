import logging
from logging import config as logging_config
from utils.file_io import glob_filename, glob_filepath
from algs_wrapper.draco import Draco
from evaluator.metrics import MetricLogger
from pathlib import Path


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
    glob_filename('.', '*.py')
    
    glob_filepath('.', '*.py')

    # draco = Draco('cfgs')
    # draco.run(
    #     '02691156/test/1a9b552befd6306cc8f2d5fe7449af61.ply',
    #     '/mnt/data6/chenghao/PCC_datasets/ShapeNet/color_scale1024',
    #     '/mnt/data6/chenghao/PCC_datasets/ShapeNet/color_normal_scale1024',
    #     '/home/chenghao/PCC_Arena/test',
    #     color = 1
    # )

    mLogger = MetricLogger(
        "/mnt/data6/chenghao/PCC_datasets/ShapeNet/color_normal_scale1024/02691156/test/1a9b552befd6306cc8f2d5fe7449af61.ply",
        "/home/chenghao/PCC_Arena/test/dec/02691156/test/1a9b552befd6306cc8f2d5fe7449af61.ply",
        "/home/chenghao/PCC_Arena/test_single.log",
        color = 1
    )
    mLogger.evaluate_all()
    # draco.run_dataset('SNC', '/home/chenghao/PCC_Arena/test')

if __name__ == '__main__':
    main()
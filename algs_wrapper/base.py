import abc
import logging
from pathlib import Path
from functools import partial

from utils.file_io import load_cfg, glob_filename, glob_filepath
from utils.processing import timer, parallel
from evaluator.metrics import pc_error_wrapper

logger = logging.getLogger(__name__)

class Base(metaclass=abc.ABCMeta):
    def __init__(self, algs_cfg_file):
        self.algs_cfg = load_cfg(algs_cfg_file)

    @abc.abstractmethod
    def preprocess(self):
        return NotImplemented

    @abc.abstractmethod
    def encode(self):
        return NotImplemented

    @abc.abstractmethod
    def decode(self):
        return NotImplemented

    @abc.abstractmethod
    def postprocess(self):
        return NotImplemented

    def set_filepath(self, pcfile, src_dir, nor_dir, exp_dir):
        '''
        Set up the experiment file paths, including encoded binary, decoded point cloud, and evaluation log.

        Parameters:
            pcfile (str or PosixPath): The relative path of input point cloud.
            src_dir (str or PosixPath): The directory of input point cloud.
            nor_dir (str or PosixPath): The directory of input point cloud with normal. (Used to calculate p2plane metrics.)
            exp_dir (str or PosixPath): The directory to store experiments results.
        
        Returns:
            in_pcfile (PosixPath): The absolute path of input point cloud.
            bin_file (PosixPath): The absolute path of encoded binary file.
            out_pcfile (PosixPath): The absolute path of output point cloud.
            evl_log (PosixPath): The absolute path of evaluation log file.
        '''
        in_pcfile = Path(src_dir).joinpath(pcfile)
        nor_pcfile = Path(nor_dir).joinpath(pcfile)
        bin_file = Path(exp_dir).joinpath('bin', pcfile).with_suffix(self.algs_cfg['bin_suffix'])
        out_pcfile = Path(exp_dir).joinpath('dec', pcfile)
        evl_log = Path(exp_dir).joinpath('evl', pcfile).with_suffix('.log')
        
        bin_file.parent.mkdir(parents=True, exist_ok=True)
        out_pcfile.parent.mkdir(parents=True, exist_ok=True)
        evl_log.parent.mkdir(parents=True, exist_ok=True)

        return in_pcfile, nor_pcfile, bin_file, out_pcfile, evl_log

    def run(self, pcfile, src_dir, nor_dir, exp_dir, color=0, resolution=1024):
        '''
        Run a single experiment on the input point cloud and get the experiment results and evaluation log.

        Parameters:
            pcfile (str or PosixPath): The relative path of input point cloud.
            src_dir (str or PosixPath): The directory of input point cloud.
            nor_dir (str or PosixPath): The directory of input point cloud with normal. (Used to calculate p2plane metrics.)
            exp_dir (str or PosixPath): The directory to store experiments results.
        
        Optionals:
            color (int): Calculate color distortion or not. (0: false, 1: true)
            resolution (int): Resolution (scale) of the point cloud.
        '''
        
        in_pcfile, nor_pcfile, bin_file, out_pcfile, evl_log = self.set_filepath(pcfile, src_dir, nor_dir, exp_dir)

        pre_time = timer(self.preprocess)
        enc_time = timer(self.encode, in_pcfile, bin_file)
        dec_time = timer(self.decode, bin_file, out_pcfile)
        post_time = timer(self.postprocess)

        

        print(pc_error_wrapper(nor_pcfile, out_pcfile, color, resolution))


    def run_dataset(self, ds_name, exp_dir, ds_cfg_file=None):
        '''
        Run the experiments on the specified dataset in the experiment directory.

        Parameters:
            ds_name (str): The name of the dataset (refer to cfgs/datasets.yml).
            exp_dir (str or PosixPath): The directory to store experiments results.
        
        Optionals:
            ds_cfg_file (str or PosixPath): The YAML config file of datasets. (default is cfg/datasets.yml)
        '''

        logger.info(f"Start to run experiments on {ds_name} dataset with {type(self).__name__}")

        if ds_cfg_file is None:
            ds_cfg_file = Path(__file__).parent.joinpath("../cfgs/datasets.yml").resolve()
        ds_cfg = load_cfg(ds_cfg_file)

        pc_files = glob_filename(
            ds_cfg[ds_name]['dataset_dir'],
            ds_cfg[ds_name]['test_pattern']
        )

        prun = partial(
            self.run,
            src_dir=ds_cfg[ds_name]['dataset_dir'],
            nor_dir=ds_cfg[ds_name]['dataset_w_normal_dir'],
            exp_dir=exp_dir,
            color=ds_cfg[ds_name]['color'],
            resolution=ds_cfg[ds_name]['resolution']
        )

        parallel(prun, pc_files)
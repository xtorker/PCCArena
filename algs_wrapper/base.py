import abc
from pathlib import Path
from functools import partialmethod

from utils.file_io import load_cfg, glob_filename, glob_filepath
from utils.processing import parallel
from evaluator.metrics import evaluate

class Base(metaclass=abc.ABCMeta):
    def __init__(self, algs_cfg_file):
        self.algs_cfg = load_cfg(algs_cfg_file)

    @abc.abstractmethod
    def encode(self):
        return NotImplemented

    @abc.abstractmethod
    def decode(self):
        return NotImplemented

    def set_filepath(self, pcfile, src_dir, exp_dir):
        '''
        Set up the experiment file paths, including encoded binary, decoded point cloud, and evaluation log.

        Parameters:
            pcfile (str or PosixPath): The relative path of input point cloud.
            src_dir (str or PosixPath): The directory of input point cloud.
            exp_dir (str or PosixPath): The directory to store experiments results.
        
        Returns:
            in_pcfile (PosixPath): The absolute path of input point cloud.
            binfile (PosixPath): The absolute path of encoded binary file.
            out_pcfile (PosixPath): The absolute path of output point cloud.
            evl_log (PosixPath): The absolute path of evaluation log file.
        '''
        in_pcfile = Path(src_dir).joinpath(pcfile)
        binfile = Path(exp_dir).joinpath('bin', pcfile).with_suffix(self.algs_cfg['bin_suffix'])
        out_pcfile = Path(exp_dir).joinpath('dec', pcfile)
        evl_log = Path(exp_dir).joinpath('evl', pcfile).with_suffix('.log')
        
        in_pcfile.parent.mkdir(parents=True, exist_ok=True)
        binfile.parent.mkdir(parents=True, exist_ok=True)
        out_pcfile.parent.mkdir(parents=True, exist_ok=True)
        evl_log.parent.mkdir(parents=True, exist_ok=True)

        return in_pcfile, binfile, out_pcfile, evl_log

    def run(self, pcfile, src_dir, exp_dir, color=0, resolution=1024):
        '''
        Run a single experiment on the input point cloud and get the experiment results and evaluation log.

        Parameters:
            pcfile (str or PosixPath): The relative path of input point cloud.
            src_dir (str or PosixPath): The directory of input point cloud.
            exp_dir (str or PosixPath): The directory to store experiments results.
        
        Optionals:
            color (int): Calculate color distortion or not. (0: false, 1: true)
            resolution (int): Resolution (scale) of the point cloud.
        '''
        
        in_pcfile, binfile, out_pcfile, evl_log = self.set_filepath(pcfile, src_dir, exp_dir)

        self.encode(in_pcfile, binfile)

        self.decode(binfile, out_pcfile)

        evaluate(in_pcfile, out_pcfile, evl_log, color, resolution)


    def run_dataset(self, ds_name, exp_dir, ds_cfg_file=None):
        '''
        Run the experiments on the specified dataset in the experiment directory.

        Parameters:
            ds_name (str): The name of the dataset (refer to cfgs/datasets.yml).
            exp_dir (str or PosixPath): The directory to store experiments results.
        
        Optionals:
            ds_cfg_file (str or PosixPath): The YAML config file of datasets. (default is cfg/datasets.yml)
        '''
        if ds_cfg_file is None:
            ds_cfg_file = Path(__file__).parent.joinpath("../cfgs/datasets.yml").resolve()
        ds_cfg = load_cfg(ds_cfg_file)

        pc_files = glob_filename(
            ds_cfg[ds_name]['dataset_dir'],
            ds_cfg[ds_name]['test_pattern']
        )

        # [TODO]
        # TypeError: 'partialmethod' object is not callable
        # https://stackoverflow.com/questions/49662666/unable-to-call-function-defined-by-partialmethod
        self.prun = partialmethod(
            self.run,
            src_dir=ds_cfg[ds_name]['dataset_dir'],
            exp_dir=exp_dir,
            color=ds_cfg[ds_name]['color'],
            resolution=ds_cfg[ds_name]['resolution']
        )

        parallel(self.prun, pc_files)
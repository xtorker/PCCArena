import abc
import logging
from pathlib import Path
from functools import partial

from utils.file_io import load_cfg, glob_filename, glob_filepath
from utils.processing import timer, parallel
from evaluator.metrics import MetricLogger

logger = logging.getLogger(__name__)

class Base(metaclass=abc.ABCMeta):
    def __init__(self, algs_cfg_file):
        algs_cfg_file = Path(algs_cfg_file).resolve()
        self.algs_cfg = load_cfg(algs_cfg_file)

    @abc.abstractmethod
    def encode(self):
        return NotImplemented

    @abc.abstractmethod
    def decode(self):
        return NotImplemented

    def set_filepath(
            self, 
            pcfile: str or PosixPath,
            src_dir: str or PosixPath,
            nor_dir: str or PosixPath,
            exp_dir: str or PosixPath
        ):
        """Set up the experiment file paths, including encoded binary, decoded point cloud, and evaluation log.

        Args:
            pcfile (str or PosixPath): The relative path of input point cloud.
            src_dir (str or PosixPath): The directory of input point cloud.
            nor_dir (str or PosixPath): The directory of input point cloud with normal. (Necessary for p2plane metrics.)
            exp_dir (str or PosixPath): The directory to store experiments results.

        Returns:
            in_pcfile (PosixPath): The absolute path of input point cloud.
            bin_file (PosixPath): The absolute path of encoded binary file.
            out_pcfile (PosixPath): The absolute path of output point cloud.
            evl_log (PosixPath): The absolute path of evaluation log file.
        """
        in_pcfile = Path(src_dir).joinpath(pcfile)
        nor_pcfile = Path(nor_dir).joinpath(pcfile)
        bin_file = Path(exp_dir).joinpath('bin', pcfile).with_suffix(self.algs_cfg['bin_suffix'])
        out_pcfile = Path(exp_dir).joinpath('dec', pcfile)
        evl_log = Path(exp_dir).joinpath('evl', pcfile).with_suffix('.log')
        
        bin_file.parent.mkdir(parents=True, exist_ok=True)
        out_pcfile.parent.mkdir(parents=True, exist_ok=True)
        evl_log.parent.mkdir(parents=True, exist_ok=True)

        return in_pcfile, nor_pcfile, bin_file, out_pcfile, evl_log

    def run(
            self,
            pcfile: str or PosixPath,
            src_dir: str or PosixPath,
            nor_dir: str or PosixPath,
            exp_dir: str or PosixPath,
            color=0,
            resolution=1024
        ) -> None:
        """Run a single experiment on the given `pcfile` and save the experiment results and evaluation log into `exp_dir`.

        Args:
            pcfile (str or PosixPath): The relative path to `src_dir` of input point cloud.
            src_dir (str or PosixPath): The directory of input point cloud.
            nor_dir (str or PosixPath): The directory of input point cloud with normal. (Necessary for p2plane metrics.)
            exp_dir (str or PosixPath): The directory to store experiments results.
            color (int, optional): Calculate color distortion or not. (0: false, 1: true). Defaults to 0.
            resolution (int, optional): Resolution (scale) of the point cloud. Defaults to 1024.
        """
        self.color = color
        self.resolution = resolution
        
        in_pcfile, nor_pcfile, bin_file, out_pcfile, evl_log = self.set_filepath(pcfile, src_dir, nor_dir, exp_dir)

        enc_time = timer(self.encode, str(in_pcfile), str(bin_file))
        dec_time = timer(self.decode, str(bin_file), str(out_pcfile))

        # grab all the encoded binary files with same filename, but different suffix
        bin_files = glob_filepath(bin_file.parent, bin_file.stem+'*')

        mLogger = MetricLogger(
            nor_pcfile,
            out_pcfile,
            evl_log,
            enc_time,
            dec_time,
            bin_files,
            color,
            resolution
        )

        mLogger.evaluate_all()

    def run_dataset(
            self,
            ds_name: str,
            exp_dir: str or PosixPath,
            use_gpu=False,
            ds_cfg_file='cfgs/datasets.yml'
        ) -> None:
        """Run the experiments on dataset `ds_name` in the `exp_dir`.

        Args:
            ds_name (str): The name of the dataset (refer to cfgs/datasets.yml).
            exp_dir (str or PosixPath): The directory to store experiments results.
            use_gpu (bool, optional): Running PCC algorithm on GPU or not. Defaults to False.
            ds_cfg_file (str or PosixPath, optional): The YAML config file of datasets. Defaults to '../cfgs/datasets.yml'.
        """
        logger.info(f"Start to run experiments on {ds_name} dataset with {type(self).__name__} in {exp_dir}")

        if ds_cfg_file == 'cfgs/datasets.yml':
            ds_cfg_file = Path(__file__).parent.parent.joinpath(ds_cfg_file).resolve()
        ds_cfg = load_cfg(ds_cfg_file)

        pc_files = glob_filename(
            ds_cfg[ds_name]['dataset_dir'],
            ds_cfg[ds_name]['test_pattern'],
            verbose=True
        )

        prun = partial(
            self.run,
            src_dir=ds_cfg[ds_name]['dataset_dir'],
            nor_dir=ds_cfg[ds_name]['dataset_w_normal_dir'],
            exp_dir=exp_dir,
            color=ds_cfg[ds_name]['color'],
            resolution=ds_cfg[ds_name]['resolution']
        )

        parallel(prun, pc_files, use_gpu)
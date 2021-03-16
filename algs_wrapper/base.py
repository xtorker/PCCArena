import re
import abc
import logging
from pathlib import Path
from typing import Union
from functools import partial
from multiprocessing.managers import BaseProxy

from utils.file_io import load_cfg, glob_file
from utils.processing import timer, parallel
from evaluator.summary import summary_one_setup
from evaluator.metrics import ViewIndependentMetrics

logger = logging.getLogger(__name__)

class Base(metaclass=abc.ABCMeta):
    def __init__(self) -> None:
        algs_cfg_file = (
            Path(__file__).parents[1]
            .joinpath(f'cfgs/algs/{type(self).__name__}.yml').resolve()
        )
        self._algs_cfg = load_cfg(algs_cfg_file)
        self._use_gpu = self._algs_cfg['use_gpu']

    @abc.abstractmethod
    def encode(self):
        return NotImplemented

    @abc.abstractmethod
    def decode(self):
        return NotImplemented

    @property
    def rate(self) -> str:
        """Specify the set of bitrate control coding parameters. 
        The related coding parameters need to be configured in the 
        corresponding PCC algs config file.
        
        Returns
        -------
        `str`
            Tag of the rate control set.
        """
        return self._rate

    @rate.setter
    def rate(self, rate: str) -> None:
        m = re.search('^r[1-9]+', rate, re.MULTILINE)
        if m is None:
            logger.warning(
                f"Invalid rate control parameters. Use 'r1', 'r2', etc."
            )
        self._rate = m.group()

    def run_dataset(
            self,
            ds_name: str,
            exp_dir: Union[str, Path],
            ds_cfg_file: Union[str, Path] = 'cfgs/datasets.yml'
        ) -> None:
        """Run the experiments on dataset `ds_name` in the ``exp_dir``.
        
        Parameters
        ----------
        ds_name : `str`
            The name of the dataset (stored in 'cfgs/datasets.yml').
        exp_dir : `Union[str, Path]`
            The directory to store experiments results.
        ds_cfg_file : `Union[str, Path]`, optional
            The YAML config file of datasets. Defaults to 
            'cfgs/datasets.yml'.
        """
        exp_dir = (
            Path(exp_dir)
            .joinpath(f'{type(self).__name__}/{ds_name}/{self._rate}')
            .resolve()
        )
        
        logger.info(
            f"Start to run experiments on {ds_name} dataset "
            f"with {type(self).__name__} in {exp_dir}"
        )

        if ds_cfg_file == 'cfgs/datasets.yml':
            ds_cfg_file = (
                Path(__file__).parents[1].joinpath(ds_cfg_file).resolve()
            )
        ds_cfg = load_cfg(ds_cfg_file)

        pc_files = glob_file(
            ds_cfg[ds_name]['dataset_dir'],
            ds_cfg[ds_name]['test_pattern'],
            verbose=True
        )

        prun = partial(
            self.run,
            src_dir=ds_cfg[ds_name]['dataset_dir'],
            nor_dir=ds_cfg[ds_name]['dataset_w_normal_dir'],
            exp_dir=exp_dir,
            scale=ds_cfg[ds_name]['scale'],
            color=ds_cfg[ds_name]['color'],
            resolution=ds_cfg[ds_name]['resolution']
        )

        parallel(prun, pc_files, self._use_gpu)
        
        summary_one_setup(Path(exp_dir).joinpath('evl'))

    def run(
            self,
            pcfile: Union[str, Path],
            src_dir: Union[str, Path],
            nor_dir: Union[str, Path],
            exp_dir: Union[str, Path],
            scale: int,
            color: int = 0,
            resolution: int = None,
            gpu_queue: BaseProxy = None
        ) -> None:
        """Run a single experiment on the given ``pcfile`` and save the 
        experiment results and evaluation log into ``exp_dir``.
        
        Parameters
        ----------
        pcfile : `Union[str, Path]`
            The relative path to ``src_dir`` of input point cloud.
        src_dir : `Union[str, Path]`
            The directory of input point cloud.
        nor_dir : `Union[str, Path]`
            The directory of input point cloud with normal. (Necessary 
            for p2plane metrics.)
        exp_dir : `Union[str, Path]`
            The directory to store experiments results.
        scale : `int`
            The maximum length of the ``pcfile`` among x, y, and z axes.
            Used as an encoding parameter in several PCC algorithms.
        color : `int`, optional
            1 for ``pcfile`` containing color, 0 otherwise. Defaults to 0.
        resolution : `int`, optional
            Maximum NN distance of the ``pcfile``. Only used for 
            evaluation. If the resolution is not specified, it will be 
            calculated on the fly. Defaults to None.
        gpu_queue : `BaseProxy`, optional
            A multiprocessing Manager.Queue() object. The queue stores 
            the GPU device IDs get from GPUtil.getAvailable(). Must be 
            assigned if running a PCC algorithm using GPUs.
        """
        self._pc_scale = scale
        self._color = color
        
        in_pcfile, nor_pcfile, bin_file, out_pcfile, evl_log = (
            self._set_filepath(pcfile, src_dir, nor_dir, exp_dir)
        )

        if self._use_gpu is True:
            gpu_id = gpu_queue.get()
            enc_time = timer(
                self.encode, in_pcfile, bin_file, gpu_id)
            dec_time = timer(
                self.decode, bin_file, out_pcfile, gpu_id)
            gpu_queue.put(gpu_id)
        else:
            enc_time = timer(self.encode, in_pcfile, bin_file)
            dec_time = timer(self.decode, bin_file, out_pcfile)

        VIMetrics = ViewIndependentMetrics()
        ret = VIMetrics.evaluate(
            nor_pcfile,
            out_pcfile,
            color,
            resolution,
            enc_time,
            dec_time,
            [bin_file]
        )
        with open(evl_log, 'w') as f:
            f.write(ret)

    def _set_filepath(
            self, 
            pcfile: Union[str, Path],
            src_dir: Union[str, Path],
            nor_dir: Union[str, Path],
            exp_dir: Union[str, Path]
        ) -> tuple[str, str, str, str, str]:
        """Set up the experiment file paths, including encoded binary, 
        decoded point cloud, and evaluation log.
        
        Parameters
        ----------
        pcfile : `Union[str, Path]`
            The relative path of input point cloud.
        src_dir : `Union[str, Path]`
            The directory of input point cloud.
        nor_dir : `Union[str, Path]`
            The directory of input point cloud with normal. (Necessary 
            for p2plane metrics.)
        exp_dir : `Union[str, Path]`
            The directory to store experiments results.
        
        Returns
        -------
        `tuple[str, str, str, str, str]`
            The full path of input point cloud, input point cloud with 
            normal, encoded binary file, output point cloud, and 
            evaluation log file.
        """
        in_pcfile = Path(src_dir).joinpath(pcfile)
        nor_pcfile = Path(nor_dir).joinpath(pcfile)
        bin_file = (
            Path(exp_dir)
            .joinpath('bin', pcfile).with_suffix(self._algs_cfg['bin_suffix'])
        )
        out_pcfile = Path(exp_dir).joinpath('dec', pcfile)
        evl_log = Path(exp_dir).joinpath('evl', pcfile).with_suffix('.log')
        
        bin_file.parent.mkdir(parents=True, exist_ok=True)
        out_pcfile.parent.mkdir(parents=True, exist_ok=True)
        evl_log.parent.mkdir(parents=True, exist_ok=True)

        return (
            str(in_pcfile), str(nor_pcfile), str(bin_file), str(out_pcfile), 
            str(evl_log)
        )
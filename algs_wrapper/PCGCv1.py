from typing import Union
from pathlib import Path
from multiprocessing.managers import BaseProxy

from algs_wrapper.base import Base
from utils.file_io import glob_file
from utils.processing import execute_cmd, timer
from evaluator.metrics import ViewIndependentMetrics

class PCGCv1(Base):
    def __init__(self):
        super().__init__()

    def encode(self, in_pcfile, bin_file, gpu_id):
        cmd = [
            self._algs_cfg['python'],
            self._algs_cfg['test_script'],
            'compress',
            in_pcfile,
            bin_file,
            '--ckpt_dir', self._algs_cfg[self.rate]['ckpt_dir'],
            '--scale', str(self._algs_cfg[self.rate]['scale']),
            '--rho', str(self._algs_cfg[self.rate]['rho'])
        ]
        
        assert execute_cmd(cmd, cwd=self._algs_cfg['rootdir'], gpu_id=gpu_id)

    def decode(self, bin_file, out_pcfile, gpu_id):
        cmd = [
            self._algs_cfg['python'],
            self._algs_cfg['test_script'],
            'decompress',
            bin_file,
            out_pcfile,
            '--ckpt_dir', self._algs_cfg[self.rate]['ckpt_dir'],
            '--scale', str(self._algs_cfg[self.rate]['scale']),
            '--rho', str(self._algs_cfg[self.rate]['rho'])
        ]

        assert execute_cmd(cmd, cwd=self._algs_cfg['rootdir'], gpu_id=gpu_id)
    
    # Overwriting the base class method due to the compressed binary 
    # file format of PCGCv1.
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
            1 for calculating color metric, 0 otherwise. Defaults to 0.
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
                self.encode, str(in_pcfile), str(bin_file), gpu_id)
            dec_time = timer(
                self.decode, str(bin_file), str(out_pcfile), gpu_id)
            gpu_queue.put(gpu_id)
        else:
            enc_time = timer(self.encode, str(in_pcfile), str(bin_file))
            dec_time = timer(self.decode, str(bin_file), str(out_pcfile))

        # [TODO] Consider to extract a method to collect bin files to 
        # avoid overwrite the run() method.
        
        # grab all the encoded binary files with same filename, but 
        # different suffix
        bin_files = glob_file(
            bin_file.parent, bin_file.stem+'*', fullpath=True
        )

        VIMetrics = ViewIndependentMetrics()
        ret = VIMetrics.evaluate(
            nor_pcfile,
            out_pcfile,
            color,
            resolution,
            enc_time,
            dec_time,
            bin_files
        )
        with open(evl_log, 'w') as f:
            f.write(ret)
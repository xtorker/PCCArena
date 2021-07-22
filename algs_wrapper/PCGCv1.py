from typing import Union
from pathlib import Path
from multiprocessing.managers import BaseProxy

from algs_wrapper.base import Base
from utils.file_io import glob_file
from evaluator.evaluator import Evaluator

class PCGCv1(Base):
    def __init__(self):
        super().__init__()

    def make_encode_cmd(self, in_pcfile, bin_file):
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
        
        return cmd

    def make_decode_cmd(self, bin_file, out_pcfile):
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

        return cmd
    
    # Overwriting the base class method due to the compressed binary 
    # file format of PCGCv1.
    def _evaluate_and_log(
            self,
            ref_pcfile: Union[str, Path],
            target_pcfile: Union[str, Path],
            bin_file: Union[str, Path],
            evl_log: Union[str, Path],
            enc_time: float = None,
            dec_time: float = None,
            o3d_vis = None
        ):
        # grab all the encoded binary files with same filename, but 
        # different suffix
        bin_files = glob_file(
            Path(bin_file).parent, Path(bin_file).stem+'*', 
            fullpath=True
        )
        
        aggregated_bin = Path(bin_file).with_suffix('.bin')
        with open(aggregated_bin, 'wb') as fw:
            for bin_file in bin_files:
                with open(bin_file, 'rb') as fr:
                    fw.write(fr.read())

        evaluator = Evaluator(
            ref_pcfile,
            target_pcfile,
            aggregated_bin,
            enc_time,
            dec_time,
            o3d_vis
        )
        ret = evaluator.evaluate()
        
        with open(evl_log, 'w') as f:
            f.write(ret)



from pathlib import Path

from algs_wrapper.base import Base
from utils.processing import execute_cmd

class PCGCv1(Base):
    def __init__(self, ):
        super().__init__("cfgs/pcgc_v1.yml", use_gpu=True)

    def encode(self, in_pcfile, bin_file):
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
        
        assert execute_cmd(cmd)


    def decode(self, bin_file, out_pcfile):
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

        assert execute_cmd(cmd)
from pathlib import Path

from algs_wrapper.base import Base
from utils.processing import execute_cmd

class PCGCv1(Base):
    def __init__(self, rate):
        super().__init__("cfgs/pcgc_v1.yml")
        self.rate = rate

    def encode(self, in_pcfile, bin_file):
        cmd = [
            self.algs_cfg['python'],
            self.algs_cfg['test_script'],
            'compress',
            in_pcfile,
            bin_file,
            '--ckpt_dir', self.algs_cfg[self.rate]['ckpt_dir'],
            '--scale', str(self.algs_cfg[self.rate]['scale']),
            '--rho', str(self.algs_cfg[self.rate]['rho'])
        ]
        
        assert execute_cmd(cmd)


    def decode(self, bin_file, out_pcfile):
        cmd = [
            self.algs_cfg['python'],
            self.algs_cfg['test_script'],
            'decompress',
            bin_file,
            out_pcfile,
            '--ckpt_dir', self.algs_cfg[self.rate]['ckpt_dir'],
            '--scale', str(self.algs_cfg[self.rate]['scale']),
            '--rho', str(self.algs_cfg[self.rate]['rho'])
        ]

        assert execute_cmd(cmd)



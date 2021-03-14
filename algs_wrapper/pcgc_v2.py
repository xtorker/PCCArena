from pathlib import Path

from algs_wrapper.base import Base
from utils.processing import execute_cmd

class PCGCv2(Base):
    def __init__(self, ):
        super().__init__("cfgs/pcgc_v2.yml", use_gpu=True)

    def encode(self, in_pcfile, bin_file):
        cmd = [
            self._algs_cfg['python'],
            self._algs_cfg['test_script'],
            'compress',
            in_pcfile,
            bin_file,
            '--ckpt_dir', self._algs_cfg[self.rate]['ckpt_dir'],
            '--voxel_size', str(self._algs_cfg[self.rate]['voxel_size'])
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
            '--voxel_size', str(self._algs_cfg[self.rate]['voxel_size']),
            '--rho', str(self._algs_cfg[self.rate]['rho'])
        ]

        assert execute_cmd(cmd)
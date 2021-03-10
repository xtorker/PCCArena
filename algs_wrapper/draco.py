from pathlib import Path

from algs_wrapper.base import Base
from utils.processing import execute_cmd

class Draco(Base):
    def __init__(self, rate):
        super().__init__("cfgs/draco.yml")
        self.rate = rate

    def encode(self, in_pcfile, bin_file):
        cmd = [
            self.algs_cfg['encoder'],
            '-i', in_pcfile,
            '-o', bin_file,
            '-point_cloud',
            '-qp', str(self.algs_cfg[self.rate]['qp']),
            '-qt', str(self.algs_cfg[self.rate]['qt']),
            '-qn', str(self.algs_cfg[self.rate]['qn']),
            '-qg', str(self.algs_cfg[self.rate]['qg']),
            '-cl', str(self.algs_cfg[self.rate]['cl'])
        ]
        
        assert execute_cmd(cmd)


    def decode(self, bin_file, out_pcfile):
        cmd = [
            self.algs_cfg['decoder'],
            '-i', bin_file,
            '-o', out_pcfile
        ]

        assert execute_cmd(cmd)

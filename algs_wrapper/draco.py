from pathlib import Path

from algs_wrapper.base import Base
from utils.processing import execute_cmd

class Draco(Base):
    def __init__(self, cfg_dir):
        self.algs_cfg_file = Path(cfg_dir).joinpath('draco.yml')
        super().__init__(self.algs_cfg_file)

    def preprocess(self):
        pass

    def encode(self, in_pcfile, bin_file):
        cmd = [
            self.algs_cfg['draco_encoder'],
            '-i', in_pcfile,
            '-o', bin_file,
            '-point_cloud',
            '-qp', str(self.algs_cfg['qp']),
            '-qt', str(self.algs_cfg['qt']),
            '-qn', str(self.algs_cfg['qn']),
            '-qg', str(self.algs_cfg['qg']),
            '-cl', str(self.algs_cfg['cl'])
        ]
        
        assert execute_cmd(cmd)


    def decode(self, bin_file, out_pcfile):
        cmd = [
            self.algs_cfg['draco_decoder'],
            '-i', bin_file,
            '-o', out_pcfile
        ]

        assert execute_cmd(cmd)

    def postprocess(self):
        pass




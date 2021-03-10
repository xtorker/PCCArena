from pathlib import Path

from algs_wrapper.base import Base
from utils.processing import execute_cmd

class PCGCv2(Base):
    def __init__(self, rate):
        super().__init__("cfgs/pcgc_v2.yml")
        self.rate = rate

    def encode(self, in_pcfile, bin_file):
        cmd = [
            self.algs_cfg['python'],
            self.algs_cfg['encoder'],
            '--input_files', in_pcfile,
            '--output_files', bin_file,
            '--checkpoint_dir', self.algs_cfg['checkpoint_dir'],
            '--model_config', self.algs_cfg['model_config'],
            '--opt_metrics', self.algs_cfg['opt_metrics'],
            '--resolution', str(self.algs_cfg[self.rate]['resolution'])
        ]
        
        assert execute_cmd(cmd)


    def decode(self, bin_file, out_pcfile):
        cmd = [
            self.algs_cfg['python'],
            self.algs_cfg['decoder'],
            '--input_files', bin_file,
            '--output_files', out_pcfile,
            '--checkpoint_dir', self.algs_cfg['checkpoint_dir'],
            '--model_config', self.algs_cfg['model_config']
        ]

        assert execute_cmd(cmd)



from pathlib import Path

from algs_wrapper.base import Base
from utils.processing import execute_cmd

class GPCC(Base):
    def __init__(self, rate):
        super().__init__("cfgs/gpcc.yml")
        self.rate = rate

    def encode(self, in_pcfile, bin_file):
        cmd = [
            self.algs_cfg['encoder'],
            f'--uncompressedDataPath={in_pcfile}',
            f'--compressedStreamPath={bin_file}',
            f'--positionQuantizationScale={self.algs_cfg[self.rate]["positionQuantizationScale"]}',
            '--mergeDuplicatedPoints=1',
            '--mode=0'
        ]
        if self.color == 1:
            cmd = cmd + [
                '--attribute=color'
            ]
        
        assert execute_cmd(cmd)


    def decode(self, bin_file, out_pcfile):
        cmd = [
            self.algs_cfg['decoder'],
            f'--compressedStreamPath={bin_file}',
            f'--reconstructedDataPath={out_pcfile}',
            '--mode=1'
        ]

        assert execute_cmd(cmd)




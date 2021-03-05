from pathlib import Path

from algs_wrapper.base import Base
from utils.processing import execute_cmd

class G_PCC(Base):
    def __init__(self, gpcc_cfg_file):
        super().__init__(gpcc_cfg_file)

    def preprocess(self):
        pass

    def encode(self, in_pcfile, bin_file):
        cmd = [
            self.algs_cfg['gpcc_encoder'],
            f'--uncompressedDataPath={in_pcfile}',
            f'--compressedStreamPath={bin_file}',
            f'--positionQuantizationScale={self.algs_cfg["positionQuantizationScale"]}',
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
            self.algs_cfg['gpcc_decoder'],
            f'--compressedStreamPath={bin_file}',
            f'--reconstructedDataPath={out_pcfile}',
            '--mode=1'
        ]

        assert execute_cmd(cmd)

    def postprocess(self):
        pass




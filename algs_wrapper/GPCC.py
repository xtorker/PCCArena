from algs_wrapper.base import Base

class GPCC(Base):
    def __init__(self):
        super().__init__()

    def encode(self, in_pcfile, bin_file):
        cmd = [
            self._algs_cfg['encoder'],
            f'--uncompressedDataPath={in_pcfile}',
            f'--compressedStreamPath={bin_file}',
            f'--positionQuantizationScale={self._algs_cfg[self.rate]["positionQuantizationScale"]}',
            '--mergeDuplicatedPoints=1',
            '--mode=0'
        ]
        if self._color == 1:
            cmd = cmd + [
                '--attribute=color'
            ]
        
        return cmd

    def decode(self, bin_file, out_pcfile):
        cmd = [
            self._algs_cfg['decoder'],
            f'--compressedStreamPath={bin_file}',
            f'--reconstructedDataPath={out_pcfile}',
            '--mode=1'
        ]

        return cmd




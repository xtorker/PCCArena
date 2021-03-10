from pathlib import Path

from algs_wrapper.base import Base
from utils.processing import execute_cmd

logger = logging.getLogger(__name__)

class VPCC(Base):
    def __init__(self, rate):
        super().__init__("cfgs/vpcc.yml")
        self.rate = rate

    def encode(self, in_pcfile, bin_file):
        cmd = [
            self.algs_cfg['encoder'],
            '--configurationFolder=cfg/',
            '--config=cfg/common/ctc-common.cfg',
            f'--config={self.algs_cfg['condition_cfg']}',
            f'--config={self.algs_cfg[self.rate]['rate_cfg']}',
            f'--videoEncoderOccupancyPath={self.algs_cfg['videoEncoder']}',
            f'--videoEncoderGeometryPath={self.algs_cfg['videoEncoder']}',
            f'--videoEncoderAttributePath={self.algs_cfg['videoEncoder']}',
            '--frameCount=1',
            f'--resolution={self.resolution}',
            f'--uncompressedDataPath={in_pcfile}',
            f'--compressedStreamPath={bin_file}
        ]
        try:
            assert self.color == 1
        except AssertionError:
            logger.error("V-PCC only supports point cloud with color, please check the input point cloud.")
            raise
        
        assert execute_cmd(cmd)


    def decode(self, bin_file, out_pcfile):
        cmd = [
            self.algs_cfg['decoder'],
            f'--videoDecoderOccupancyPath={self.algs_cfg['videoDecoder']}',
            f'--videoDecoderGeometryPath={self.algs_cfg['videoDecoder']}',
            f'--videoDecoderAttributePath={self.algs_cfg['videoDecoder']}',
            f'--inverseColorSpaceConversionConfig={self.algs_cfg['inverseColorSpaceConversionConfig']}',
            f'--compressedStreamPath={bin_file}',
            f'--reconstructedDataPath={out_pcfile}'
        ]

        assert execute_cmd(cmd)




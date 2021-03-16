import logging

from algs_wrapper.base import Base
from utils.processing import execute_cmd

logger = logging.getLogger(__name__)

class VPCC(Base):
    def __init__(self):
        super().__init__()

    def encode(self, in_pcfile, bin_file):
        cmd = [
            self._algs_cfg['encoder'],
            f'--uncompressedDataPath={in_pcfile}',
            f'--compressedStreamPath={bin_file}',
            '--configurationFolder=cfg/',
            '--config=cfg/common/ctc-common.cfg',
            f'--config={self._algs_cfg["condition_cfg"]}',
            f'--config={self._algs_cfg[self.rate]["rate_cfg"]}',
            f'--videoEncoderOccupancyPath={self._algs_cfg["videoEncoder"]}',
            f'--videoEncoderGeometryPath={self._algs_cfg["videoEncoder"]}',
            f'--videoEncoderAttributePath={self._algs_cfg["videoEncoder"]}',
            '--frameCount=1',
            '--computeMetrics=0'
        ]
        try:
            assert self._color == 1
        except AssertionError:
            logger.error("V-PCC only supports point cloud with color, please check the input point cloud.")
            raise
        
        assert execute_cmd(cmd, cwd=self._algs_cfg['rootdir'])

    def decode(self, bin_file, out_pcfile):
        cmd = [
            self._algs_cfg['decoder'],
            f'--compressedStreamPath={bin_file}',
            f'--reconstructedDataPath={out_pcfile}',
            f'--videoDecoderOccupancyPath={self._algs_cfg["videoDecoder"]}',
            f'--videoDecoderGeometryPath={self._algs_cfg["videoDecoder"]}',
            f'--videoDecoderAttributePath={self._algs_cfg["videoDecoder"]}',
            f'--inverseColorSpaceConversionConfig={self._algs_cfg["inverseColorSpaceConversionConfig"]}',
            '--computeMetrics=0'
        ]

        assert execute_cmd(cmd, cwd=self._algs_cfg['rootdir'])




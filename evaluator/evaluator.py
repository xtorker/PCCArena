
from pathlib import Path
from typing import Union, List, Tuple

import open3d as o3d

from utils._version import __version__
from evaluator.metrics.PointBasedMetrics import PointBasedMetrics
from evaluator.metrics.ProjectionBasedMetrics import ProjectionBasedMetrics


class Evaluator():
    def __init__(
            self,
            ref_pc: Union[str, Path],
            target_pc: Union[str, Path],
            bin_file: Union[str, Path] = None,
            enc_t: float = None,
            dec_t: float = None
        ):
        self._ref_pc = ref_pc
        self._target_pc = target_pc
        self._bin_file = bin_file
        self._enc_t = enc_t
        self._dec_t = dec_t
        self._results = ''

    def evaluate(self):
        # get log header
        self._get_log_header()
        
        # log running time and bitrate
        self._log_running_time_and_filesize()
        
        PointMetrics = PointBasedMetrics(self._ref_pc, self._target_pc)
        ProjMetrics = ProjectionBasedMetrics(self._ref_pc, self._target_pc)
        
        self._results += PointMetrics.evaluate()
        self._results += ProjMetrics.evaluate()
        
        # [TODO] Dynamic Import Modules
        # for metrics_cls in load_modules():
        #     instance = metrics_cls()
        #     ret = instance.evaluate(self._ref_pc, self._target_pc)
        #     self._results += ret
        
        return self._results
    
    def _get_log_header(self) -> None:
        """Log the version of PCC Arena and the path of two point cloud.
        """
        
        lines = [
            f"PCC-Arena Evaluator {__version__}",
            f"Reference Point Cloud: {self._ref_pc}",
            f"Target Point Cloud: {self._target_pc}",
            "\n",
        ]
        lines = '\n'.join(lines)
        
        self._results += lines

    def _log_running_time_and_filesize(self) -> None:
        """Log running time (encoding and decoding) and encoded 
        binary size.
        """
        
        # number of points in reference point cloud
        pc = o3d.io.read_point_cloud(self._ref_pc)
        num_points = len(pc.points)

        # file size of reference point cloud in `kB`
        ref_pc_size = Path(self._ref_pc).stat().st_size / 1000
        
        # check if binary file is initialized in constructor
        if self._bin_file:
            # file size of compressed binary file in `kB`
            bin_size = Path(self._bin_file).stat().st_size / 1000
            compression_ratio = bin_size / ref_pc_size  # kB
            bpp = (bin_size * 1000 * 8) / num_points
        else:
            bin_size = compression_ratio = bpp = "Not Avaliable"

        # check if running time is initialized in constructor
        if self._enc_t and self._dec_t:
            enc_t = f"{self._enc_t:0.4f}"
            dec_t = f"{self._dec_t:0.4f}"
        else:
            enc_t = dec_t = "Not Avaliable"

        lines = [
            f"========== Time & Binary Size ==========",
            f"Encoding time (s)           : {enc_t}",
            f"Decoding time (s)           : {dec_t}",
            f"Source point cloud size (kB): {ref_pc_size}",
            f"Total binary files size (kB): {bin_size}",
            f"Compression ratio           : {compression_ratio}",
            f"bpp (bits per point)        : {bpp}",
            "\n",
        ]
        lines = '\n'.join(lines)

        self._results += lines
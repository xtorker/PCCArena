import re
import logging
import subprocess as sp
from pathlib import Path
from typing import Union

from pyntcloud import PyntCloud

from _version import __version__

logger = logging.getLogger(__name__)

class MetricLogger:
    """A class for evaluting point cloud and logging the result into 
    file.
    """
    
    def __init__(self) -> None:
        self._pc_error_bin = (
            Path(__file__)
            .parent.joinpath("mpeg-pcc-dmetric-master/test/pc_error")
            .resolve()
        )

    def evaluate_and_log(
            self,
            ref_pc: Union[str, Path],
            target_pc: Union[str, Path],
            evl_log: Union[str, Path],
            color: int = 0,
            resolution: int = 1024,
            enc_t: float = None,
            dec_t: float = None,
            bin_files: Union[str, Path] = None
        ) -> None:
        """Run the evaluation and log into ``evl_log``.
        
        Parameters
        ----------
        ref_pc : `Union[str, Path]`
            Full path of the reference point cloud.
        target_pc : `Union[str, Path]`
            Full path of the target point.
        evl_log : `Union[str, Path]`
            Full path of the log file to store the evaluation result.
        color : `int`, optional
            1 for calculating color metric, 0 otherwise. Defaults to 0.
        resolution : `int`, optional
            Bounding box size of the point cloud (Max length among xyz 
            axises). Defaults to 1024.
        enc_t : `float`, optional
            Total encoding time. Defaults to None.
        dec_t : `float`, optional
            Total decoding time. Defaults to None.
        bin_files : `Union[str, Path]`, optional
            Full path of the encoded binary file. Used for calculate the
            compression ratio. Defaults to None.
        """
        self._ref_pc = ref_pc
        self._target_pc = target_pc
        self._evl_log = evl_log
        self._color = color
        self._resolution = resolution
        self._enc_t = enc_t
        self._dec_t = dec_t
        self._bin_files = bin_files
        
        self.__log_header()

        # check if any of the values below is not initialized
        if None in [self._enc_t, self._dec_t, self._bin_files]:
            pass
        else:
            self.__log_time_and_filesize()

        self.__objective_quality()

    def __log_header(self):
        """Log the version of PCC Arena and the path of two point cloud.
        """
        lines = [
            f"PCC-Arena Evaluator {__version__}",
            f"ref_pc: {self._ref_pc}",
            f"target_pc: {self._target_pc}",
            "\n",
        ]
        with open(self._evl_log, 'w') as f:
            f.writelines('\n'.join(lines))

    def __log_time_and_filesize(self):
        """Log processing time (encoding and decoding) and encoded 
        binary size if they are provided in constructor.
        """
        cloud = PyntCloud.from_file(str(self._ref_pc))
        num_points = len(cloud.points['x'])

        ref_pc_size = Path(self._ref_pc).stat().st_size / 1000  # kB
        total_bin_size = (
            sum(Path(bin_f).stat().st_size for bin_f in self._bin_files) / 1000
        )  # kB
        compression_ratio = total_bin_size / ref_pc_size  # kB
        bpp = (total_bin_size * 1000 * 8) / num_points

        lines = [
            f"========== Time & Binary Size ==========",
            f"Encoding time:                {self._enc_t:0.4f}",
            f"Decoding time:                {self._dec_t:0.4f}",
            f"Source point cloud size (kB): {ref_pc_size}",
            f"Total binary files size (kB): {total_bin_size}",
            f"Compression ratio:            {compression_ratio}",
            f"bpp (bits per point):         {bpp}",
            "\n",
        ]

        with open(self._evl_log, 'a') as f:
            f.writelines('\n'.join(lines))

    def __objective_quality(self):
        """Parse the result of objective quality metrics and log it into
        ``self.eva_log``.
        """
        ret = self.__pc_error_wrapper()

        chosen_metrics = [
            'ACD1      \(p2point\): ',
            'ACD2      \(p2point\): ',
            'CD        \(p2point\): ',
            'CD,PSNR   \(p2point\): ',
            'h.        \(p2point\): ',
            'ACD1      \(p2plane\): ',
            'ACD2      \(p2plane\): ',
            'CD        \(p2plane\): ',
            'CD,PSNR   \(p2plane\): ',
            'h.        \(p2plane\): ',
            'c\[0\],PSNRF         : ',
            'c\[1\],PSNRF         : ',
            'c\[2\],PSNRF         : ',
            'hybrid geo-color   : ',
        ]

        found_val = []

        for pattern in chosen_metrics:
            isfound = False
            for line in ret.splitlines():
                m = re.search(f'(?<={pattern}).*', line)
                if m:
                    found_val.append(m.group())
                    isfound = True
                    break
            if isfound is False:
                found_val.append('NaN')

        assert len(found_val) == len(chosen_metrics)

        lines = [
            f"========== Objective Quality ===========",
            f"Asym. Chamfer dist. (1->2) p2pt: {found_val[0]}",
            f"Asym. Chamfer dist. (2->1) p2pt: {found_val[1]}",
            f"Chamfer dist.              p2pt: {found_val[2]}",
            f"CD-PSNR                    p2pt: {found_val[3]}",
            f"Hausdorff distance         p2pt: {found_val[4]}",
            f"----------------------------------------",
            f"Asym. Chamfer dist. (1->2) p2pl: {found_val[5]}",
            f"Asym. Chamfer dist. (2->1) p2pl: {found_val[6]}",
            f"Chamfer dist.              p2pl: {found_val[7]}",
            f"CD-PSNR                    p2pl: {found_val[8]}",
            f"Hausdorff distance         p2pl: {found_val[9]}",
            f"----------------------------------------",
            f"Y-CPSNR                        : {found_val[10]}",
            f"U-CPSNR                        : {found_val[11]}",
            f"V-CPSNR                        : {found_val[12]}",
            "\n",
            f"============== QoE Metric ==============",
            f"Hybrid geo-color               : {found_val[13]}",
            "\n",
        ]

        with open(self._evl_log, 'a') as f:
            f.writelines('\n'.join(lines))

    def __pc_error_wrapper(self) -> str:
        """Wrapper of the metric software, which modifies the formulas 
        and adds new metrics based on mpeg-pcc-dmetric.

        Returns
        -------
        `str`
            The result of objective quality metrics.
        """
        cmd = [
            self._pc_error_bin,
            f'--fileA={self._ref_pc}',
            f'--fileB={self._target_pc}',
            f'--color={self._color}',
            f'--resolution={self._resolution}',
            '--hausdorff=1',
        ]

        ret = sp.run(cmd, capture_output=True, universal_newlines=True)

        return ret.stdout
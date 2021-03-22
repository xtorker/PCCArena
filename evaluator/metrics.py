import re
import abc
import logging
import subprocess as sp
from pathlib import Path
from typing import Union

from pyntcloud import PyntCloud

from utils._version import __version__
from evaluator.gdiam_wrapper import findMaxNNdistance

logger = logging.getLogger(__name__)

class BaseMetrics(metaclass=abc.ABCMeta):
    """Base class of metrics. Generate log header, processing time, and 
    bitrate metrics results.
    """
    
    def __init__(self) -> None:
        self._results = []

    @abc.abstractmethod
    def _get_quality_metrics(self):
        return NotImplemented

    def _attributes_initialization(
            self,
            ref_pc: Union[str, Path],
            target_pc: Union[str, Path]
        ) -> None:
        """Initialize common instance attributes.
        
        Parameters
        ----------
        ref_pc : `Union[str, Path]`
            Full path of the reference point cloud.
        target_pc : `Union[str, Path]`
            Full path of the target point.
        """
        self._ref_pc = ref_pc
        self._target_pc = target_pc

    def _get_log_header(self) -> None:
        """Log the version of PCC Arena and the path of two point cloud.
        """
        self._attributes_validator()
        
        lines = [
            f"PCC-Arena Evaluator {__version__}",
            f"ref_pc: {self._ref_pc}",
            f"target_pc: {self._target_pc}",
            "\n",
        ]
        
        self._results += lines

    def _get_processing_time_and_filesize(
            self,
            enc_t: float,
            dec_t: float,
            bin_files: list[Union[str, Path]]
        ) -> None:
        """Log processing time (encoding and decoding) and encoded 
        binary size.
        
        Parameters
        ----------
        enc_t : `float`
            Total encoding time.
        dec_t : `float`
            Total decoding time.
        bin_files : `list[Union[str, Path]]`
            List of the full path of the encoded binary file. Used for 
            calculate the compression ratio and bpp.
        """
        self._attributes_validator()
        
        cloud = PyntCloud.from_file(str(self._ref_pc))
        num_points = len(cloud.points['x'])

        ref_pc_size = Path(self._ref_pc).stat().st_size / 1000  # kB
        total_bin_size = (
            sum(Path(bin_f).stat().st_size for bin_f in bin_files) / 1000
        )  # kB
        compression_ratio = total_bin_size / ref_pc_size  # kB
        bpp = (total_bin_size * 1000 * 8) / num_points

        lines = [
            f"========== Time & Binary Size ==========",
            f"Encoding time (s)           : {enc_t:0.4f}",
            f"Decoding time (s)           : {dec_t:0.4f}",
            f"Source point cloud size (kB): {ref_pc_size}",
            f"Total binary files size (kB): {total_bin_size}",
            f"Compression ratio           : {compression_ratio}",
            f"bpp (bits per point)        : {bpp}",
            "\n",
        ]

        self._results += lines

    def _attributes_validator(self) -> None:
        # if None in list(self._ref_pc, self._target_pc, self._evl_log):
        #     logger.warning(
        #         f"Inherited metric class has to call ``{self._attributes_initialization.__name__}``"
        #     )
        try:
            self._ref_pc
            self._target_pc
        except AttributeError:
            logger.warning(
                f"Inherited metric class has to call "
                f"``{self._attributes_initialization.__name__}`` before "
                f"calling ``{self.calculate_and_log.__name__}``"
            )
            raise AttributeError

class ViewIndependentMetrics(BaseMetrics):
    """Class for evaluating view independent metrics of given point 
    clouds.
    
    View Independent Metrics:
        ACD (1->2), ACD (2->1),
        CD,
        CD-PSNR,
        Hausdorff,
        Y-CPSNR, U-CPSNR, V-CPSNR,
        Hybrid geo-color
    """
    
    def __init__(self) -> None:
        super().__init__()
        self._pc_error_bin = (
            Path(__file__)
            .parent.joinpath("mpeg-pcc-dmetric-master/test/pc_error")
            .resolve()
        )

    def evaluate(
            self,
            ref_pc: Union[str, Path],
            target_pc: Union[str, Path],
            color: int = 0,
            resolution: int = None,
            enc_t: float = None,
            dec_t: float = None,
            bin_files: list[Union[str, Path]] = None
        ) -> str:
        """Run the evaluation and generate the formatted evaluation 
        results.
        
        Parameters
        ----------
        ref_pc : `Union[str, Path]`
            Full path of the reference point cloud. Use point cloud with
            normal to calculate the p2plane metrics.
        target_pc : `Union[str, Path]`
            Full path of the target point.
        color : `int`, optional
            1 for calculating color metric, 0 otherwise. Defaults to 0.
        resolution : `int`, optional
            Maximum NN distance of the ``ref_pc``. If the resolution is 
            not specified, it will be calculated on the fly. Defaults to
            None.
        enc_t : `float`, optional
            Total encoding time. Defaults to None.
        dec_t : `float`, optional
            Total decoding time. Defaults to None.
        bin_files : `list[Union[str, Path]]`, optional
            List of the full path of the encoded binary file. Used for 
            calculate the compression ratio and bpp.
        
        Returns
        -------
        `str`
            The formatted evaluation results.
        """
        self._attributes_initialization(ref_pc, target_pc)
        self._color = color
        self._resolution = resolution
        
        self._get_log_header()

        # check if any of the values below is not initialized
        if None in [enc_t, dec_t, bin_files]:
            pass
        else:
            self._get_processing_time_and_filesize(
                enc_t, dec_t, bin_files
            )

        self._get_quality_metrics()
        
        ret = '\n'.join(self._results)
        
        return ret

    def _get_quality_metrics(self)-> None:
        """Calculate and parse the results of quality metrics from
        pc_error.
        """
        ret = self._pc_error_wrapper()

        chosen_metrics = [
            'ACD1      (p2point): ',
            'ACD2      (p2point): ',
            'CD        (p2point): ',
            'CD,PSNR   (p2point): ',
            'h.        (p2point): ',
            'ACD1      (p2plane): ',
            'ACD2      (p2plane): ',
            'CD        (p2plane): ',
            'CD,PSNR   (p2plane): ',
            'h.        (p2plane): ',
        ]
        if self._color == 1:
            chosen_metrics += [
                'c[0],PSNRF         : ',
                'c[1],PSNRF         : ',
                'c[2],PSNRF         : ',
                'hybrid geo-color   : ',
            ]

        chosen_metrics = [re.escape(pattern) for pattern in chosen_metrics]

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
                found_val.append('nan')

        assert len(found_val) == len(chosen_metrics)

        lines = [
            f"========== Objective Quality ===========",
            f"Asym. Chamfer dist. (1->2) p2pt: {found_val[0]}",
            f"Asym. Chamfer dist. (2->1) p2pt: {found_val[1]}",
            f"Chamfer dist.              p2pt: {found_val[2]}",
            f"CD-PSNR (dB)               p2pt: {found_val[3]}",
            f"Hausdorff distance         p2pt: {found_val[4]}",
            f"----------------------------------------",
            f"Asym. Chamfer dist. (1->2) p2pl: {found_val[5]}",
            f"Asym. Chamfer dist. (2->1) p2pl: {found_val[6]}",
            f"Chamfer dist.              p2pl: {found_val[7]}",
            f"CD-PSNR (dB)               p2pl: {found_val[8]}",
            f"Hausdorff distance         p2pl: {found_val[9]}",
        ]
        if self._color == 1:
            lines += [
                f"----------------------------------------",
                f"Y-CPSNR (dB)                   : {found_val[10]}",
                f"U-CPSNR (dB)                   : {found_val[11]}",
                f"V-CPSNR (dB)                   : {found_val[12]}",
                "\n",
                f"============== QoE Metric ==============",
                f"Hybrid geo-color               : {found_val[13]}",
                "\n",
            ]

        self._results += lines

    def _pc_error_wrapper(self) -> str:
        """Wrapper of the metric software, which modifies the formulas 
        and adds new metrics based on mpeg-pcc-dmetric.

        Returns
        -------
        `str`
            The result of objective quality metrics.
        """
        # [TODO]
        # Integrate findMaxNNdistance into mpeg-pcc-dmetric
        if self._resolution is None:
            self._resolution = findMaxNNdistance(self._ref_pc)

        cmd = [
            self._pc_error_bin,
            f'--fileA={self._ref_pc}',
            f'--fileB={self._target_pc}',
            f'--color={self._color}',
            '--hausdorff=1',
            f'--resolution={self._resolution}',
        ]

        ret = sp.run(cmd, capture_output=True, universal_newlines=True)

        return ret.stdout
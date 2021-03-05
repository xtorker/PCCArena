import re
import logging
from pathlib import Path
import subprocess as sp

from pyntcloud import PyntCloud

from _version import __version__

logger = logging.getLogger(__name__)

class MetricLogger():
    def __init__(
        self,
        ref_pc,
        target_pc,
        evl_log,
        pre_t=None,
        enc_t=None,
        dec_t=None,
        post_t=None,
        bin_files=None,
        color=0,
        resolution=1024
    ):
        self.ref_pc = ref_pc
        self.bin_files = bin_files
        self.target_pc = target_pc
        self.evl_log = evl_log
        self.pre_t = pre_t
        self.enc_t = enc_t
        self.dec_t = dec_t
        self.post_t = post_t
        self.color = color
        self.resolution = resolution

    def log_initializer(self):
        lines = [
            f"PCC-Arena Evaluator {__version__}",
            f"ref_pc: {self.ref_pc}",
            f"target_pc: {self.target_pc}",
            "\n"
        ]
        with open(self.evl_log, 'w') as f:
            f.writelines('\n'.join(lines))

    def log_time_and_filesize(self):

        cloud = PyntCloud.from_file(str(self.ref_pc))
        num_points = len(cloud.points['x'])

        ref_pc_size = Path(self.ref_pc).stat().st_size / 1000 # kB
        total_bin_size = sum(Path(bin_f).stat().st_size for bin_f in self.bin_files) / 1000 # kB
        compression_ratio = total_bin_size / ref_pc_size # kB
        bpp = (total_bin_size * 1000 * 8) / num_points

        lines = [
            f"========== Time & Binary Size ==========",
            f"Pre-processing time:          {self.pre_t:0.4f}",
            f"Encoding time:                {self.enc_t:0.4f}",
            f"Decoding time:                {self.dec_t:0.4f}",
            f"Post-processing time:         {self.post_t:0.4f}",
            f"Source point cloud size (kB): {ref_pc_size}",
            f"Total binary files size (kB): {total_bin_size}",
            f"bpp (bits per point):         {bpp}",
            "\n"
        ]

        with open(self.evl_log, 'a') as f:
            f.writelines('\n'.join(lines))

    def objective_quality(self):
        ret = self.pc_error_wrapper()

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
            'hybrid geo-color   : '
        ]

        found_val = []

        for pattern in chosen_metrics:
            isfound = False
            for line in ret.splitlines():
                m = re.search(f'(?<={pattern}).*', line)
                if(m):
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
            "\n"
        ]

        with open(self.evl_log, 'a') as f:
            f.writelines('\n'.join(lines))

    def pc_error_wrapper(self):
        '''
        Wrapper of the metric software, modified based on mpeg-pcc-dmetric.

        Parameters:
            ref_pc (str or PosixPath): Reference (source) point cloud.
            target_pc (str or PosixPath): Target (reconstructed/decoded) point cloud.

        Optionals:
            color (int): Calculate color distortion or not. (0: false, 1: true)
            resolution (int): Resolution (scale) of the point cloud.

        Returns:
            string : Logs of objective quality.
        '''

        # metric software modified based on mpeg-pcc-dmetric
        pc_error_bin = Path(__file__).parent.joinpath("mpeg-pcc-dmetric-master/test/pc_error").resolve()

        cmd = [
            pc_error_bin,
            f'--fileA={self.ref_pc}',
            f'--fileB={self.target_pc}',
            f'--color={self.color}',
            f'--resolution={self.resolution}',
            '--hausdorff=1'
        ]

        ret = sp.run(cmd, stdout=sp.PIPE, stderr=sp.DEVNULL, universal_newlines=True)

        return ret.stdout

    def evaluate_all(self):
        self.log_initializer()

        # check if any of the values below is not initialized
        if None in [self.pre_t, self.enc_t, self.dec_t, self.post_t, self.bin_files]:
            pass
        else:
            self.log_time_and_filesize()

        self.objective_quality()
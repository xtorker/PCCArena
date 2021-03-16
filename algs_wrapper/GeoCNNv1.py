from pathlib import Path
from typing import Union

from algs_wrapper.base import Base
from utils.processing import execute_cmd

class GeoCNNv1(Base):
    def __init__(self):
        super().__init__()

    def encode(self, in_pcfile, bin_file):
        input_dir = Path(in_pcfile).parent
        input_pattern = Path(in_pcfile).name
        output_dir = Path(bin_file).parent
        cmd = [
            self._algs_cfg['python'],
            self._algs_cfg['encoder'],
            input_dir,
            input_pattern,
            output_dir,
            self._algs_cfg[self.rate]['checkpoint_dir'],
            '--resolution', self._pc_scale,
            '--preprocess_threads', '1',
        ]
        
        assert execute_cmd(cmd, cwd=self._algs_cfg['rootdir'])

    def decode(self, bin_file, out_pcfile):
        input_dir = Path(bin_file).parent
        input_pattern = Path(bin_file).name
        output_dir = Path(out_pcfile).parent
        cmd = [
            self._algs_cfg['python'],
            self._algs_cfg['decoder'],
            input_dir,
            input_pattern,
            output_dir,
            self._algs_cfg[self.rate]['checkpoint_dir'],
            '--preprocess_threads', '1',
        ]

        assert execute_cmd(cmd, cwd=self._algs_cfg['rootdir'])

    # GeoCNNv1 directly adds .bin after the point cloud file name, and 
    # adds .ply after the binary file.
    # e.g. 
    #       in_pcfile: test.ply
    #       bin_file: test.ply.bin
    #       out_pcfile: test.ply.bin.ply
    # With loss of generality on input point cloud data type, the 
    # config file of GeoCNNv1 assign bin_suffix as .bin
    # We then deal with the correct bin_suffix here.
    def _set_filepath(
            self, 
            pcfile: Union[str, Path],
            src_dir: Union[str, Path],
            nor_dir: Union[str, Path],
            exp_dir: Union[str, Path]
        ) -> tuple[str, str, str, str, str]:
        """Set up the experiment file paths, including encoded binary, 
        decoded point cloud, and evaluation log.
        
        Parameters
        ----------
        pcfile : `Union[str, Path]`
            The relative path of input point cloud.
        src_dir : `Union[str, Path]`
            The directory of input point cloud.
        nor_dir : `Union[str, Path]`
            The directory of input point cloud with normal. (Necessary 
            for p2plane metrics.)
        exp_dir : `Union[str, Path]`
            The directory to store experiments results.
        
        Returns
        -------
        `tuple[str, str, str, str, str]`
            The full path of input point cloud, input point cloud with 
            normal, encoded binary file, output point cloud, and 
            evaluation log file.
        """
        bin_suffix = Path(pcfile).suffix + self._algs_cfg['bin_suffix']
        out_pc_suffix = (
            Path(pcfile).suffix 
            + self._algs_cfg['bin_suffix'] 
            + Path(pcfile).suffix
        )
        
        in_pcfile = Path(src_dir).joinpath(pcfile)
        nor_pcfile = Path(nor_dir).joinpath(pcfile)
        bin_file = (
            Path(exp_dir)
            .joinpath('bin', pcfile).with_suffix(bin_suffix)
        )
        out_pcfile = (
            Path(exp_dir)
            .joinpath('dec', pcfile).with_suffix(out_pc_suffix)
        )
        evl_log = Path(exp_dir).joinpath('evl', pcfile).with_suffix('.log')
        
        bin_file.parent.mkdir(parents=True, exist_ok=True)
        out_pcfile.parent.mkdir(parents=True, exist_ok=True)
        evl_log.parent.mkdir(parents=True, exist_ok=True)

        return (
            str(in_pcfile), str(nor_pcfile), str(bin_file), str(out_pcfile), 
            str(evl_log)
        )


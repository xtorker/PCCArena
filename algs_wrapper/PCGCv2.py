from algs_wrapper.base import Base
from utils.processing import execute_cmd

class PCGCv2(Base):
    def __init__(self):
        super().__init__()

    def encode(self, in_pcfile, bin_file, gpu_id):
        cmd = [
            self._algs_cfg['python'],
            self._algs_cfg['test_script'],
            'compress',
            in_pcfile,
            bin_file,
            '--ckptdir', self._algs_cfg[self.rate]['ckptdir'],
            '--voxel_size', str(self._algs_cfg[self.rate]['voxel_size'])
        ]
        
        assert execute_cmd(cmd, cwd=self._algs_cfg['rootdir'], gpu_id=gpu_id)

    def decode(self, bin_file, out_pcfile, gpu_id):
        cmd = [
            self._algs_cfg['python'],
            self._algs_cfg['test_script'],
            'decompress',
            bin_file,
            out_pcfile,
            '--ckptdir', self._algs_cfg[self.rate]['ckptdir'],
            '--voxel_size', str(self._algs_cfg[self.rate]['voxel_size']),
            '--rho', str(self._algs_cfg[self.rate]['rho'])
        ]

        assert execute_cmd(cmd, cwd=self._algs_cfg['rootdir'], gpu_id=gpu_id)
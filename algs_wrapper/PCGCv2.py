from algs_wrapper.base import Base

class PCGCv2(Base):
    def __init__(self):
        super().__init__()

    def make_encode_cmd(self, in_pcfile, bin_file):
        cmd = [
            self._algs_cfg['python'],
            self._algs_cfg['test_script'],
            'compress',
            in_pcfile,
            bin_file,
            '--ckptdir', self._algs_cfg[self.rate]['ckptdir'],
            '--voxel_size', str(self._algs_cfg[self.rate]['voxel_size'])
        ]
        
        return cmd

    def make_decode_cmd(self, bin_file, out_pcfile):
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

        return cmd
from algs_wrapper.base import Base

class Draco(Base):
    def __init__(self):
        super().__init__()

    def make_encode_cmd(self, in_pcfile, bin_file):
        cmd = [
            self._algs_cfg['encoder'],
            '-i', in_pcfile,
            '-o', bin_file,
            '-point_cloud',
            '-qp', str(self._algs_cfg[self.rate]['qp']),
            '-qt', str(self._algs_cfg[self.rate]['qt']),
            '-qn', str(self._algs_cfg[self.rate]['qn']),
            '-qg', str(self._algs_cfg[self.rate]['qg']),
            '-cl', str(self._algs_cfg[self.rate]['cl'])
        ]
        
        return cmd

    def make_decode_cmd(self, bin_file, out_pcfile):
        cmd = [
            self._algs_cfg['decoder'],
            '-i', bin_file,
            '-o', out_pcfile
        ]

        return cmd

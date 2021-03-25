from algs_wrapper.base import Base

class GeoCNNv2(Base):
    def __init__(self):
        super().__init__()

    def make_encode_cmd(self, in_pcfile, bin_file):
        cmd = [
            self._algs_cfg['python'],
            self._algs_cfg['encoder'],
            '--input_files', in_pcfile,
            '--output_files', bin_file,
            '--checkpoint_dir', self._algs_cfg[self.rate]['checkpoint_dir'],
            '--model_config', self._algs_cfg['model_config'],
            '--opt_metrics', self._algs_cfg['opt_metrics'],
            '--resolution', str(self._pc_scale)
        ]
        
        return cmd

    def make_decode_cmd(self, bin_file, out_pcfile):
        cmd = [
            self._algs_cfg['python'],
            self._algs_cfg['decoder'],
            '--input_files', bin_file,
            '--output_files', out_pcfile,
            '--checkpoint_dir', self._algs_cfg[self.rate]['checkpoint_dir'],
            '--model_config', self._algs_cfg['model_config']
        ]

        return cmd



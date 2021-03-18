from algs_wrapper.base import Base
from utils.processing import execute_cmd

class GeoCNNv2(Base):
    def __init__(self):
        super().__init__()

    def encode(self, in_pcfile, bin_file, gpu_id):
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
        
        assert execute_cmd(cmd, cwd=self._algs_cfg['rootdir'], gpu_id=gpu_id)

    def decode(self, bin_file, out_pcfile, gpu_id):
        cmd = [
            self._algs_cfg['python'],
            self._algs_cfg['decoder'],
            '--input_files', bin_file,
            '--output_files', out_pcfile,
            '--checkpoint_dir', self._algs_cfg[self.rate]['checkpoint_dir'],
            '--model_config', self._algs_cfg['model_config']
        ]

        assert execute_cmd(cmd, cwd=self._algs_cfg['rootdir'], gpu_id=gpu_id)



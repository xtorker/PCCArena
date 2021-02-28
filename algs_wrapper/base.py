import abc
import yaml
from pathlib import Path

from utils.file_io import glob_filename, glob_filepath

class Base(metaclass=abc.ABCMeta):
    def __init__(self, algs_cfg_file):
        with open(algs_cfg_file, 'r') as f:
            self.algs_cfg = yaml.load(f, Loader=yaml.FullLoader)
        self.ds_cfg_file = Path(__file__).parent.joinpath("../cfgs/datasets.yml").resolve()
        self.exp_dir = "/home/chenghao/PCC_Arena"
        self.dataset_dir = "/mnt/data6/chenghao/PCC_datasets/ShapeNet/geo_only_scale1024"

    @abc.abstractmethod
    def encode(self):
        return NotImplemented

    @abc.abstractmethod
    def decode(self):
        return NotImplemented

    def set_filepath(self, pcfile):
        in_pcfile = Path(self.dataset_dir).joinpath(pcfile)
        binfile = Path(self.exp_dir).joinpath('bin', pcfile).with_suffix(self.algs_cfg['bin_suffix'])
        out_pcfile = Path(self.exp_dir).joinpath('dec', pcfile)
        evl_log = Path(self.exp_dir).joinpath('evl', pcfile).with_suffix('.log')
        
        in_pcfile.mkdir(parents=True, exist_ok=True)
        binfile.mkdir(parents=True, exist_ok=True)
        out_pcfile.mkdir(parents=True, exist_ok=True)
        evl_log.mkdir(parents=True, exist_ok=True)

        return in_pcfile, binfile, out_pcfile, evl_log

    def run(self, pcfile):
        in_pcfile, binfile, out_pcfile, evl_log = self.set_filepath(pcfile)
        
        self.encode(in_pcfile, binfile)

        self.decode(binfile, out_pcfile)


    def run_dataset(self, ds_name, ds_type, ds_cfg_file=None):
        # if ds_cfg_file is not specify, use the default path initalized in __init__
        if ds_cfg_file is None:
            ds_cfg_file = self.ds_cfg_file
        
        with open(ds_cfg_file, 'r') as f:
            ds_cfg = yaml.load(f, Loader=yaml.FullLoader)
        
        self.dataset_dir = ds_cfg[ds_name][ds_type]['dataset_dir']

        pc_files = glob_filename(
                       ds_cfg[ds_name][ds_type]['dataset_dir'],
                       ds_cfg[ds_name][ds_type]['test_pattern']
                   )
        infile = ds_cfg[ds_name][ds_type]['']
        
        print(ds_cfg[ds_name][ds_type]['train_pattern'])
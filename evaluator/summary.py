import re
import csv
import logging
import numpy as np
from pathlib import Path
from typing import Union
from collections import defaultdict

from scipy.io import savemat

from utils.file_io import glob_file
from utils._version import __version__

logger = logging.getLogger(__name__)

# [TODO]
# Find a better way handle the log parsing and writing
# Current version is hard to maintain.
def summarize_one_setup(log_dir: Union[str, Path]) -> None:
    """Summarize the evaluation results for an experimental setup.
    
    Parameters
    ----------
    log_dir : `Union[str, Path]`
        The directory of the evaluation log files.
    """
    log_files = glob_file(log_dir, '**/*.log', fullpath=True)

    chosen_metrics = [
        'Encoding time (s)           : ',
        'Decoding time (s)           : ',
        'Source point cloud size (kB): ',
        'Total binary files size (kB): ',
        'Compression ratio           : ',
        'bpp (bits per point)        : ',
        'Asym. Chamfer dist. (1->2) p2pt: ',
        'Asym. Chamfer dist. (2->1) p2pt: ',
        'Chamfer dist.              p2pt: ',
        'CD-PSNR (dB)               p2pt: ',
        'Hausdorff distance         p2pt: ',
        'Asym. Chamfer dist. (1->2) p2pl: ',
        'Asym. Chamfer dist. (2->1) p2pl: ',
        'Chamfer dist.              p2pl: ',
        'CD-PSNR (dB)               p2pl: ',
        'Hausdorff distance         p2pl: ',
        'Y-CPSNR (dB)                   : ',
        'U-CPSNR (dB)                   : ',
        'V-CPSNR (dB)                   : ',
        'Hybrid geo-color               : ',
    ]

    # escape special characters
    chosen_metrics = [re.escape(pattern) for pattern in chosen_metrics]
    
    max_val = {
        'Y-CPSNR (dB)                   : ': 100,
        'U-CPSNR (dB)                   : ': 100,
        'V-CPSNR (dB)                   : ': 100
    }
    
    found_val = [ [] for i in range(len(chosen_metrics))]

    for log in log_files:
        with open(log, 'r') as f:
            for line in f:
                for idx, pattern in enumerate(chosen_metrics):
                    m = re.search(f'(?<={pattern}).*', line)
                    if m:
                        if m.group() == 'inf':
                            # [TODO]
                            # fix it with dict(metric, pattern)
                            found_val[idx].append(float(100))
                        elif m.group() == 'nan':
                            found_val[idx].append(np.nan)
                        else:
                            found_val[idx].append(float(m.group()))

    summary_log_path = (
        Path(log_dir).parent
        .joinpath(
            f'{Path(log_dir).parents[2].stem}_'
            f'{Path(log_dir).parents[1].stem}_'
            f'{Path(log_dir).parents[0].stem}_'
            'summary.log'
        )
    )

    with open(summary_log_path, 'w') as f:
        lines = [
            f"PCC-Arena Evaluator {__version__}",
            f"Summary of the log directory: {log_dir}"
            "\n",
            f"***** Average *****",
            f"========== Time & Binary Size ==========",
            f"avg. Encoding time (s)           : {np.mean(found_val[0])}",
            f"avg. Decoding time (s)           : {np.mean(found_val[1])}",
            f"avg. Source point cloud size (kB): {np.mean(found_val[2])}",
            f"avg. Total binary files size (kB): {np.mean(found_val[3])}",
            f"avg. Compression ratio           : {np.mean(found_val[4])}",
            f"avg. bpp (bits per point)        : {np.mean(found_val[5])}",
            "\n",
            f"========== Objective Quality ===========",
            f"avg. Asym. Chamfer dist. (1->2) p2pt: {np.mean(found_val[6])}",
            f"avg. Asym. Chamfer dist. (2->1) p2pt: {np.mean(found_val[7])}",
            f"avg. Chamfer dist.              p2pt: {np.mean(found_val[8])}",
            f"avg. CD-PSNR (dB)               p2pt: {np.mean(found_val[9])}",
            f"avg. Hausdorff distance         p2pt: {np.mean(found_val[10])}",
            f"----------------------------------------",
            f"avg. Asym. Chamfer dist. (1->2) p2pl: {np.mean(found_val[11])}",
            f"avg. Asym. Chamfer dist. (2->1) p2pl: {np.mean(found_val[12])}",
            f"avg. Chamfer dist.              p2pl: {np.mean(found_val[13])}",
            f"avg. CD-PSNR (dB)               p2pl: {np.mean(found_val[14])}",
            f"avg. Hausdorff distance         p2pl: {np.mean(found_val[15])}",
            f"----------------------------------------",
            f"avg. Y-CPSNR (dB)                   : {np.mean(found_val[16])}",
            f"avg. U-CPSNR (dB)                   : {np.mean(found_val[17])}",
            f"avg. V-CPSNR (dB)                   : {np.mean(found_val[18])}",
            "\n",
            f"============== QoE Metric ==============",
            f"avg. Hybrid geo-color               : {np.mean(found_val[19])}",
            "\n",
        ]
        lines += [
            "\n",
            f"***** Standard Deviation *****",
            f"========== Time & Binary Size ==========",
            f"stdev. Encoding time (s)           : {np.std(found_val[0])}",
            f"stdev. Decoding time (s)           : {np.std(found_val[1])}",
            f"stdev. Source point cloud size (kB): {np.std(found_val[2])}",
            f"stdev. Total binary files size (kB): {np.std(found_val[3])}",
            f"stdev. Compression ratio           : {np.std(found_val[4])}",
            f"stdev. bpp (bits per point)        : {np.std(found_val[5])}",
            "\n",
            f"========== Objective Quality ===========",
            f"stdev. Asym. Chamfer dist. (1->2) p2pt: {np.std(found_val[6])}",
            f"stdev. Asym. Chamfer dist. (2->1) p2pt: {np.std(found_val[7])}",
            f"stdev. Chamfer dist.              p2pt: {np.std(found_val[8])}",
            f"stdev. CD-PSNR (dB)               p2pt: {np.std(found_val[9])}",
            f"stdev. Hausdorff distance         p2pt: {np.std(found_val[10])}",
            f"----------------------------------------",
            f"stdev. Asym. Chamfer dist. (1->2) p2pl: {np.std(found_val[11])}",
            f"stdev. Asym. Chamfer dist. (2->1) p2pl: {np.std(found_val[12])}",
            f"stdev. Chamfer dist.              p2pl: {np.std(found_val[13])}",
            f"stdev. CD-PSNR (dB)               p2pl: {np.std(found_val[14])}",
            f"stdev. Hausdorff distance         p2pl: {np.std(found_val[15])}",
            f"----------------------------------------",
            f"stdev. Y-CPSNR (dB)                   : {np.std(found_val[16])}",
            f"stdev. U-CPSNR (dB)                   : {np.std(found_val[17])}",
            f"stdev. V-CPSNR (dB)                   : {np.std(found_val[18])}",
            "\n",
            f"============== QoE Metric ==============",
            f"stdev. Hybrid geo-color               : {np.std(found_val[19])}",
        ]
        lines += [
            "\n",
            f"***** Maximum *****",
            f"========== Time & Binary Size ==========",
            f"max. Encoding time (s)           : {np.max(found_val[0])}",
            f"max. Decoding time (s)           : {np.max(found_val[1])}",
            f"max. Source point cloud size (kB): {np.max(found_val[2])}",
            f"max. Total binary files size (kB): {np.max(found_val[3])}",
            f"max. Compression ratio           : {np.max(found_val[4])}",
            f"max. bpp (bits per point)        : {np.max(found_val[5])}",
            "\n",
            f"========== Objective Quality ===========",
            f"max. Asym. Chamfer dist. (1->2) p2pt: {np.max(found_val[6])}",
            f"max. Asym. Chamfer dist. (2->1) p2pt: {np.max(found_val[7])}",
            f"max. Chamfer dist.              p2pt: {np.max(found_val[8])}",
            f"max. CD-PSNR (dB)               p2pt: {np.max(found_val[9])}",
            f"max. Hausdorff distance         p2pt: {np.max(found_val[10])}",
            f"----------------------------------------",
            f"max. Asym. Chamfer dist. (1->2) p2pl: {np.max(found_val[11])}",
            f"max. Asym. Chamfer dist. (2->1) p2pl: {np.max(found_val[12])}",
            f"max. Chamfer dist.              p2pl: {np.max(found_val[13])}",
            f"max. CD-PSNR (dB)               p2pl: {np.max(found_val[14])}",
            f"max. Hausdorff distance         p2pl: {np.max(found_val[15])}",
            f"----------------------------------------",
            f"max. Y-CPSNR (dB)                   : {np.max(found_val[16])}",
            f"max. U-CPSNR (dB)                   : {np.max(found_val[17])}",
            f"max. V-CPSNR (dB)                   : {np.max(found_val[18])}",
            "\n",
            f"============== QoE Metric ==============",
            f"max. Hybrid geo-color               : {np.max(found_val[19])}",
        ]
        lines += [
            "\n",
            f"***** Minimum *****",
            f"========== Time & Binary Size ==========",
            f"min. Encoding time (s)           : {np.min(found_val[0])}",
            f"min. Decoding time (s)           : {np.min(found_val[1])}",
            f"min. Source point cloud size (kB): {np.min(found_val[2])}",
            f"min. Total binary files size (kB): {np.min(found_val[3])}",
            f"min. Compression ratio           : {np.min(found_val[4])}",
            f"min. bpp (bits per point)        : {np.min(found_val[5])}",
            "\n",
            f"========== Objective Quality ===========",
            f"min. Asym. Chamfer dist. (1->2) p2pt: {np.min(found_val[6])}",
            f"min. Asym. Chamfer dist. (2->1) p2pt: {np.min(found_val[7])}",
            f"min. Chamfer dist.              p2pt: {np.min(found_val[8])}",
            f"min. CD-PSNR (dB)               p2pt: {np.min(found_val[9])}",
            f"min. Hausdorff distance         p2pt: {np.min(found_val[10])}",
            f"----------------------------------------",
            f"min. Asym. Chamfer dist. (1->2) p2pl: {np.min(found_val[11])}",
            f"min. Asym. Chamfer dist. (2->1) p2pl: {np.min(found_val[12])}",
            f"min. Chamfer dist.              p2pl: {np.min(found_val[13])}",
            f"min. CD-PSNR (dB)               p2pl: {np.min(found_val[14])}",
            f"min. Hausdorff distance         p2pl: {np.min(found_val[15])}",
            f"----------------------------------------",
            f"min. Y-CPSNR (dB)                   : {np.min(found_val[16])}",
            f"min. U-CPSNR (dB)                   : {np.min(found_val[17])}",
            f"min. V-CPSNR (dB)                   : {np.min(found_val[18])}",
            "\n",
            f"============== QoE Metric ==============",
            f"min. Hybrid geo-color               : {np.min(found_val[19])}",
        ]
        f.writelines('\n'.join(lines))
    return 0

def summarize_all_to_csv(exp_dir):
    # [TODO]
    # Unfinished
    summary_log_files = sorted(
        glob_file(exp_dir, '*_summary.log', fullpath=True)
    )
    csvfile = Path(exp_dir).joinpath('summary.csv')
    
    chosen_metrics = [
        'encT',
        'decT',
        'bpp',
        'acd12_p2pt',
        'acd21_p2pt',
        'cd_p2pt',
        'cdpsnr_p2pt',
        'h_p2pt',
        'acd12_p2pl',
        'acd21_p2pl',
        'cd_p2pl',
        'cdpsnr_p2pl',
        'h_p2pl',
        'y_cpsnr',
        'u_cpsnr',
        'v_cpsnr',
        'hybrid'
    ]
    
    patterns = {
        'encT':        'Encoding time (s)           : ',
        'decT':        'Decoding time (s)           : ',
        'bpp':         'bpp (bits per point)        : ',
        'acd12_p2pt':  'Asym. Chamfer dist. (1->2) p2pt: ',
        'acd21_p2pt':  'Asym. Chamfer dist. (2->1) p2pt: ',
        'cd_p2pt':     'Chamfer dist.              p2pt: ',
        'cdpsnr_p2pt': 'CD-PSNR (dB)               p2pt: ',
        'h_p2pt':      'Hausdorff distance         p2pt: ',
        'acd12_p2pl':  'Asym. Chamfer dist. (1->2) p2pl: ',
        'acd21_p2pl':  'Asym. Chamfer dist. (2->1) p2pl: ',
        'cd_p2pl':     'Chamfer dist.              p2pl: ',
        'cdpsnr_p2pl': 'CD-PSNR (dB)               p2pl: ',
        'h_p2pl':      'Hausdorff distance         p2pl: ',
        'y_cpsnr':     'Y-CPSNR (dB)                   : ',
        'u_cpsnr':     'U-CPSNR (dB)                   : ',
        'v_cpsnr':     'V-CPSNR (dB)                   : ',
        'hybrid':      'Hybrid geo-color               : ',
    }
    # escape special characters
    for key in patterns:
        patterns[key] = re.escape(patterns[key])

    with open(csvfile, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        header = [
            'PCC_algs',
            'Datasets',
            'Rate',
            'Avg. Encoding Time',
            'Avg. Decoding Time',
            'Avg. bpp',
            'Avg. Asym. Chamfer Distance 1->2 (p2pt)',
            'Avg. Asym. Chamfer Distance 2->1 (p2pt)',
            'Avg. Chamfer Distance (p2pt)',
            'Avg. CD-PSNR (p2pt)',
            'Avg. Hausdorff Distance (p2pt)',
            'Avg. Asym. Chamfer Distance 1->2 (p2pl)',
            'Avg. Asym. Chamfer Distance 2->1 (p2pl)',
            'Avg. Chamfer Distance (p2pl)',
            'Avg. CD-PSNR (p2pl)',
            'Avg. Hausdorff Distance (p2pl)',
            'Avg. Y-CPSNR',
            'Avg. U-CPSNR',
            'Avg. V-CPSNR',
            'Avg. Hybrid Geo-Color',
            'Stdev. Encoding Time',
            'Stdev. Decoding Time',
            'Stdev. bpp',
            'Stdev. Asym. Chamfer Distance 1->2 (p2pt)',
            'Stdev. Asym. Chamfer Distance 2->1 (p2pt)',
            'Stdev. Chamfer Distance (p2pt)',
            'Stdev. CD-PSNR (p2pt)',
            'Stdev. Hausdorff Distance (p2pt)',
            'Stdev. Asym. Chamfer Distance 1->2 (p2pl)',
            'Stdev. Asym. Chamfer Distance 2->1 (p2pl)',
            'Stdev. Chamfer Distance (p2pl)',
            'Stdev. CD-PSNR (p2pl)',
            'Stdev. Hausdorff Distance (p2pl)',
            'Stdev. Y-CPSNR',
            'Stdev. U-CPSNR',
            'Stdev. V-CPSNR',
            'Stdev. Hybrid Geo-Color',
            'Max. Encoding Time',
            'Max. Decoding Time',
            'Max. bpp',
            'Max. Asym. Chamfer Distance 1->2 (p2pt)',
            'Max. Asym. Chamfer Distance 2->1 (p2pt)',
            'Max. Chamfer Distance (p2pt)',
            'Max. CD-PSNR (p2pt)',
            'Max. Hausdorff Distance (p2pt)',
            'Max. Asym. Chamfer Distance 1->2 (p2pl)',
            'Max. Asym. Chamfer Distance 2->1 (p2pl)',
            'Max. Chamfer Distance (p2pl)',
            'Max. CD-PSNR (p2pl)',
            'Max. Hausdorff Distance (p2pl)',
            'Max. Y-CPSNR',
            'Max. U-CPSNR',
            'Max. V-CPSNR',
            'Max. Hybrid Geo-Color',
            'Min. Encoding Time',
            'Min. Decoding Time',
            'Min. bpp',
            'Min. Asym. Chamfer Distance 1->2 (p2pt)',
            'Min. Asym. Chamfer Distance 2->1 (p2pt)',
            'Min. Chamfer Distance (p2pt)',
            'Min. CD-PSNR (p2pt)',
            'Min. Hausdorff Distance (p2pt)',
            'Min. Asym. Chamfer Distance 1->2 (p2pl)',
            'Min. Asym. Chamfer Distance 2->1 (p2pl)',
            'Min. Chamfer Distance (p2pl)',
            'Min. CD-PSNR (p2pl)',
            'Min. Hausdorff Distance (p2pl)',
            'Min. Y-CPSNR',
            'Min. U-CPSNR',
            'Min. V-CPSNR',
            'Min. Hybrid Geo-Color',
        ]
        csvwriter.writerow(header)
        for log in summary_log_files:
            alg_name = Path(log).parents[2].stem
            ds_name = Path(log).parents[1].stem
            rate = Path(log).parents[0].stem
            
            with open(log, 'r') as f:
                row = [alg_name, ds_name, rate]
                for line in f:
                    for metric in chosen_metrics:
                        m = re.search(f'(?<={patterns[metric]}).*', line)
                        if m:
                            row.append(m.group())
            csvwriter.writerow(row)

def summarize_all_to_mat(exp_dir):
    summary_log_files = glob_file(exp_dir, '*_summary.log', fullpath=True)
    ret = nested_dict()
    matfile = Path(exp_dir).joinpath('summary.mat')
    
    chosen_metrics = [
        'encT',
        'decT',
        'bpp',
        'cd_p2pt',
        'cdpsnr_p2pt',
        'h_p2pt',
        'cd_p2pl',
        'cdpsnr_p2pl',
        'h_p2pl',
        'y_cpsnr',
        'u_cpsnr',
        'v_cpsnr',
        'hybrid'
    ]
    
    patterns = {
        'encT':        'Encoding time (s)           : ',
        'decT':        'Decoding time (s)           : ',
        'bpp':         'bpp (bits per point)        : ',
        'cd_p2pt':     'Chamfer dist.              p2pt: ',
        'cdpsnr_p2pt': 'CD-PSNR (dB)               p2pt: ',
        'h_p2pt':      'Hausdorff distance         p2pt: ',
        'cd_p2pl':     'Chamfer dist.              p2pl: ',
        'cdpsnr_p2pl': 'CD-PSNR (dB)               p2pl: ',
        'h_p2pl':      'Hausdorff distance         p2pl: ',
        'y_cpsnr':     'Y-CPSNR (dB)                   : ',
        'u_cpsnr':     'U-CPSNR (dB)                   : ',
        'v_cpsnr':     'V-CPSNR (dB)                   : ',
        'hybrid':      'Hybrid geo-color               : ',
    }
    # escape special characters
    for key in patterns:
        patterns[key] = re.escape(patterns[key])

    for log in summary_log_files:
        alg_name = Path(log).parents[2].stem
        ds_name = Path(log).parents[1].stem
        rate = Path(log).parents[0].stem

        with open(log, 'r') as f:
            for line in f:
                for metric in chosen_metrics:
                    m = re.search(f'(?<={patterns[metric]}).*', line)
                    if m:
                        if m.group() == 'nan':
                            break
                        else:
                            # search for ["avg", "stdev", "max", and "min"]
                            statistic = re.search(f'.*(?=. {patterns[metric]})', line).group()
                            val = float(m.group())
                            # ret[alg_name][ds_name][rate][metric][statistic] = val
                            ret[statistic][metric][ds_name][alg_name][rate] = val
    savemat(matfile, ret)

def nested_dict():
    # https://stackoverflow.com/a/652226
    return defaultdict(nested_dict)
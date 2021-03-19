import re
import csv
import logging
import numpy as np
from pathlib import Path
from collections import defaultdict

from scipy.io import savemat

from utils.file_io import glob_file
from utils._version import __version__

logger = logging.getLogger(__name__)

# [TODO]
# Find a better way handle the log parsing and writing
# Current version is hard to maintain.

def summarize_one_setup(log_dir):
    log_files = glob_file(log_dir, '**/*.log', fullpath=True)

    chosen_metrics = [
        'Encoding time:                ',
        'Decoding time:                ',
        'Source point cloud size \(kB\): ',
        'Total binary files size \(kB\): ',
        'Compression ratio:            ',
        'bpp \(bits per point\):         ',
        'Asym. Chamfer dist. \(1->2\) p2pt: ',
        'Asym. Chamfer dist. \(2->1\) p2pt: ',
        'Chamfer dist.              p2pt: ',
        'CD-PSNR                    p2pt: ',
        'Hausdorff distance         p2pt: ',
        'Asym. Chamfer dist. \(1->2\) p2pl: ',
        'Asym. Chamfer dist. \(2->1\) p2pl: ',
        'Chamfer dist.              p2pl: ',
        'CD-PSNR                    p2pl: ',
        'Hausdorff distance         p2pl: ',
        'Y-CPSNR                        : ',
        'U-CPSNR                        : ',
        'V-CPSNR                        : ',
        'Hybrid geo-color               : ',
    ]
    
    max_val = {
        'Y-CPSNR                        : ': 100,
        'U-CPSNR                        : ': 100,
        'V-CPSNR                        : ': 100
    }
    
    found_val = [ [] for i in range(len(chosen_metrics))]

    for log in log_files:
        with open(log, 'r') as f:
            for line in f:
                for idx, pattern in enumerate(chosen_metrics):
                    m = re.search(f'(?<={pattern}).*', line)
                    if m:
                        if m.group() == 'inf':
                            found_val[idx].append(float(max_val[pattern]))
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
            f"avg. Encoding time:                {np.mean(found_val[0]):0.4f}",
            f"avg. Decoding time:                {np.mean(found_val[1]):0.4f}",
            f"avg. Source point cloud size (kB): {np.mean(found_val[2]):0.4f}",
            f"avg. Total binary files size (kB): {np.mean(found_val[3]):0.4f}",
            f"avg. Compression ratio:            {np.mean(found_val[4]):0.4f}",
            f"avg. bpp (bits per point):         {np.mean(found_val[5]):0.4f}",
            "\n",
            f"========== Objective Quality ===========",
            f"avg. Asym. Chamfer dist. (1->2) p2pt: {np.mean(found_val[6]):0.4f}",
            f"avg. Asym. Chamfer dist. (2->1) p2pt: {np.mean(found_val[7]):0.4f}",
            f"avg. Chamfer dist.              p2pt: {np.mean(found_val[8]):0.4f}",
            f"avg. CD-PSNR                    p2pt: {np.mean(found_val[9]):0.4f}",
            f"avg. Hausdorff distance         p2pt: {np.mean(found_val[10]):0.4f}",
            f"----------------------------------------",
            f"avg. Asym. Chamfer dist. (1->2) p2pl: {np.mean(found_val[11]):0.4f}",
            f"avg. Asym. Chamfer dist. (2->1) p2pl: {np.mean(found_val[12]):0.4f}",
            f"avg. Chamfer dist.              p2pl: {np.mean(found_val[13]):0.4f}",
            f"avg. CD-PSNR                    p2pl: {np.mean(found_val[14]):0.4f}",
            f"avg. Hausdorff distance         p2pl: {np.mean(found_val[15]):0.4f}",
            f"----------------------------------------",
            f"avg. Y-CPSNR                        : {np.mean(found_val[16]):0.4f}",
            f"avg. U-CPSNR                        : {np.mean(found_val[17]):0.4f}",
            f"avg. V-CPSNR                        : {np.mean(found_val[18]):0.4f}",
            "\n",
            f"============== QoE Metric ==============",
            f"avg. Hybrid geo-color               : {np.mean(found_val[19]):0.4f}",
            "\n",
        ]
        lines += [
            "\n",
            f"***** Standard Deviation *****",
            f"========== Time & Binary Size ==========",
            f"stdev. Encoding time:                {np.std(found_val[0]):0.4f}",
            f"stdev. Decoding time:                {np.std(found_val[1]):0.4f}",
            f"stdev. Source point cloud size (kB): {np.std(found_val[2]):0.4f}",
            f"stdev. Total binary files size (kB): {np.std(found_val[3]):0.4f}",
            f"stdev. Compression ratio:            {np.std(found_val[4]):0.4f}",
            f"stdev. bpp (bits per point):         {np.std(found_val[5]):0.4f}",
            "\n",
            f"========== Objective Quality ===========",
            f"stdev. Asym. Chamfer dist. (1->2) p2pt: {np.std(found_val[6]):0.4f}",
            f"stdev. Asym. Chamfer dist. (2->1) p2pt: {np.std(found_val[7]):0.4f}",
            f"stdev. Chamfer dist.              p2pt: {np.std(found_val[8]):0.4f}",
            f"stdev. CD-PSNR                    p2pt: {np.std(found_val[9]):0.4f}",
            f"stdev. Hausdorff distance         p2pt: {np.std(found_val[10]):0.4f}",
            f"----------------------------------------",
            f"stdev. Asym. Chamfer dist. (1->2) p2pl: {np.std(found_val[11]):0.4f}",
            f"stdev. Asym. Chamfer dist. (2->1) p2pl: {np.std(found_val[12]):0.4f}",
            f"stdev. Chamfer dist.              p2pl: {np.std(found_val[13]):0.4f}",
            f"stdev. CD-PSNR                    p2pl: {np.std(found_val[14]):0.4f}",
            f"stdev. Hausdorff distance         p2pl: {np.std(found_val[15]):0.4f}",
            f"----------------------------------------",
            f"stdev. Y-CPSNR                        : {np.std(found_val[16]):0.4f}",
            f"stdev. U-CPSNR                        : {np.std(found_val[17]):0.4f}",
            f"stdev. V-CPSNR                        : {np.std(found_val[18]):0.4f}",
            "\n",
            f"============== QoE Metric ==============",
            f"stdev. Hybrid geo-color               : {np.std(found_val[19]):0.4f}",
        ]
        lines += [
            "\n",
            f"***** Maximum *****",
            f"========== Time & Binary Size ==========",
            f"max. Encoding time:                {np.max(found_val[0]):0.4f}",
            f"max. Decoding time:                {np.max(found_val[1]):0.4f}",
            f"max. Source point cloud size (kB): {np.max(found_val[2]):0.4f}",
            f"max. Total binary files size (kB): {np.max(found_val[3]):0.4f}",
            f"max. Compression ratio:            {np.max(found_val[4]):0.4f}",
            f"max. bpp (bits per point):         {np.max(found_val[5]):0.4f}",
            "\n",
            f"========== Objective Quality ===========",
            f"max. Asym. Chamfer dist. (1->2) p2pt: {np.max(found_val[6]):0.4f}",
            f"max. Asym. Chamfer dist. (2->1) p2pt: {np.max(found_val[7]):0.4f}",
            f"max. Chamfer dist.              p2pt: {np.max(found_val[8]):0.4f}",
            f"max. CD-PSNR                    p2pt: {np.max(found_val[9]):0.4f}",
            f"max. Hausdorff distance         p2pt: {np.max(found_val[10]):0.4f}",
            f"----------------------------------------",
            f"max. Asym. Chamfer dist. (1->2) p2pl: {np.max(found_val[11]):0.4f}",
            f"max. Asym. Chamfer dist. (2->1) p2pl: {np.max(found_val[12]):0.4f}",
            f"max. Chamfer dist.              p2pl: {np.max(found_val[13]):0.4f}",
            f"max. CD-PSNR                    p2pl: {np.max(found_val[14]):0.4f}",
            f"max. Hausdorff distance         p2pl: {np.max(found_val[15]):0.4f}",
            f"----------------------------------------",
            f"max. Y-CPSNR                        : {np.max(found_val[16]):0.4f}",
            f"max. U-CPSNR                        : {np.max(found_val[17]):0.4f}",
            f"max. V-CPSNR                        : {np.max(found_val[18]):0.4f}",
            "\n",
            f"============== QoE Metric ==============",
            f"max. Hybrid geo-color               : {np.max(found_val[19]):0.4f}",
        ]
        lines += [
            "\n",
            f"***** Minimum *****",
            f"========== Time & Binary Size ==========",
            f"min. Encoding time:                {np.min(found_val[0]):0.4f}",
            f"min. Decoding time:                {np.min(found_val[1]):0.4f}",
            f"min. Source point cloud size (kB): {np.min(found_val[2]):0.4f}",
            f"min. Total binary files size (kB): {np.min(found_val[3]):0.4f}",
            f"min. Compression ratio:            {np.min(found_val[4]):0.4f}",
            f"min. bpp (bits per point):         {np.min(found_val[5]):0.4f}",
            "\n",
            f"========== Objective Quality ===========",
            f"min. Asym. Chamfer dist. (1->2) p2pt: {np.min(found_val[6]):0.4f}",
            f"min. Asym. Chamfer dist. (2->1) p2pt: {np.min(found_val[7]):0.4f}",
            f"min. Chamfer dist.              p2pt: {np.min(found_val[8]):0.4f}",
            f"min. CD-PSNR                    p2pt: {np.min(found_val[9]):0.4f}",
            f"min. Hausdorff distance         p2pt: {np.min(found_val[10]):0.4f}",
            f"----------------------------------------",
            f"min. Asym. Chamfer dist. (1->2) p2pl: {np.min(found_val[11]):0.4f}",
            f"min. Asym. Chamfer dist. (2->1) p2pl: {np.min(found_val[12]):0.4f}",
            f"min. Chamfer dist.              p2pl: {np.min(found_val[13]):0.4f}",
            f"min. CD-PSNR                    p2pl: {np.min(found_val[14]):0.4f}",
            f"min. Hausdorff distance         p2pl: {np.min(found_val[15]):0.4f}",
            f"----------------------------------------",
            f"min. Y-CPSNR                        : {np.min(found_val[16]):0.4f}",
            f"min. U-CPSNR                        : {np.min(found_val[17]):0.4f}",
            f"min. V-CPSNR                        : {np.min(found_val[18]):0.4f}",
            "\n",
            f"============== QoE Metric ==============",
            f"min. Hybrid geo-color               : {np.min(found_val[19]):0.4f}",
        ]
        f.writelines('\n'.join(lines))
    return 0

def summarize_all_to_tsv(exp_dir):
    # [TODO]
    # Unfinished
    summary_log_files = glob_file(exp_dir, '_summary.log', fullpath=True)
    with open(csvfile, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter='\t')
        header = [
            'PCC_algs',
            'datasets',
            'rate',
            'avg_encT',
            'avg_decT',
            'avg_bpp',
            'avg_cd_p2pt',
            'avg_cdpsnr_p2pt',
            'avg_h_p2pt',
            'avg_cd_p2pl',
            'avg_cdpsnr_p2pl',
            'avg_h_p2pl',
            'avg_',
            'avg_',
            'avg_',
            'avg_',
            'avg_',
            'avg_',
            'avg_',
            'avg_',
            'avg_',
            'avg_',
            'avg_',
            'avg_',
            'avg_',
            'avg_',
        ]
        csvwriter.writerow(header)
        for log in summary_log_files:
            alg_name = Path(log).parents[2]
            ds_name = Path(log).parents[1]
            rate = Path(log).parents[0]
            # row = 
            # csvwriter.writerow(row)

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
        'encT':        'Encoding time:                ',
        'decT':        'Decoding time:                ',
        'bpp':         'bpp \(bits per point\):         ',
        'cd_p2pt':     'Chamfer dist.              p2pt: ',
        'cdpsnr_p2pt': 'CD-PSNR                    p2pt: ',
        'h_p2pt':      'Hausdorff distance         p2pt: ',
        'cd_p2pl':     'Chamfer dist.              p2pl: ',
        'cdpsnr_p2pl': 'CD-PSNR                    p2pl: ',
        'h_p2pl':      'Hausdorff distance         p2pl: ',
        'y_cpsnr':     'Y-CPSNR                        : ',
        'u_cpsnr':     'U-CPSNR                        : ',
        'v_cpsnr':     'V-CPSNR                        : ',
        'hybrid':      'Hybrid geo-color               : ',
    }

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
                            ret[alg_name][ds_name][rate][metric][statistic] = val
    savemat(matfile, ret)

def nested_dict():
    # https://stackoverflow.com/a/652226
    return defaultdict(nested_dict)
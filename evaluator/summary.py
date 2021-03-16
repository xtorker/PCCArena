import re
import logging
import numpy as np
from pathlib import Path

from utils.file_io import glob_file
from utils._version import __version__

logger = logging.getLogger(__name__)

def summary_one_setup(log_dir):
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
            for idx, pattern in enumerate(chosen_metrics):
                isfound = False
                for line in f:
                    m = re.search(f'(?<={pattern}).*', line)
                    if m:
                        if m.group() == 'inf':
                            found_val[idx].append(float(max_val[pattern]))
                        elif m.group() == 'NaN':
                            found_val[idx].append(np.nan)
                        else:
                            found_val[idx].append(float(m.group()))
                        isfound = True
                        break
                if isfound is False:
                    # Not supposed to go into this if block
                    logger.error(f"Pattern {pattern} not found in {log}")
                    raise ValueError

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
            f"avg. Source point cloud size (kB): {np.mean(found_val[2])}",
            f"avg. Total binary files size (kB): {np.mean(found_val[3])}",
            f"avg. Compression ratio:            {np.mean(found_val[4])}",
            f"avg. bpp (bits per point):         {np.mean(found_val[5])}",
            "\n",
            f"========== Objective Quality ===========",
            f"avg. Asym. Chamfer dist. (1->2) p2pt: {np.mean(found_val[6])}",
            f"avg. Asym. Chamfer dist. (2->1) p2pt: {np.mean(found_val[7])}",
            f"avg. Chamfer dist.              p2pt: {np.mean(found_val[8])}",
            f"avg. CD-PSNR                    p2pt: {np.mean(found_val[9])}",
            f"avg. Hausdorff distance         p2pt: {np.mean(found_val[10])}",
            f"----------------------------------------",
            f"avg. Asym. Chamfer dist. (1->2) p2pl: {np.mean(found_val[11])}",
            f"avg. Asym. Chamfer dist. (2->1) p2pl: {np.mean(found_val[12])}",
            f"avg. Chamfer dist.              p2pl: {np.mean(found_val[13])}",
            f"avg. CD-PSNR                    p2pl: {np.mean(found_val[14])}",
            f"avg. Hausdorff distance         p2pl: {np.mean(found_val[15])}",
            f"----------------------------------------",
            f"avg. Y-CPSNR                        : {np.mean(found_val[16])}",
            f"avg. U-CPSNR                        : {np.mean(found_val[17])}",
            f"avg. V-CPSNR                        : {np.mean(found_val[18])}",
            "\n",
            f"============== QoE Metric ==============",
            f"avg. Hybrid geo-color               : {np.mean(found_val[19])}",
            "\n",
        ]
        lines += [
            "\n",
            f"***** Standard Deviation *****",
            f"========== Time & Binary Size ==========",
            f"stdev. Encoding time:                {np.std(found_val[0]):0.4f}",
            f"stdev. Decoding time:                {np.std(found_val[1]):0.4f}",
            f"stdev. Source point cloud size (kB): {np.std(found_val[2])}",
            f"stdev. Total binary files size (kB): {np.std(found_val[3])}",
            f"stdev. Compression ratio:            {np.std(found_val[4])}",
            f"stdev. bpp (bits per point):         {np.std(found_val[5])}",
            "\n",
            f"========== Objective Quality ===========",
            f"stdev. Asym. Chamfer dist. (1->2) p2pt: {np.std(found_val[6])}",
            f"stdev. Asym. Chamfer dist. (2->1) p2pt: {np.std(found_val[7])}",
            f"stdev. Chamfer dist.              p2pt: {np.std(found_val[8])}",
            f"stdev. CD-PSNR                    p2pt: {np.std(found_val[9])}",
            f"stdev. Hausdorff distance         p2pt: {np.std(found_val[10])}",
            f"----------------------------------------",
            f"stdev. Asym. Chamfer dist. (1->2) p2pl: {np.std(found_val[11])}",
            f"stdev. Asym. Chamfer dist. (2->1) p2pl: {np.std(found_val[12])}",
            f"stdev. Chamfer dist.              p2pl: {np.std(found_val[13])}",
            f"stdev. CD-PSNR                    p2pl: {np.std(found_val[14])}",
            f"stdev. Hausdorff distance         p2pl: {np.std(found_val[15])}",
            f"----------------------------------------",
            f"stdev. Y-CPSNR                        : {np.std(found_val[16])}",
            f"stdev. U-CPSNR                        : {np.std(found_val[17])}",
            f"stdev. V-CPSNR                        : {np.std(found_val[18])}",
            "\n",
            f"============== QoE Metric ==============",
            f"stdev. Hybrid geo-color               : {np.std(found_val[19])}",
        ]
        lines += [
            "\n",
            f"***** Maximum *****",
            f"========== Time & Binary Size ==========",
            f"max. Encoding time:                {np.max(found_val[0]):0.4f}",
            f"max. Decoding time:                {np.max(found_val[1]):0.4f}",
            f"max. Source point cloud size (kB): {np.max(found_val[2])}",
            f"max. Total binary files size (kB): {np.max(found_val[3])}",
            f"max. Compression ratio:            {np.max(found_val[4])}",
            f"max. bpp (bits per point):         {np.max(found_val[5])}",
            "\n",
            f"========== Objective Quality ===========",
            f"max. Asym. Chamfer dist. (1->2) p2pt: {np.max(found_val[6])}",
            f"max. Asym. Chamfer dist. (2->1) p2pt: {np.max(found_val[7])}",
            f"max. Chamfer dist.              p2pt: {np.max(found_val[8])}",
            f"max. CD-PSNR                    p2pt: {np.max(found_val[9])}",
            f"max. Hausdorff distance         p2pt: {np.max(found_val[10])}",
            f"----------------------------------------",
            f"max. Asym. Chamfer dist. (1->2) p2pl: {np.max(found_val[11])}",
            f"max. Asym. Chamfer dist. (2->1) p2pl: {np.max(found_val[12])}",
            f"max. Chamfer dist.              p2pl: {np.max(found_val[13])}",
            f"max. CD-PSNR                    p2pl: {np.max(found_val[14])}",
            f"max. Hausdorff distance         p2pl: {np.max(found_val[15])}",
            f"----------------------------------------",
            f"max. Y-CPSNR                        : {np.max(found_val[16])}",
            f"max. U-CPSNR                        : {np.max(found_val[17])}",
            f"max. V-CPSNR                        : {np.max(found_val[18])}",
            "\n",
            f"============== QoE Metric ==============",
            f"max. Hybrid geo-color               : {np.max(found_val[19])}",
        ]
        lines += [
            "\n",
            f"***** Minimum *****",
            f"========== Time & Binary Size ==========",
            f"min. Encoding time:                {np.min(found_val[0]):0.4f}",
            f"min. Decoding time:                {np.min(found_val[1]):0.4f}",
            f"min. Source point cloud size (kB): {np.min(found_val[2])}",
            f"min. Total binary files size (kB): {np.min(found_val[3])}",
            f"min. Compression ratio:            {np.min(found_val[4])}",
            f"min. bpp (bits per point):         {np.min(found_val[5])}",
            "\n",
            f"========== Objective Quality ===========",
            f"min. Asym. Chamfer dist. (1->2) p2pt: {np.min(found_val[6])}",
            f"min. Asym. Chamfer dist. (2->1) p2pt: {np.min(found_val[7])}",
            f"min. Chamfer dist.              p2pt: {np.min(found_val[8])}",
            f"min. CD-PSNR                    p2pt: {np.min(found_val[9])}",
            f"min. Hausdorff distance         p2pt: {np.min(found_val[10])}",
            f"----------------------------------------",
            f"min. Asym. Chamfer dist. (1->2) p2pl: {np.min(found_val[11])}",
            f"min. Asym. Chamfer dist. (2->1) p2pl: {np.min(found_val[12])}",
            f"min. Chamfer dist.              p2pl: {np.min(found_val[13])}",
            f"min. CD-PSNR                    p2pl: {np.min(found_val[14])}",
            f"min. Hausdorff distance         p2pl: {np.min(found_val[15])}",
            f"----------------------------------------",
            f"min. Y-CPSNR                        : {np.min(found_val[16])}",
            f"min. U-CPSNR                        : {np.min(found_val[17])}",
            f"min. V-CPSNR                        : {np.min(found_val[18])}",
            "\n",
            f"============== QoE Metric ==============",
            f"min. Hybrid geo-color               : {np.min(found_val[19])}",
        ]
        f.writelines('\n'.join(lines))
    return 0

from collections import defaultdict
from scipy.io import savemat
import re
import numpy as np
import csv
from itertools import zip_longest

from evaluator.summary import summarize_all_to_mat, summarize_all_to_csv

# summarize_all_to_csv('experiments')

chosen_metrics = {
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
chosen_metrics.update((key, re.escape(pattern)) for key, pattern in chosen_metrics.items())
# chosen_metrics = {key: re.escape(chosen_metrics[key]) for key, value in chosen_metrics}
# print(chosen_metrics)
found_val = {key: [] for key in chosen_metrics.keys()}
found_val['encT'].append(np.inf)
found_val['encT'].append(None)
found_val['encT'].append(30)

found_val['decT'].append(10)
found_val['decT'].append(20)
found_val['decT'].append(30)

found_val['bpp'].append(-np.inf)
found_val['bpp'].append(100)
found_val['bpp'].append(0)
print([list_ for key, list_ in found_val.items()])

with open('test.csv', 'w') as csvfile:
    rows = zip_longest(*[list_ for list_ in found_val.values()])
    csvwriter = csv.writer(csvfile, delimiter=',')
    for row in rows:
        print(row)
        csvwriter.writerow(row)
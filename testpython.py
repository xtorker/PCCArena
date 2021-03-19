from collections import defaultdict
from scipy.io import savemat

from evaluator.summary import summarize_all_to_mat

summarize_all_to_mat('experiments')

# def nested_dict():
#     return defaultdict(nested_dict)

# dd = nested_dict()

# # print(dd)

# dd['draco']['snc']['r4']['encT'] = 12
# dd['draco']['snc']['r4']['decT'] = 13
# dd['draco']['snc']['r5']['encT'] = 14
# dd['draco']['snc']['r5']['deT'] = 15
# dd['draco']['sncc']['r4']['encT'] = 16
# dd['draco']['sncc']['r4']['encT'] = 17
# dd['gpcc']['snc']['r4']['encT'] = 18

# # savemat('test.mat', dd)
# # print(dd['draco']['snc']['r4'])

# chosen_metrics = [
#     {'encT':        'Encoding time:                '},
#     {'devT':        'Decoding time:                '},
#     {'bpp':         'bpp \(bits per point\):         '},
#     {'cd_p2pt':     'Chamfer dist.              p2pt: '},
#     {'cdpsnr_p2pt': 'CD-PSNR                    p2pt: '},
#     {'h_p2pt':      'Hausdorff distance         p2pt: '},
#     {'cd_p2pl':     'Chamfer dist.              p2pl: '},
#     {'cdpsnr_p2pl': 'CD-PSNR                    p2pl: '},
#     {'h_p2pl':      'Hausdorff distance         p2pl: '},
#     {'y_cpsnr':     'Y-CPSNR                        : '},
#     {'u_cpsnr':     'U-CPSNR                        : '},
#     {'v_cpsnr':     'V-CPSNR                        : '},
#     {'hybrid':      'Hybrid geo-color               : '},
# ]

# print(chosen_metrics[2].)
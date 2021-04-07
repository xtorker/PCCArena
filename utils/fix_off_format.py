'''
Fix the .off file format in ModelNet10/40 datasets
i.e.
=======================================
OFF
4562 5415 0     is the correct format
=======================================
OFF4562 5415 0  is the incorrect format
=======================================
'''

from multiprocessing import Pool
import argparse
import functools
from glob import glob
from tqdm import tqdm
from os.path import join

def rewrite(filename):
    with open(filename, "r+") as off:
        first_line = off.readline()
        if len(first_line) != 3:
            remain_lines = off.readlines()
            second_line = first_line[3:]
            off.seek(0)
            off.write("OFF\n")
            off.write(second_line)
            off.writelines(remain_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'dir',
        help='Directory of off models.')

    args = parser.parse_args()

    paths = glob(join(args.dir, '**', '*.off'), recursive=True)
    paths_len = len(paths)
    assert paths_len > 0

    with Pool() as p:
        list(tqdm(p.imap(rewrite, paths), total=paths_len)) 

    # for filepath in tqdm(glob.glob(args.dir + '**/*.off', recursive=True)):
    #     rewrite(filepath)

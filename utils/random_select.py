import random
import os
from pathlib import Path

pattern = "**/test/**/*.ply"
src_dir = "/mnt/data6/chenghao/PCC_datasets/ShapeNet/SNCC_scale1024/"
dest_dir = "/mnt/data6/chenghao/PCC_datasets/ShapeNet/SNCC_scale1024_test_sample100/"
nor_src_dir = "/mnt/data6/chenghao/PCC_datasets/ShapeNet/SNCC_normal_scale1024/"
nor_dest_dir = "/mnt/data6/chenghao/PCC_datasets/ShapeNet/SNCC_normal_scale1024_test_sample100/"

# done_dir = "/mnt/data6/chenghao/PCC_datasets/ShapeNet/SNC_scale1024_test_sample100/"

# src_dir = "/mnt/data5/chenghao/MN40_scale1024/"
# dest_dir = "/mnt/data5/chenghao/MN40_scale1024_test_sample100"
# nor_src_dir = "/mnt/data5/chenghao/MN40_normal_scale1024/"
# nor_dest_dir = "/mnt/data5/chenghao/MN40_normal_scale1024_test_sample100"
# done_dir = ""

# src_dir = "/mnt/data5/chenghao/CAPOD_scale1024_sample100/"
# dest_dir = "/mnt/data5/chenghao/CAPOD_scale1024_sample10"
# nor_src_dir = "/mnt/data5/chenghao/CAPOD_normal_scale1024_sample100/"
# nor_dest_dir = "/mnt/data5/chenghao/CAPOD_normal_scale1024_sample10"
# done_dir = ""

# src_dir = "/mnt/data5/chenghao/redandblack_vox10/color"
# dest_dir = "/mnt/data5/chenghao/redandblack_vox10_sample25"
# nor_src_dir = "/mnt/data5/chenghao/redandblack_vox10/color_normal"
# nor_dest_dir = "/mnt/data5/chenghao/redandblack_vox10_normal_sample25"
# done_dir = ""

# filelist = list(set(Path(src_dir).rglob(pattern)) - set(Path(done_dir).rglob(pattern)))
filelist = list(Path(src_dir).rglob(pattern))
selected = random.sample(filelist, 100)
sym_selected = list(Path(dest_dir).joinpath(Path(file).relative_to(src_dir)) for file in selected)

# normal
nor_selected = list(Path(nor_src_dir).joinpath(Path(file).relative_to(src_dir)) for file in selected)
sym_nor_selected = list(Path(nor_dest_dir).joinpath(Path(file).relative_to(src_dir)) for file in selected)

[Path(file).parent.mkdir(parents=True, exist_ok=True) for file in sym_selected]
[Path(file).parent.mkdir(parents=True, exist_ok=True) for file in sym_nor_selected]

for idx, ori in enumerate(selected):
    os.symlink(ori, sym_selected[idx])
for idx, ori_nor in enumerate(nor_selected):
    os.symlink(ori_nor, sym_nor_selected[idx])
    

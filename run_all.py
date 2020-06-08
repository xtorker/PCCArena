import subprocess as sp
import os
from os.path import join, abspath
import time
CWD = os.getcwd()
CPUs = str(os.cpu_count())

# dataset = 'ModelNet10_pc50k_0-1'
dataset = 'ModelNet40_pc50k_0-1'
# dataset = 'ShapeNetCore_pc50k_0-1'

source_path = abspath(join('datasets', dataset))

############################################
# PCL Compression
# octreeRes: Quantization bits for the position attribute.
# doVoxel: Drop the duplicate points during voxelization. (0:false, 1:true)
############################################
pcl = 'run_pcl.py'
pcl_wd = 'algorithms/PCL_compression'
octreeRes = [str(x) for x in [1/100, 1/150, 1/175, 1/200]] #lower bitrate
octreeRes = [str(x) for x in [1/512.5, 1/725, 1/1150, 1/2000]] #higher bitrate
doVoxel = '1'

sp.run(['python', pcl,
         source_path, f'experiments/{dataset}_octreeRes{octreeRes[0]}',
         octreeRes[0]], cwd=pcl_wd)
sp.run(['python', pcl,
         source_path, f'experiments/{dataset}_octreeRes{octreeRes[1]}',
         octreeRes[1]], cwd=pcl_wd)
sp.run(['python', pcl,
         source_path, f'experiments/{dataset}_octreeRes{octreeRes[2]}',
         octreeRes[2]], cwd=pcl_wd)
sp.run(['python', pcl,
         source_path, f'experiments/{dataset}_octreeRes{octreeRes[3]}',
         octreeRes[3]], cwd=pcl_wd)

# ############################################
# # Draco
# # qp: Quantization bits for the position attribute.
# # cl: Compression level [0-10], most=10, least=0.
# ############################################
draco = 'run_draco.py'
draco_wd = 'algorithms/draco'
qp = [str(x) for x in [4,5,6,7]] #lower bitrate
# qp = [str(x) for x in [8,9,10,11]] #higher bitrate
cl = str(10)

sp.run(['python', draco,
         source_path, f'experiments/{dataset}_qp{qp[0]}',
         '--qp', qp[0],
         '--cl', cl], cwd=draco_wd)
sp.run(['python', draco,
         source_path, f'experiments/{dataset}_qp{qp[1]}',
         '--qp', qp[1],
         '--cl', cl], cwd=draco_wd)
sp.run(['python', draco,
         source_path, f'experiments/{dataset}_qp{qp[2]}',
         '--qp', qp[2],
         '--cl', cl], cwd=draco_wd)
sp.run(['python', draco,
         source_path, f'experiments/{dataset}_qp{qp[3]}',
         '--qp', qp[3],
         '--cl', cl], cwd=draco_wd)

# ############################################
# # G-PCC tmc13
# # scale_factor: Scale factor to be applied to point positions during quantization process.
# #               (Prior to encoding, scale the point cloud geometry by multiplying each 
# #               co-ordinate by the real FACTOR and rounding to integer precision. 
# #               The scale factor is written to the bitstream and a decoder may use it 
# #               to provide output at the original scale.)
# # merge: Drop the duplicate points during voxelization. (0: false, 1: true)
# ############################################
tmc13 = 'run_tmc13.py'
tmc13_wd = 'algorithms/mpeg-pcc-tmc13-v6'
scale_factor = [str(x) for x in [128,192,224,256]] #lower bitrate
# scale_factor = [str(x) for x in [720,1056,1728,3072]] #higher bitrate
merge = '1'

sp.run(['python', tmc13,
         source_path, f'experiments/{dataset}_sf{scale_factor[0]}',
         '--scale_factor', scale_factor[0],
         '--merge', merge], cwd=tmc13_wd)
sp.run(['python', tmc13,
         source_path, f'experiments/{dataset}_sf{scale_factor[1]}',
         '--scale_factor', scale_factor[1],
         '--merge', merge], cwd=tmc13_wd)
sp.run(['python', tmc13,
         source_path, f'experiments/{dataset}_sf{scale_factor[2]}',
         '--scale_factor', scale_factor[2],
         '--merge', merge], cwd=tmc13_wd)
sp.run(['python', tmc13,
         source_path, f'experiments/{dataset}_sf{scale_factor[3]}',
         '--scale_factor', scale_factor[3],
         '--merge', merge], cwd=tmc13_wd)

############################################
# Geo-CNN
# resolution: Scale to which voxel resolution.
# divide_oct: Compression level [0-10], most=10, least=0.
############################################
geocnn = 'run_geo_cnn.py'
geocnn_wd = 'algorithms/pcc_geo_cnn'
model_path = 'models/ModelNet40_vox64_00001'
resolution = [str(x) for x in [256,384,448,512]]
divide_oct = [str(x) for x in [0,0,0,0]]

sp.run(['python', geocnn,
         source_path, f'/mnt/data6/chenghao/experiments/{dataset}_vg{resolution[0]}', model_path,
         '--resolution', resolution[0],
         '--preprocess_threads', CPUs,
         '--divide_oct', divide_oct[0]], cwd=geocnn_wd)
sp.run(['python', geocnn,
         source_path, f'/mnt/data6/chenghao/experiments/{dataset}_vg{resolution[1]}', model_path,
         '--resolution', resolution[1],
         '--preprocess_threads', CPUs,
         '--divide_oct', divide_oct[1]], cwd=geocnn_wd)
sp.run(['python', geocnn,
         source_path, f'/mnt/data6/chenghao/experiments/{dataset}_vg{resolution[2]}', model_path,
         '--resolution', resolution[2],
         '--preprocess_threads', CPUs,
         '--divide_oct', divide_oct[2]], cwd=geocnn_wd)
sp.run(['python', geocnn,
         source_path, f'/mnt/data6/chenghao/experiments/{dataset}_vg{resolution[3]}', model_path,
         '--resolution', resolution[3],
         '--preprocess_threads', CPUs,
         '--divide_oct', divide_oct[3]], cwd=geocnn_wd)




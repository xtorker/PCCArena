#! /bin/bash

# ========== In [root] ==========
conda env create -f cfgs/conda_env/pcc_arena.yml
conda env create -f cfgs/conda_env/geocnn_v1.yml
conda env create -f cfgs/conda_env/geocnn_v2.yml
conda env create -f cfgs/conda_env/pcgc_v1.yml
conda env create -f cfgs/conda_env/pcgc_v2.yml



cd algs
# ========== In [root]/algs/ ==========

## Draco
git clone --depth 1 --branch 1.3.6 https://github.com/google/draco.git Draco
cd Draco
mkdir build && cd build && cmake .. && make
cd ../..

## GPCC
git clone --depth 1 --branch release-v12.0 https://github.com/MPEGGroup/mpeg-pcc-tmc13.git GPCC
cd GPCC
mkdir build && cd build && cmake .. && make
cd ../..

## VPCC
git clone --depth 1 --branch release-v12.0 https://github.com/MPEGGroup/mpeg-pcc-tmc2.git VPCC
cd VPCC
mkdir build && cd build && cmake .. && make
cd ../..

## GeoCNNv1
git clone https://github.com/mauriceqch/pcc_geo_cnn.git GeoCNNv1

## GeoCNNv2
git clone https://github.com/mauriceqch/pcc_geo_cnn_v2.git GeoCNNv2
cd GeoCNNv2
wget http://teddy.cs.nthu.edu.tw/geocnn_v2.tar.bz2
tar jxvf geocnn_v2.tar.bz2
rm geocnn_v2.tar.bz2
cd ..

## PCGCv1
git clone https://github.com/NJUVISION/PCGCv1.git PCGCv1

## PCGCv2
git clone https://github.com/NJUVISION/PCGCv2.git PCGCv2



cd ../../evaluator
# ========== In [root]/evaluator/ ==========

cd mpeg-pcc-dmetric-master
sh build.sh

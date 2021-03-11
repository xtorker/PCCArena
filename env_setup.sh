#! /bin/bash

# ========== In [root] ==========
conda env create -f cfgs/conda_env/pcc_arena.yml
conda env create -f cfgs/conda_env/geocnn_v2.yml

cd algs
# ========== In [root]/algs/ ==========

## Draco
git clone --depth 1 --branch 1.3.6 https://github.com/google/draco.git draco
cd draco
mkdir build && cd build && cmake .. && make
cd ../..

## GeoCNNv2
git clone https://github.com/mauriceqch/pcc_geo_cnn_v2.git geocnn_v2
cd geocnn_v2
wget http://teddy.cs.nthu.edu.tw/geocnn_v2.tar.bz2
tar jxvf geocnn_v2.tar.bz2
rm geocnn_v2.tar.bz2

cd ../../evaluator

# ========== In [root]/evaluator/ ==========
cd mpeg-pcc-dmetric-master
sh build.sh

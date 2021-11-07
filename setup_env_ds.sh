#! /bin/bash
set -euo pipefail

# check mpeg-pcc-dmetric-master.tar.gz exists
if [ ! -f evaluator/dependencies/mpeg-pcc-dmetric-master.tar.gz ]; then
    echo "[File not found] evaluator/dependencies/mpeg-pcc-dmetric-master.tar.gz"
    echo "Please download it from http://mpegx.int-evry.fr/software/MPEG/PCC/mpeg-pcc-dmetric"
    exit 0
fi

# Cleaning conda environments 
conda env remove -n GeoCNNv1
conda env remove -n GeoCNNv2
conda env remove -n PCGCv1
conda env remove -n PCGCv2

# ========== In [root] ==========
conda env create -f cfgs/conda_env/GeoCNNv1.yml
conda env create -f cfgs/conda_env/GeoCNNv2.yml
conda env create -f cfgs/conda_env/PCGCv1.yml
conda env create -f cfgs/conda_env/PCGCv2.yml



cd algorithms
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
./build.sh
cd ..

## GeoCNNv1
git clone https://github.com/mauriceqch/pcc_geo_cnn.git GeoCNNv1

## GeoCNNv2
git clone https://github.com/mauriceqch/pcc_geo_cnn_v2.git GeoCNNv2

## PCGCv1
git clone https://github.com/xtorker/PCGCv1.git PCGCv1

## PCGCv2
git clone https://github.com/xtorker/PCGCv2.git PCGCv2

cd ..


cd evaluator/dependencies
# ========== In [root]/evaluator/dependencies ==========

# MPEG pcc dmetric
# Download mpeg-pcc-dmetric-master.tar.gz v0.13.5 
# from http://mpegx.int-evry.fr/software/MPEG/PCC/mpeg-pcc-dmetric
tar zxvf mpeg-pcc-dmetric-master.tar.gz
patch -sp0 < mpeg-pcc-dmetric.patch
cd mpeg-pcc-dmetric-master
./build.sh
cd ..

# libgdiam
wget https://sarielhp.org/research/papers/00/diameter/libgdiam-1.0.3.tar.gz
tar zxvf libgdiam-1.0.3.tar.gz
patch -sp0 < libgdiam-1.0.3.patch
cd libgdiam-1.0.3
mkdir build && cd build && cmake .. && make
cd ../../../..
mv checkpoints/ algorithms/PCGCv1/
mv ckpts/ algorithms/PCGCv2/
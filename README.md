# PCC Arena

## Environments
Ubuntu 20.04

## Prerequisites
- Ananconda 3
- git
- gcc
- g++

## Installation
```bash=
git clone https://github.com/xtorker/PCC_Arena.git
cd PCC_Arena
conda env create -f cfgs/conda_env/pcc_arena.yml
conda activate pcc_arena
python setup.py
```
Make sure you have downloaded "**mpeg-pcc-dmetric-master.tar.gz (v0.13.5)**" from http://mpegx.int-evry.fr/software/MPEG/PCC/mpeg-pcc-dmetric and put it under evaluator/dependencies
```bash=
./setup_env_ds.sh
```

## Run Experiments
```bash=
python run_experiments.py
```

## Add More PCC Algorithms
1. Put the whole PCC algorithm project folder under algorithms/
2. Write a specific wrapper for it and put it under algs_wrapper/
3. Write a json file for configuring any coding parameters and rate control parameters, and put it under cfgs/algs/
4. (Optional) If the PCC algorithm need specific virtual environment, make sure to indicate the python path in the json file (Step 3).

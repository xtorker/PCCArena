# PCC Arena

## Environments
Ubuntu 20.04

## Prerequisites
- Ananconda 3
- git
- gcc
- g++
- xvfb (if running on system without gui)

## Installation
```bash=
git clone https://github.com/TokenHung/PCCArena.git
cd PCCArena
conda env create -f cfgs/conda_env/pcc_arena.yml
conda activate pcc_arena
python setup.py
```
<!-- Make sure you have downloaded "**mpeg-pcc-dmetric-master.tar.gz (v0.13.5)**" from http://mpegx.int-evry.fr/software/MPEG/PCC/mpeg-pcc-dmetric and put it under evaluator/dependencies -->
```bash=
chmod +x setup_env_ds.sh
./setup_env_ds.sh
```

## Prepare Datasets
<!-- To skip this step, we have prepare an sample SNC dataset on https://drive.google.com/drive/folders/1HQS0tzTF-ukifNXxrYqld2yT1bHOcMQQ?usp=sharing.
Please download and extract it under datasets/ -->

Please download pre-trained dataset for geocnnv1 and v2.

## Run Experiments
```bash=
python run_experiments.py
```

## Add More PCC Algorithms
1. Put the whole PCC algorithm project folder under algorithms/
2. Write a specific wrapper for it and put it under algs_wrapper/
3. Write a YAML file for configuring any coding parameters and rate control parameters, and put it under cfgs/algs/
4. (Optional) If the PCC algorithm need specific virtual environment, make sure to indicate the python path in the YAML file (Step 3).

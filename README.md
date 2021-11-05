# PCC Arena

## Environments
Ubuntu 20.04

## Prerequisites
- git
- gcc
- g++
- CUDA (CUDA 11.5)
download guide: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html
- Ananconda 3
```
wget https://repo.anaconda.com/archive/Anaconda3-2020.11-Linux-x86_64.sh
sh Anaconda3-2020.11-Linux-x86_64.sh
source .bashrc
```
- SVN
- xvfb (if running on the system without gui)
```
sudo apt install git gcc g++ xvfb subversion -y
```

## Quick Start
To download and set up PCC Arena, please type the following commands.

- Step 1: Clone the github project.
```
git clone https://github.com/TokenHung/PCCArena.git
```
- Step 2: Change the current directory.
```
cd PCCArena
```
- Step 3: Create the conda environment pcc_arena.
```
conda env create -f cfgs/conda_env/pcc_arena.yml
```
- Step 4: Activate the environment pcc_arena.
```
conda activate pcc_arena
```
- Step 5: Set up the environments.
```
python setup.py
```
- Step 6: Grant executed permission.
```
chmod +x setup_env_ds.sh
```
- Step 7: Run environment setup script.
```
./setup_env_ds.sh
```

- Step 8: Download the pretrained models of GeoCNNv1 and GeoCNNv2 using the following links. Save them in the current directory.
GeoCNNv1: https://drive.google.com/file/d/1S0llGslYHcOVYWfl4tqvyN08rO7IHcKu/view?usp=sharing
GeoCNNv2:
https://drive.google.com/file/d/1w5jue_dgR8Xw3D5gvZV1lXDA36NO5T_4/view?usp=sharing

- Step 9: Uncompress the models into algorithms/GeoCNNv1 and algorithms/GeoCNNv2.
```
unzip geocnnv1_models.zip -C algorithms/GeoCNNv1/models
tar -Jxvf geocnn_v2_pretrained_models.tar.xz algorithms/GeoCNNv2/models
```

- Step10: Run experiments in PCC Arena.
We have two types of python files for experimenting. One is a short version for testing, and the other is a full version.
The short version only runs one compression rate for each algorithm and doesn't run the algorithms which require lots of memory (e.g., GeoCNNv1 requires more than 50GB).
```
# Short version
python run_experiments_short.py
```
```
# Full version
python run_experiments.py
```
<!-- ## Clean the conda environment
```bash=
# Clean conda environment if exists
conda env remove -n pcc_arena
conda env remove -n GeoCNNv1
conda env remove -n GeoCNNv2
conda env remove -n PCGCv1
conda env remove -n PCGCv2
```
## Installation
```
git clone https://github.com/TokenHung/PCCArena.git
cd PCCArena
conda env create -f cfgs/conda_env/pcc_arena.yml
conda activate pcc_arena
python setup.py
chmod +x setup_env_ds.sh
./setup_env_ds.sh
```
## Download the pretrained models for GeoCNNv1 and GeoCNNv2
v1 - https://drive.google.com/file/d/1aeQL9xrpRxbNGWj4eQutsCnNB6irbT8l/view?usp=sharing

v2 - https://drive.google.com/file/d/1w5jue_dgR8Xw3D5gvZV1lXDA36NO5T_4/view?usp=sharing
```
# you can either link or unzip Pre-trained model to algorithms/GeoCNNv1 and v2
# the following is using soft link
rm -rf algorithms/GeoCNNv1/models
rm -rf algorithms/GeoCNNv2/models
ln -s /home/token/geocnnv1_models/ algorithms/GeoCNNv1/models
ln -s /home/token/geocnnv2_models/ algorithms/GeoCNNv2/models
```
## Now we can run PCC_Arena
```
python run_experiments.py
```
## All-in-one bash script for installation and running experiments
[Youtube Video Link of running all-in-one script](https://youtu.be/LhtEQsvSghM)

Full script for reference.

Run script by ```bash -i yourscript.sh```
```
# Clean conda environment
conda env remove -n pcc_arena
conda env remove -n GeoCNNv1
conda env remove -n GeoCNNv2
conda env remove -n PCGCv1
conda env remove -n PCGCv2

# Steps following readme
git clone https://github.com/TokenHung/PCCArena.git
cd PCCArena
conda env create -f cfgs/conda_env/pcc_arena.yml
conda activate pcc_arena
python setup.py
chmod +x setup_env_ds.sh
./setup_env_ds.sh

# You can either link or unzip Pre-trained model to algorithms/GeoCNNv1 and v2
# the following is using softlink
rm -rf algorithms/GeoCNNv1/models
rm -rf algorithms/GeoCNNv2/models
ln -sfn /mnt/data4/token/geocnnv1_models/ algorithms/GeoCNNv1/models
ln -sfn /mnt/data4/token/geocnnv2_models/ algorithms/GeoCNNv2/models

# Now we can run PCC_Arena
conda init bash
conda activate pcc_arena
python run_experiments.py
``` -->
## Add More PCC Algorithms
1. Put the whole PCC algorithm project folder under algorithms/
2. Write a specific wrapper for it and put it under algs_wrapper/
3. Write a YAML file for configuring any coding parameters and rate control parameters, and put it under cfgs/algs/
4. (Optional) If the PCC algorithm needs specific virtual environment, make sure to indicate the python path in the YAML file (Step 3).

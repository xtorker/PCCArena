# PCC Arena

## Environments
Ubuntu 20.04

## Prerequisites
- Ananconda 3
- git
- gcc
- g++
- xvfb (if running on system without gui)

## Clean the conda environment
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
<iframe width="560" height="315" src="https://www.youtube.com/embed/LhtEQsvSghM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
Full script for reference
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
```
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
```
## Add More PCC Algorithms
1. Put the whole PCC algorithm project folder under algorithms/
2. Write a specific wrapper for it and put it under algs_wrapper/
3. Write a YAML file for configuring any coding parameters and rate control parameters, and put it under cfgs/algs/
4. (Optional) If the PCC algorithm need specific virtual environment, make sure to indicate the python path in the YAML file (Step 3).

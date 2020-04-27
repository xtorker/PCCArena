# PCC Arena
## Preparation
### Algorithms
1. Clone each projects (Draco, G-PCC, Geo-CNN) into /algorithms folder.
Draco: https://github.com/google/draco.git
G-PCC: https://github.com/MPEGGroup/mpeg-pcc-tmc13.git
Geo-CNN: https://github.com/mauriceqch/pcc_geo_cnn.git
2. Patch corresponding scripts in /algorithms into each algorithms folder and sub-folders.
3. Build the projects (Draco, G-PCC, PCL) with
    ```
    mkdir build && cd build
    cmake ..
    make
    ```

### Datasets
1. Download each datasets (MN40, SNC, CAPOD) into /datasets folder.
MN40: http://modelnet.cs.princeton.edu/ModelNet40.zip
SNC: https://www.shapenet.org/
CAPOD: https://sites.google.com/site/pgpapadakis/home/CAPOD/CAPOD.zip
2. Fix the .off format in MN40 with /utils/fix_off_format.py
`python fix_off_format.py /datasets/ModelNet40`
3. Reconstruct the SNC directory structure.
    a.) Paste /utils/shapenet_structure.py and /utils/train_test_split.csv into /datasets/ShapeNetCore.v2
    b.) `python shapenet_structure.py`
4. Transform all the datasets from mesh to point cloud with
MN40:
`python /utils/mesh2pc.py /datasets/ModelNet40 /datasets/ModelNet40_pc500k_0-1`
SNC:
`python /utils/mesh2pc.py /datasets/shapenet_new_structure /datasets/ShapeNetCore_pc500k_0-1 --source_extension .obj`
CAPOD:
`python /utils/mesh2pc.py /datasets/CAPOD /datasets/CAPOD_pc500k_0-1 --source_extension .obj`

### Evaluator
1. Build /evaluator/geo_dist with PCL >= 1.8

## Running Experiments with our selected Coding Parameters
`python run_all.py`
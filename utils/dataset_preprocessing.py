import argparse
import numpy as np
import open3d as o3d
from pathlib import Path
from multiprocessing import Pool
from tqdm import tqdm
# import pymeshlab as ml

def normal_estimation(infile, outfile):

    # ms = ml.MeshSet()
    # ms.load_new_mesh(infile)
    # ms.apply_filter('compute_normals_for_point_sets', k=30, viewpos=[281, 510.5, 1286])
    # ms.save_current_mesh(outfile)
    

    pcd = o3d.io.read_point_cloud(infile)
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamKNN(knn=30))
    pcd.orient_normals_consistent_tangent_plane(k=30)

    o3d.io.write_point_cloud(outfile, pcd)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src_dir", help="Input point cloud directory.")
    parser.add_argument("dest_dir", help="Output point cloud directory.")
    parser.add_argument("-r", "--radius", help="Radius of KDTree search.", type=float, default=0.1, dest="radius")
    parser.add_argument("-k", "--knn", help="Max NN of KDTree search.", type=int, default=30, dest="knn")
    args = parser.parse_args()

    # glob for point cloud filename only

    pc_files = [Path(pc).name for pc in Path(args.src_dir).glob("*.ply")]

    infile_path = [str(Path(args.src_dir).joinpath(pc)) for pc in pc_files]
    outfile_path = [str(Path(args.dest_dir).joinpath(pc.replace(".ply", "_normal.ply"))) for pc in pc_files]

    files_len = len(infile_path)
    assert files_len > 0
    for infile, outfile in zip(infile_path, outfile_path):
        normal_estimation(infile, outfile)
    # with Pool() as p:
    #     list(tqdm(p.starmap(normal_estimation, zip(infile_path, outfile_path)), total=files_len))
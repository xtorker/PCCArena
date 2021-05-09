import os
import csv
import subprocess as sp
from pathlib import Path
from typing import Union, List, Tuple

import cv2
import numpy as np
import open3d as o3d
from xvfbwrapper import Xvfb

from libs.metric_base import MetricBase

class ProjectionBasedMetrics(MetricBase):
    """Class for evaluating view dependent metrics of given point clouds.

    View Dependent Metrics:
        Y-PSNR, Cb-PSNR, Cr-PSNR
        SSIM,
        VMAF
    """

    def __init__(
            self,
            ref_pc: Union[str, Path],
            target_pc: Union[str, Path]
        ) -> None:
        super().__init__(ref_pc, target_pc)
        
        # projected image size
        self._width = 1920
        self._height = 1920
        # default point cloud color if it does not have one
        self._pc_color = [0, 0, 0]
        # default background color
        self._bg_color = [0.5, 0.5, 0.5]
        self._vmaf_bin = (
            Path(__file__).parents[1].
            joinpath("dependencies/vmaf.linux").resolve()
        )

    def evaluate(self) -> str:
        """Run the evaluation and generate the formatted evaluation 
        results.
        
        Parameters
        ----------
        camera_parameter : List
            List of tuple
            tuple is like (camera_front[100, 100, 0], camera_up[1, 0, 0])
            You can add as many camera position as possible

        Returns
        -------
        `str`
            The formatted evaluation results.
        """
        
        # [TODO] find a better way to generate this
        rotation_matrice = np.array([
            [0,   0, 0],
            [0, 0.5, 0],
            [0,   1, 0],
            [0, 1.5, 0],
            [0.5, 0, 0],
            [1.5, 0, 0]
        ]) * np.pi
        
        disp = Xvfb()
        disp.start()
        # get projected yuv images of ref. and tar. point cloud with
        # each rotation_matrix
        imgs = self._render_2d_image(rotation_matrice)
        disp.stop()
        
        self._get_quality_metrics(imgs)
        
        ret = '\n'.join(self._results)
        
        return ret

    def _render_2d_image(self, rotation_matrice):
        ref_cloud = o3d.io.read_point_cloud(self._ref_pc)
        tar_cloud = o3d.io.read_point_cloud(self._target_pc)

        if self._has_color is False:
            ref_cloud.paint_uniform_color(self._pc_color)
            tar_cloud.paint_uniform_color(self._pc_color)

        # Align the point clouds based on the oriented bounding box of
        # the reference point cloud
        obb = ref_cloud.get_oriented_bounding_box()
        center = ref_cloud.get_center()
        ref_cloud = ref_cloud.rotate(obb.R, center)
        tar_cloud = tar_cloud.rotate(obb.R, center)

        vis = o3d.visualization.Visualizer()
        vis.create_window(width=self._width, height=self._height)
        opt = vis.get_render_option()
        opt.background_color = self._bg_color
        
        imgs = []
        
        # generate projected 2D image with each rotation_matrix
        for idx, mat in enumerate(rotation_matrice):
            R = ref_cloud.get_rotation_matrix_from_xyz(mat)
            
            ref_tmp = f'ref_{idx}.png'
            tar_tmp = f'tar_{idx}.png'
            
            tmp_cloud = ref_cloud.rotate(R, center)
            vis.add_geometry(tmp_cloud)
            vis.capture_screen_image(ref_tmp, do_render=True)
            vis.clear_geometries()
            
            tmp_cloud = tar_cloud.rotate(R, center)
            vis.add_geometry(tmp_cloud)
            vis.capture_screen_image(tar_tmp, do_render=True)
            vis.clear_geometries()

            ref_BGR = cv2.imread(ref_tmp)
            tar_BGR = cv2.imread(tar_tmp)
            os.remove(ref_tmp)
            os.remove(tar_tmp)
            
            # convert color space from BGR to YUV420
            ref_yuv = cv2.cvtColor(ref_BGR, cv2.COLOR_BGR2YUV_I420)
            tar_yuv = cv2.cvtColor(tar_BGR, cv2.COLOR_BGR2YUV_I420)
            
            # save yuv files
            ref_file = f'ref_{self._width}x{self._height}_I420.yuv'
            tar_file = f'tar_{self._width}x{self._height}_I420.yuv'
            ref_yuv.tofile(ref_file)
            tar_yuv.tofile(tar_file)

            imgs.append((ref_file, tar_file))

        return imgs

    def _get_quality_metrics(self, imgs):
        # keys are related vmaf csv log file
        chosen_metrics = {
            'psnr_y': [],
            'psnr_cb': [],
            'psnr_cr': [],
            'float_ssim': [],
            'vmaf': []
        }
        
        for ref_file, tar_file in imgs:
            log_file = self._vmaf_wrapper(ref_file, tar_file)
            
            # collect value of each metric from the log file
            with open(log_file, 'r') as csvfile:
                # here we only have one row
                row = list(csv.DictReader(csvfile))[0]
            
            os.remove(log_file)
            
            for metric in chosen_metrics.keys():
                chosen_metrics[metric].append(float(row[metric]))

        # calculate mean of each metric
        for metric in chosen_metrics.keys():
            chosen_metrics[metric] = np.array(chosen_metrics[metric]).mean()

        lines = [
            f"======= Projection-based Metrics =======",
            f"Y-PSNR (dB)                    : {chosen_metrics['psnr_y']}",
            f"Cb-PSNR (dB)                   : {chosen_metrics['psnr_cb']}",
            f"Cr-PSNR (dB)                   : {chosen_metrics['psnr_cr']}",
            f"SSIM                           : {chosen_metrics['float_ssim']}",
            f"VMAF                           : {chosen_metrics['vmaf']}"
            "\n",
        ]

        self._results += lines

    def _vmaf_wrapper(self, ref_file, tar_file) -> str:
        log_file = 'result.csv'

        cmd = [
            self._vmaf_bin,
            '--quiet',
            f'--reference={ref_file}',
            f'--distorted={tar_file}',
            f'--width={self._width}',
            f'--height={self._height}',
            '--pixel_format=420',
            '--bitdepth=8',
            '--feature=psnr',
            '--feature=float_ssim',
            f'--output={log_file}',
            '--csv'
        ]

        sp.run(cmd)

        return log_file
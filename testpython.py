from collections import defaultdict
import logging
import os
import cv2
import numpy as np
import pandas as pd
import open3d as o3d
import time
# from pyntcloud import PyntCloud
import re
import signal
import numpy as np
import csv
from itertools import zip_longest
import subprocess as sp
from xvfbwrapper import Xvfb

from evaluator.summary import summarize_all_to_csv
from evaluator.metrics import ViewDependentMetrics

# summarize_all_to_csv('experiments')

# rotation_matrixs = np.array([
#     [0,   0, 0],
#     [0, 0.5, 0],
#     [0,   1, 0],
#     [0, 1.5, 0],
#     [0.5, 0, 0],
#     [1.5, 0, 0]
# ]) * np.pi
# print(rotation_matrixs)

# VDMetrics = ViewDependentMetrics()
# VDMetrics._render3d_to_2d('m1.ply', 'm2.ply', ([1,1,0], [50,10,45]))

disp = Xvfb()
disp.start()

pc = o3d.io.read_point_cloud('color.ply')
# pc = pc.paint_uniform_color([0, 0, 0])
obb = pc.get_oriented_bounding_box()
center = pc.get_center()
pc = pc.rotate(obb.R, center)

vis = o3d.visualization.Visualizer()
vis.create_window(width=1920, height=1920)
opt = vis.get_render_option()
opt.background_color = [0.5, 0.5, 0.5]

vis.add_geometry(pc)
vis.capture_screen_image('before.png', do_render=True)

R = pc.get_rotation_matrix_from_xyz((-np.pi / 2, 0, 0))
pc = pc.rotate(R, center)
vis.update_geometry(pc)
after = vis.capture_screen_image('after.png', do_render=True)

img = cv2.imread('after.png')

yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420)
yuv.tofile('after.yuv')

vis.destroy_window()
del vis, opt

disp.stop()

# def work():
#     disp_id = 99
#     cmd = ['Xvfb', f':{disp_id}']
#     # cmd = f"Xvfb :{disp_id}"
#     print(cmd)

#     p = sp.Popen(cmd)
#     old_env = dict(os.environ)
#     os.environ['DISPLAY'] = f":{disp_id}"
#     os.system("echo $DISPLAY")
#     time.sleep(1)
#     try:
#         vis = o3d.visualization.Visualizer()
#         vis.create_window(visible=False)
#         vis.destroy_window()
#         del vis
#         time.sleep(5)
#     finally:
#         # os.killpg(os.getpgid(p.pid), signal.SIGTERM) 
#         # try:
#         p.terminate()
#         p.wait()
#         # except:
#         #     pass
#         # os.kill(p.pid, signal.SIGTERM)
#         print("kill done")
#         os.environ.clear()
#         os.system("echo $DISPLAY")
#         os.environ.update(old_env)
#         os.system("echo $DISPLAY")
#     return

# work()
# os.kill(pid, signal.SIGTERM)
# time.sleep(3)
# print("kill Xvfb")
# os.killpg(os.getpgid(p.pid), signal.SIGTERM) 
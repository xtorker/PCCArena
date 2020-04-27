import os
import open3d as o3d
import numpy as np
import argparse
import glob
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

def custom_draw_geometry_with_rotation(model, model_type, filename):
	
	custom_draw_geometry_with_rotation.index = 0
	custom_draw_geometry_with_rotation.vis = o3d.visualization.Visualizer()
	custom_draw_geometry_with_rotation.images = []
		
	if not os.path.exists("./image/"):
		os.makedirs("./image/")
	
	def rotate_view(vis):
		
		ctr = vis.get_view_control()
		ctr.change_field_of_view(step=-30.0)
		glb = custom_draw_geometry_with_rotation

		if glb.index >= 0:
			image = vis.capture_screen_float_buffer(False)
			image_path = os.path.join(ROOT_PATH, 'image/{:03d}.png'.format(glb.index))
			plt.imsave(image_path, np.asarray(image), dpi=1)
		
		if glb.index < 110:
			ctr.rotate(20.0, 0.0)
		elif glb.index < 220:
			ctr.rotate(0.0, 20.0)
		else:
			custom_draw_geometry_with_rotation.vis.register_animation_callback(None)
			vis.destroy_window()

		glb.index = glb.index + 1
			
		return False
	
	vis = custom_draw_geometry_with_rotation.vis
	vis.create_window()
	vis.add_geometry(model)
	opt = vis.get_render_option()
	opt.background_color = np.asarray([0, 0, 0])
	
	if model_type == 'pc':
		opt.point_color_option = o3d.visualization.PointColorOption.Color
	else:
		opt.mesh_color_option = o3d.visualization.MeshColorOption.Color
	
	ctr = vis.get_view_control()
	ctr.rotate(0.0, -450.0)
	vis.register_animation_callback(rotate_view)
	vis.run()

	for i in range(220):
		image_path = os.path.join(ROOT_PATH, 'image/{:03d}.png'.format(i))
		im = Image.open(image_path)
		custom_draw_geometry_with_rotation.images.append(im)

	gif_path = os.path.join(ROOT_PATH, 'image', filename+'.gif')
	custom_draw_geometry_with_rotation.images[1].save(gif_path, save_all=True, duration=60, loop=0, \
													  append_images=custom_draw_geometry_with_rotation.images[2:])
	
	remove_list = glob.glob(os.path.join(ROOT_PATH, 'image/*.png'))
	for f in remove_list:
		os.remove(f)
	#o3d.visualization.draw_geometries_with_animation_callback([pcd], rotate_view)
'''
def custom_draw_geometry_with_key_callback(pcd):

    def change_background_to_black(vis):
        opt = vis.get_render_option()
        opt.background_color = np.asarray([0, 0, 0])
        return False

    def load_render_option(vis):
        vis.get_render_option().load_from_json(
            "../../TestData/renderoption.json")
        return False

    def capture_depth(vis):
        depth = vis.capture_depth_float_buffer()
        plt.imshow(np.asarray(depth))
        plt.show()
        return False

    def capture_image(vis):
        image = vis.capture_screen_float_buffer()
        plt.imshow(np.asarray(image))
        plt.show()
        return False

    key_to_callback = {}
    key_to_callback[ord("K")] = change_background_to_black
    key_to_callback[ord("R")] = load_render_option
    key_to_callback[ord(",")] = capture_depth
    key_to_callback[ord(".")] = capture_image
    o3d.visualization.draw_geometries_with_key_callbacks([pcd], key_to_callback)


def custom_draw_geometry_with_camera_trajectory(pcd):
    custom_draw_geometry_with_camera_trajectory.index = -1
    custom_draw_geometry_with_camera_trajectory.trajectory =\
            o3d.io.read_pinhole_camera_trajectory(
                    "../../TestData/camera_trajectory.json")
    custom_draw_geometry_with_camera_trajectory.vis = o3d.visualization.Visualizer(
    )
    if not os.path.exists("../../TestData/image/"):
        os.makedirs("../../TestData/image/")
    if not os.path.exists("../../TestData/depth/"):
        os.makedirs("../../TestData/depth/")

    def move_forward(vis):
        # This function is called within the o3d.visualization.Visualizer::run() loop
        # The run loop calls the function, then re-render
        # So the sequence in this function is to:
        # 1. Capture frame
        # 2. index++, check ending criteria
        # 3. Set camera
        # 4. (Re-render)
        ctr = vis.get_view_control()
        glb = custom_draw_geometry_with_camera_trajectory
        if glb.index >= 0:
            print("Capture image {:05d}".format(glb.index))
            depth = vis.capture_depth_float_buffer(False)
            image = vis.capture_screen_float_buffer(False)
            plt.imsave("../../TestData/depth/{:05d}.png".format(glb.index),\
                    np.asarray(depth), dpi = 1)
            plt.imsave("../../TestData/image/{:05d}.png".format(glb.index),\
                    np.asarray(image), dpi = 1)
            #vis.capture_depth_image("depth/{:05d}.png".format(glb.index), False)
            #vis.capture_screen_image("image/{:05d}.png".format(glb.index), False)
        glb.index = glb.index + 1
        if glb.index < len(glb.trajectory.parameters):
            ctr.convert_from_pinhole_camera_parameters(
                glb.trajectory.parameters[glb.index])
        else:
            custom_draw_geometry_with_camera_trajectory.vis.\
                    register_animation_callback(None)
        return False

    vis = custom_draw_geometry_with_camera_trajectory.vis
    vis.create_window()
    vis.add_geometry(pcd)
    vis.get_render_option().load_from_json("../../TestData/renderoption.json")
    vis.register_animation_callback(move_forward)
    vis.run()
    vis.destroy_window()
'''

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser()
	parser.add_argument('file_path', help='Path to point cloud or mesh')
	parser.add_argument('type', help='Specify model type', choices=['pc', 'mesh'])
	args = parser.parse_args()

	basename = os.path.basename(args.file_path)
	filename, ext = os.path.splitext(basename)

	if args.type == 'pc':
		pcd = o3d.io.read_point_cloud(args.file_path)
		pcd.paint_uniform_color([1, 1, 0])
		custom_draw_geometry_with_rotation(pcd, args.type, filename)
	else:
		mesh = o3d.io.read_triangle_mesh(args.file_path)
		mesh.paint_uniform_color([1, 1, 0])
		custom_draw_geometry_with_rotation(mesh, args.type, filename)

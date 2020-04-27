#include <pcl/io/ply_io.h>
#include <pcl/io/pcd_io.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/conversions.h>
#include <pcl/compression/octree_pointcloud_compression.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdio>
#include <cstdlib>
#include <chrono>

typedef pcl::PointXYZ PointT;

int main (int argc, char **argv)
{
	//******************************************//
	// usage: ./PCL_compression [input] [output] [mode] [pointRes] [octreeRes] [doVoxel] [doColor] [colorBitRes]
	// arguments:
	//		[input]: path to (original point cloud/compressed binary file) based on [mode]
	//		[output]: path to (compressed binary file/decompressed point cloud) based on [mode]
	//		[mode]: 0 -> Encode
	//				1 -> Decode
	//		[pointRes]: define the coding precision for point coordinates, should be lower than sampling noise
	//		[octreeRes]: define the voxel size of the octree during encoding
	//		[doVoxel]: drop the duplicate points during voxelization (0: false, 1:true)
	//		[doColor]: enable color attribute encoding (0: false, 1:true)
	//		[colorBitRes]: define the amount of bits per color attribute to be encoded
	//******************************************//

	bool showStatistics_arg = true;
	double pointResolution_arg = atof(argv[4]);
	double octreeResolution_arg = atof(argv[5]);
	bool doVoxelGridDownDownSampling_arg;
	std::istringstream(argv[6]) >> doVoxelGridDownDownSampling_arg;
	unsigned int iFrameRate_arg = 100;
	bool doColorEncoding_arg;
	std::istringstream(argv[7]) >> doColorEncoding_arg;
	unsigned char colorBitResolution_arg = atof(argv[8]);

	pcl::io::compression_Profiles_e compressionProfile = pcl::io::MANUAL_CONFIGURATION;
	pcl::io::OctreePointCloudCompression<PointT> encoder(compressionProfile, showStatistics_arg, pointResolution_arg, octreeResolution_arg, doVoxelGridDownDownSampling_arg, iFrameRate_arg, doColorEncoding_arg, colorBitResolution_arg);
	pcl::io::OctreePointCloudCompression<PointT> decoder;

	if(atof(argv[3]) == 0)
	{
		// Read input point cloud from PLY file
		std::cerr << "Read point cloud from file ...\n";
		pcl::PLYReader reader;
		pcl::PointCloud<PointT>::Ptr cloud (new pcl::PointCloud<PointT>);
		reader.read(argv[1], *cloud);
		const pcl::PointCloud<PointT>::ConstPtr cloudIn(cloud);

		std::stringstream compressedData;
		std::cerr << "Start compressing ...\n";
		encoder.encodePointCloud(cloudIn, compressedData);
		std::stringstream compressedDataCopy(compressedData.str());
		
		// Save compressed binary stream to file
		std::cerr << "Save compressed data ...\n";
		std::ofstream compressedFile (argv[2], std::ofstream::binary);
		compressedFile << compressedDataCopy.rdbuf();
		compressedFile.close();
	}
	else
	{
		// Read compressed data from binary file
		std::cerr << "Read compressed data from file ...\n";
		std::ifstream compressedFile (argv[1], std::ifstream::binary);
		std::stringstream compressedData;
		compressedData << compressedFile.rdbuf();
		std::stringstream compressedDataCopy(compressedData.str());

		pcl::PointCloud<PointT>::Ptr cloudOut (new pcl::PointCloud<PointT>);
		std::cerr << "Start decompressing ...\n";
		decoder.decodePointCloud(compressedDataCopy, cloudOut);

		// Write decompressed point cloud result to PLY file
		std::cerr << "Write decompressed point cloud to file ...\n";
		pcl::PLYWriter writer;
		writer.write<PointT>(argv[2], *cloudOut, false);
	}
	return 0;
}

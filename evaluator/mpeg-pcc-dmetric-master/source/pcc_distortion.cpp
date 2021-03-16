/*
 * Software License Agreement
 *
 *  Point to plane metric for point cloud distortion measurement
 *  Copyright (c) 2016, MERL
 *
 *  All rights reserved.
 *
 *  Contributors:
 *    Dong Tian <tian@merl.com>
 *    Maja Krivokuca <majakri01@gmail.com>
 *    Phil Chou <philchou@msn.com>
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *   * Neither the name of the copyright holder(s) nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 *
 */

#include <cstdint>
#include <iostream>
#include <fstream>
#include <sstream>
#include <limits.h>
#include <memory.h>

#include "pcc_processing.hpp"
#include "pcc_distortion.hpp"

using namespace std;
using namespace pcc_quality;
using namespace nanoflann;

// Representation of linear point cloud indexes in kd-tree
typedef uint32_t index_type;

// Representation of distance metric during kd-tree search
typedef double distance_type;

// A version of nanoflann::metric_L2 that forces metric (distance)
// calculations to be performed using double precision floats.
// NB: by default nanoflann::metric_L2 will be used with the metric
//     type of T = num_t (the coordinate type).
struct metric_L2_double
{
  template <class T, class DataSource>
  struct traits
  {
    typedef nanoflann::L2_Adaptor<T, DataSource, double> distance_t;
  };
};

typedef KDTreeVectorOfVectorsAdaptor<
    vector<PointXYZSet::point_type>,     // array type
    PointXYZSet::point_type::value_type, // coordinate type
    3,                                   // num dimensions
    metric_L2_double,                    // distance class
    index_type                           // index type (eg size_t)
    >
    my_kd_tree_t;

#define PRINT_TIMING 0

/*
 ***********************************************
   Implementation of local functions
 ***********************************************
 */

/**!
 * \function
 *   Compute the minimum and maximum NN distances, find out the
 *   intrinsic resolutions
 * \parameters
 *   @param cloudA: point cloud
 *   @param minDist: output
 *   @param maxDist: output
 * \note
 *   PointT typename of point used in point cloud
 * \author
 *   Dong Tian, MERL
 */
void findNNdistances(PccPointCloud &cloudA, double &minDist, double &maxDist)
{
  maxDist = numeric_limits<double>::min();
  minDist = numeric_limits<double>::max();
  double distTmp = 0;
  mutex myMutex;

  my_kd_tree_t mat_index(3, cloudA.xyz.p, 10); // dim, cloud, max leaf

#pragma omp parallel for
  for (long i = 0; i < cloudA.size; ++i)
  {
    // cout << "*** " << i << endl;
    // do a knn search
    const size_t num_results = 3;
    std::array<index_type, num_results> indices;
    std::array<distance_type, num_results> sqrDist;

    mat_index.query(&cloudA.xyz.p[i][0], num_results, &indices[0], &sqrDist[0]);

    if (indices[0] != i || sqrDist[1] <= 0.0000000001)
    {
      // Print some warnings
      // cerr << "Error! nFound = " << nFound << ", i, iFound = " << i << ", " << indices[0] << ", " << indices[1] << endl;
      // cerr << "       Distances = " << sqrDist[0] << ", " << sqrDist[1] << endl;
      // cerr << "  Some points are repeated!" << endl;
    }
    else
    {
      // Use the second one. assume the first one is the current point
      myMutex.lock();
      distTmp = sqrt(sqrDist[1]);
      if (distTmp > maxDist)
        maxDist = distTmp;
      if (distTmp < minDist)
        minDist = distTmp;
      myMutex.unlock();
    }
  }
}

/**!
 * \function
 *   Convert the MSE error to PSNR numbers
 * \parameters
 *   @param cloudA:  the original point cloud
 *   @param dist2: the sqr of the distortion
 *   @param p: the peak value for conversion
 *   @param factor: default 1.0. For geometry errors value 3.0 should be provided
 * \return
 *   psnr value
 * \note
 *   PointT typename of point used in point cloud
 * \author
 *   Dong Tian, MERL
 */
float getPSNR(float dist2, float p, float factor = 1.0)
{
  float max_energy = p * p;
  float psnr = 10 * log10((factor * max_energy) / dist2);

  return psnr;
}

/**!
 * \function
 *   Derive the normals for the decoded point cloud based on the
 *   normals in the original point cloud
 * \parameters
 *   @param cloudA:  the original point cloud
 *   @param cloudNormalsA: the normals in the original point cloud
 *   @param cloudB:  the decoded point cloud
 *   @param cloudNormalsB: the normals in the original point
 *     cloud. Output parameter
 * \note
 *   PointT typename of point used in point cloud
 * \author
 *   Dong Tian, MERL
 */
void scaleNormals(PccPointCloud &cloudNormalsA, PccPointCloud &cloudB, PccPointCloud &cloudNormalsB, bool bAverageNormals)
{
  // Prepare the buffer to compute the average normals
#if PRINT_TIMING
  clock_t t1 = clock();
#endif

  cloudNormalsB.normal.init(cloudB.size);
  vector<int> counts(cloudB.size);

  if (1)
  {
    my_kd_tree_t mat_indexB(3, cloudB.xyz.p, 10); // dim, cloud, max leaf
    for (long i = 0; i < cloudNormalsA.size; i++)
    {
      if (bAverageNormals)
      {
        const size_t num_results_max = 30;
        const size_t num_results_incr = 5;
        size_t num_results = 0;

        std::array<index_type, num_results_max> indices;
        std::array<distance_type, num_results_max> sqrDist;
        do
        {
          num_results += num_results_incr;
          mat_indexB.query(&cloudNormalsA.xyz.p[i][0], num_results, &indices[0], &sqrDist[0]);
        } while (sqrDist[0] == sqrDist[num_results - 1] && num_results + num_results_incr <= num_results_max);
        for (size_t j = 0; j < num_results; j++)
        {
          if (sqrDist[0] == sqrDist[j])
          {
            cloudNormalsB.normal.n[indices[j]][0] += cloudNormalsA.normal.n[i][0];
            cloudNormalsB.normal.n[indices[j]][1] += cloudNormalsA.normal.n[i][1];
            cloudNormalsB.normal.n[indices[j]][2] += cloudNormalsA.normal.n[i][2];
            counts[indices[j]]++;
          }
        }
      }
      else
      {
        const size_t num_results = 1;
        std::array<index_type, num_results> indices;
        std::array<distance_type, num_results> sqrDist;

        mat_indexB.query(&cloudNormalsA.xyz.p[i][0], num_results, &indices[0], &sqrDist[0]);

        cloudNormalsB.normal.n[indices[0]][0] += cloudNormalsA.normal.n[i][0];
        cloudNormalsB.normal.n[indices[0]][1] += cloudNormalsA.normal.n[i][1];
        cloudNormalsB.normal.n[indices[0]][2] += cloudNormalsA.normal.n[i][2];
        counts[indices[0]]++;
      }
    }
  }

  // average now
  my_kd_tree_t mat_indexA(3, cloudNormalsA.xyz.p, 10); // dim, cloud, max leaf
  for (long i = 0; i < cloudB.size; i++)
  {
    int nCount = counts[i];
    if (nCount > 0) // main branch
    {
      cloudNormalsB.normal.n[i][0] = cloudNormalsB.normal.n[i][0] / nCount;
      cloudNormalsB.normal.n[i][1] = cloudNormalsB.normal.n[i][1] / nCount;
      cloudNormalsB.normal.n[i][2] = cloudNormalsB.normal.n[i][2] / nCount;
    }
    else
    {
      if (bAverageNormals)
      {
        const size_t num_results_max = 30;
        const size_t num_results_incr = 5;
        size_t num_results = 0;
        std::array<index_type, num_results_max> indices;
        std::array<distance_type, num_results_max> sqrDist;
        do
        {
          num_results += num_results_incr;
          mat_indexA.query(&cloudB.xyz.p[i][0], num_results, &indices[0], &sqrDist[0]);
        } while (sqrDist[0] == sqrDist[num_results - 1] && num_results + num_results_incr <= num_results_max);
        size_t num = 0;
        for (size_t j = 0; j < num_results; j++)
        {
          if (sqrDist[0] == sqrDist[j])
          {
            cloudNormalsB.normal.n[i][0] += cloudNormalsA.normal.n[indices[j]][0];
            cloudNormalsB.normal.n[i][1] += cloudNormalsA.normal.n[indices[j]][1];
            cloudNormalsB.normal.n[i][2] += cloudNormalsA.normal.n[indices[j]][2];
            num++;
          }
        }
        cloudNormalsB.normal.n[i][0] /= num;
        cloudNormalsB.normal.n[i][1] /= num;
        cloudNormalsB.normal.n[i][2] /= num;
      }
      else
      {
        const size_t num_results = 1;
        std::array<index_type, num_results> indices;
        std::array<distance_type, num_results> sqrDist;

        mat_indexA.query(&cloudB.xyz.p[i][0], num_results, &indices[0], &sqrDist[0]);

        cloudNormalsB.normal.n[i][0] = cloudNormalsA.normal.n[indices[0]][0];
        cloudNormalsB.normal.n[i][1] = cloudNormalsA.normal.n[indices[0]][1];
        cloudNormalsB.normal.n[i][2] = cloudNormalsA.normal.n[indices[0]][2];
      }
    }
  }

  // Set the flag
  cloudNormalsB.bNormal = true;

#if PRINT_TIMING
  clock_t t2 = clock();
  cout << "   Converting normal vector DONE. It takes " << (t2 - t1) / CLOCKS_PER_SEC << " seconds (in CPU time)." << endl;
#endif
}

/**
   \brief helper function to convert RGB to YUV (BT.709 or YCoCg-R)
 */
void convertRGBtoYUV(int type, const std::array<unsigned char, 3> &in_rgb,
                     float *out_yuv)
{
  // color space conversion to YUV

  if (type == 0)
  {
    for (int d = 0; d < 3; d++)
      out_yuv[d] = float(in_rgb[d]);
  }
  else if (type == 8)
  {
    int g = in_rgb[1];
    int b = in_rgb[2];
    int r = in_rgb[0];

    int co = r - b;
    int t = b + (co >> 1);
    int cg = g - t;
    int y = t + (cg >> 1);

    int offset = 1 << 8;

    out_yuv[0] = y;
    out_yuv[1] = co + offset;
    out_yuv[2] = cg + offset;
  }
  else // type 1
  {
    out_yuv[0] = float((0.2126 * in_rgb[0] + 0.7152 * in_rgb[1] + 0.0722 * in_rgb[2]) / 255.0);
    out_yuv[1] = float((-0.1146 * in_rgb[0] - 0.3854 * in_rgb[1] + 0.5000 * in_rgb[2]) / 255.0 + 0.5000);
    out_yuv[2] = float((0.5000 * in_rgb[0] - 0.4542 * in_rgb[1] - 0.0458 * in_rgb[2]) / 255.0 + 0.5000);
  }
}

/**!
 * \function
 *   To compute "one-way" quality metric: Point-to-Point, Point-to-Plane
 *   and RGB. Loop over each point in A. Normals in B to be used
 *
 *   1) For each point in A, find a corresponding point in B.
 *   2) Form an error vector between the point pair.
 *   3) Use the length of the error vector as point-to-point measure
 *   4) Project the error vector along the normals in B, use the length
 *   of the projected error vector as point-to-plane measure
 *
 *   @param cloudA: Reference point cloud. e.g. the original cloud, on
 *     which normals would be estimated. It is the full set of point
 *     cloud. Multiple points in count
 *   @param cloudB: Processed point cloud. e.g. the decoded cloud
 *   @param cPar: Command line parameters
 *   @param cloudNormalsB: Normals for cloudB
 *   @param metric: updated quality metric, to be returned
 * \note
 *   PointT typename of point used in point cloud
 * \author
 *   Dong Tian, MERL
 */
void findMetric(PccPointCloud &cloudA, PccPointCloud &cloudB, commandPar &cPar, PccPointCloud &cloudNormalsB, qMetric &metric)
{
  mutex myMutex;

#if PRINT_TIMING
  clock_t t2 = clock();
#endif
  double max_dist_b_c2c = std::numeric_limits<double>::min();
  double sse_dist_b_c2c = 0;
  double max_dist_b_c2p = std::numeric_limits<double>::min();
  double sse_dist_b_c2p = 0;
  double max_reflectance = std::numeric_limits<double>::min();
  double sse_reflectance = 0;
  long num = 0;

  double sse_color[3];
  sse_color[0] = sse_color[1] = sse_color[2] = 0.0;
  double max_colorRGB[3];
  max_colorRGB[0] = max_colorRGB[1] = max_colorRGB[2] = std::numeric_limits<double>::min();

  my_kd_tree_t mat_indexB(3, cloudB.xyz.p, 10); // dim, cloud, max leaf

  const size_t num_results_max = 30;
  const size_t num_results_incr = 5;
#if DUPLICATECOLORS_DEBUG
  long NbNeighborsDst[num_results_max] = {};
#endif

#pragma omp parallel for
  for (long i = 0; i < cloudA.size; i++)
  {
    size_t num_results = num_results_incr;
    // For point 'i' in A, find its nearest neighbor in B. store it in 'j'
    std::array<index_type, num_results_max> indices;
    std::array<distance_type, num_results_max> sqrDist;
    do
    {
      num_results += num_results_incr;
      if (!mat_indexB.query(&cloudA.xyz.p[i][0], num_results, &indices[0], &sqrDist[0]))
      {
        cout << " WARNING: requested neighbors could not be found " << endl;
      }
    } while (sqrDist[0] == sqrDist[num_results - 1] && cPar.bAverageNormals && num_results + num_results_incr <= num_results_max);

    int j = indices[0];
    if (j < 0)
      continue;

    std::vector<size_t> sameDistPoints;
    if (cPar.bColor || (!cPar.c2c_only && cloudNormalsB.bNormal))
    {
      sameDistPoints.push_back(indices[0]);
      for (size_t n = 1; n < num_results; n++)
      {
        if (fabs(sqrDist[n] - sqrDist[n - 1]) < 1e-8)
        {
          sameDistPoints.push_back(indices[n]);
        }
        else
        {
          break;
        }
      }
    }

    // Compute the error vector
    std::array<double, 3> errVector;
    errVector[0] = cloudA.xyz.p[i][0] - cloudB.xyz.p[j][0];
    errVector[1] = cloudA.xyz.p[i][1] - cloudB.xyz.p[j][1];
    errVector[2] = cloudA.xyz.p[i][2] - cloudB.xyz.p[j][2];

    // Compute point-to-point, which should be equal to sqrDist[0]
    double distProj_c2c = errVector[0] * errVector[0] + errVector[1] * errVector[1] + errVector[2] * errVector[2];

    // Compute point-to-plane
    // Normals in B will be used for point-to-plane
    double distProj = 0.0;
    if (!cPar.c2c_only && cloudNormalsB.bNormal)
    {
      if (cPar.bAverageNormals)
      {
        for (auto &index : sameDistPoints)
        {
          if (!isnan(cloudNormalsB.normal.n[index][0]) &&
              !isnan(cloudNormalsB.normal.n[index][1]) &&
              !isnan(cloudNormalsB.normal.n[index][2]))
          {
            double dist = pow((cloudA.xyz.p[i][0] - cloudB.xyz.p[index][0]) * cloudNormalsB.normal.n[index][0] +
                                  (cloudA.xyz.p[i][1] - cloudB.xyz.p[index][1]) * cloudNormalsB.normal.n[index][1] +
                                  (cloudA.xyz.p[i][2] - cloudB.xyz.p[index][2]) * cloudNormalsB.normal.n[index][2],
                              2.f);
            distProj += dist;
          }
          else
          {
            distProj += cloudA.xyz.p[i][0] - cloudB.xyz.p[index][0] +
                        cloudA.xyz.p[i][1] - cloudB.xyz.p[index][1] +
                        cloudA.xyz.p[i][2] - cloudB.xyz.p[index][2];
          }
        }
        distProj /= (double)sameDistPoints.size();
      }
      else
      {
        if (!isnan(cloudNormalsB.normal.n[j][0]) &&
            !isnan(cloudNormalsB.normal.n[j][1]) &&
            !isnan(cloudNormalsB.normal.n[j][2]))
        {
          distProj = (errVector[0] * cloudNormalsB.normal.n[j][0] +
                      errVector[1] * cloudNormalsB.normal.n[j][1] +
                      errVector[2] * cloudNormalsB.normal.n[j][2]);
          distProj *= distProj; // power 2 for MSE
        }
        else
        {
          distProj = distProj_c2c;
        }
      }
    }

    double distColor[3];
    distColor[0] = distColor[1] = distColor[2] = 0.0;
    double distColorRGB[3];
    distColorRGB[0] = distColorRGB[1] = distColorRGB[2] = std::numeric_limits<double>::min();
    if (cPar.bColor && cloudA.bRgb && cloudB.bRgb)
    {
      // add Y-value of the point into histogram
      float yuv[3];
      convertRGBtoYUV(1, cloudA.rgb.c[i], yuv);
      metric.y_hist[int(round(yuv[0] * 255))]++;

      float out[3];
      float in[3];
      convertRGBtoYUV(cPar.mseSpace, cloudA.rgb.c[i], in);

      if (cPar.neighborsProc)
      {
        unsigned int r = 0, g = 0, b = 0;
        std::array<unsigned char, 3> color;
        switch (cPar.neighborsProc)
        {
        case 0:
          break;
        case 1: // Average
        case 2: // Weighted average
        {
          int nbdupcumul = 0;
          for (auto &index : sameDistPoints)
          {
            int nbdup = cloudB.xyz.nbdup[index];
            r += nbdup * cloudB.rgb.c[index][0];
            g += nbdup * cloudB.rgb.c[index][1];
            b += nbdup * cloudB.rgb.c[index][2];
            nbdupcumul += nbdup;
          }
          assert(nbdupcumul);
          color[0] = (unsigned char)round((double)r / nbdupcumul);
          color[1] = (unsigned char)round((double)g / nbdupcumul);
          color[2] = (unsigned char)round((double)b / nbdupcumul);
        }
        break;
        case 3: // Min
        {
          unsigned int distColorMin = (std::numeric_limits<unsigned int>::max)();
          size_t indexMin = 0;
          for (auto &index : sameDistPoints)
          {
            unsigned int distRGB = (cloudA.rgb.c[i][0] - cloudB.rgb.c[index][0]) * (cloudA.rgb.c[i][0] - cloudB.rgb.c[index][0]) + (cloudA.rgb.c[i][1] - cloudB.rgb.c[index][1]) * (cloudA.rgb.c[i][1] - cloudB.rgb.c[index][1]) + (cloudA.rgb.c[i][2] - cloudB.rgb.c[index][2]) * (cloudA.rgb.c[i][2] - cloudB.rgb.c[index][2]);
            if (distRGB < distColorMin)
            {
              distColorMin = distRGB;
              indexMin = index;
            }
          }
          color = cloudB.rgb.c[indexMin];
        }
        break;
        case 4: // Max
        {
          unsigned int distColorMax = 0;
          size_t indexMax = 0;
          for (auto &index : sameDistPoints)
          {
            unsigned int distRGB = (cloudA.rgb.c[i][0] - cloudB.rgb.c[index][0]) * (cloudA.rgb.c[i][0] - cloudB.rgb.c[index][0]) + (cloudA.rgb.c[i][1] - cloudB.rgb.c[index][1]) * (cloudA.rgb.c[i][1] - cloudB.rgb.c[index][1]) + (cloudA.rgb.c[i][2] - cloudB.rgb.c[index][2]) * (cloudA.rgb.c[i][2] - cloudB.rgb.c[index][2]);
            if (distRGB > distColorMax)
            {
              distColorMax = distRGB;
              indexMax = index;
            }
          }
          color = cloudB.rgb.c[indexMax];
        }
        break;
        }

        convertRGBtoYUV(cPar.mseSpace, color, out);
        distColorRGB[0] = (cloudA.rgb.c[i][0] - color[0]) * (cloudA.rgb.c[i][0] - color[0]);
        distColorRGB[1] = (cloudA.rgb.c[i][1] - color[1]) * (cloudA.rgb.c[i][1] - color[1]);
        distColorRGB[2] = (cloudA.rgb.c[i][2] - color[2]) * (cloudA.rgb.c[i][2] - color[2]);
      }
      else
      {
        convertRGBtoYUV(cPar.mseSpace, cloudB.rgb.c[j], out);
        distColorRGB[0] = (cloudA.rgb.c[i][0] - cloudB.rgb.c[j][0]) * (cloudA.rgb.c[i][0] - cloudB.rgb.c[j][0]);
        distColorRGB[1] = (cloudA.rgb.c[i][1] - cloudB.rgb.c[j][1]) * (cloudA.rgb.c[i][1] - cloudB.rgb.c[j][1]);
        distColorRGB[2] = (cloudA.rgb.c[i][2] - cloudB.rgb.c[j][2]) * (cloudA.rgb.c[i][2] - cloudB.rgb.c[j][2]);
      }

      distColor[0] = (in[0] - out[0]) * (in[0] - out[0]);
      distColor[1] = (in[1] - out[1]) * (in[1] - out[1]);
      distColor[2] = (in[2] - out[2]) * (in[2] - out[2]);
    }

    double distReflectance;
    distReflectance = 0.0;
    if (cPar.bLidar && cloudA.bLidar && cloudB.bLidar)
    {
      double diff = cloudA.lidar.reflectance[i] - cloudB.lidar.reflectance[j];
      distReflectance = diff * diff;
    }

    myMutex.lock();

    num++;
    // mean square distance
    sse_dist_b_c2c += distProj_c2c;
    if (distProj_c2c > max_dist_b_c2c)
      max_dist_b_c2c = distProj_c2c;
    if (!cPar.c2c_only)
    {
      sse_dist_b_c2p += distProj;
      if (distProj > max_dist_b_c2p)
        max_dist_b_c2p = distProj;
    }
    if (cPar.bColor)
    {
      sse_color[0] += distColor[0];
      sse_color[1] += distColor[1];
      sse_color[2] += distColor[2];

      max_colorRGB[0] = max(max_colorRGB[0], distColorRGB[0]);
      max_colorRGB[1] = max(max_colorRGB[1], distColorRGB[1]);
      max_colorRGB[2] = max(max_colorRGB[2], distColorRGB[2]);
    }
    if (cPar.bLidar && cloudA.bLidar && cloudB.bLidar)
    {
      sse_reflectance += distReflectance;
      max_reflectance = max(max_reflectance, distReflectance);
    }

#if DUPLICATECOLORS_DEBUG
    for (long n = 0; n < num_results; n++)
      if (rgb[n].size())
        NbNeighborsDst[n]++;
#endif

    myMutex.unlock();
  }
#if DUPLICATECOLORS_DEBUG
  cout << " DEBUG: " << NbNeighborsDst[1] << " points (" << (float)NbNeighborsDst[1] * 100.0 / cloudA.size << "%) found with at least 2 neighbors at the same minimum distance" << endl;
#endif

  metric.c2p_acd = float(sse_dist_b_c2p / num);
  metric.c2c_acd = float(sse_dist_b_c2c / num);
  metric.c2p_hausdorff = float(max_dist_b_c2p);
  metric.c2c_hausdorff = float(max_dist_b_c2c);

  if (cPar.bColor)
  {
    // normalize Y histogram
    int y_hist_sum = 0;
    for (int i = 0; i < 256; i++)
    {
      y_hist_sum += metric.y_hist[i];
    }

    for (int i = 0; i < 256; i++)
    {
      metric.y_hist[i] = metric.y_hist[i] / y_hist_sum;
    }

    metric.color_mse[0] = float(sse_color[0] / num);
    metric.color_mse[1] = float(sse_color[1] / num);
    metric.color_mse[2] = float(sse_color[2] / num);

    if (cPar.mseSpace == 1) //YCbCr
    {
      metric.color_psnr[0] = getPSNR(metric.color_mse[0], 1.0);
      metric.color_psnr[1] = getPSNR(metric.color_mse[1], 1.0);
      metric.color_psnr[2] = getPSNR(metric.color_mse[2], 1.0);
    }
    else if (cPar.mseSpace == 0) //RGB
    {
      metric.color_psnr[0] = getPSNR(metric.color_mse[0], 255);
      metric.color_psnr[1] = getPSNR(metric.color_mse[1], 255);
      metric.color_psnr[2] = getPSNR(metric.color_mse[2], 255);
    }
    else if (cPar.mseSpace == 8) // YCoCg-R
    {
      metric.color_psnr[0] = getPSNR(metric.color_mse[0], 255);
      metric.color_psnr[1] = getPSNR(metric.color_mse[1], 511);
      metric.color_psnr[2] = getPSNR(metric.color_mse[2], 511);
    }

    metric.color_rgb_hausdorff[0] = float(max_colorRGB[0]);
    metric.color_rgb_hausdorff[1] = float(max_colorRGB[1]);
    metric.color_rgb_hausdorff[2] = float(max_colorRGB[2]);

    metric.color_rgb_hausdorff_psnr[0] = getPSNR(metric.color_rgb_hausdorff[0], 255.0);
    metric.color_rgb_hausdorff_psnr[1] = getPSNR(metric.color_rgb_hausdorff[1], 255.0);
    metric.color_rgb_hausdorff_psnr[2] = getPSNR(metric.color_rgb_hausdorff[2], 255.0);
  }

  if (cPar.bLidar)
  {
    metric.reflectance_mse = float(sse_reflectance / num);
    metric.reflectance_psnr = getPSNR(float(metric.reflectance_mse), float(std::numeric_limits<unsigned short>::max()));
    metric.reflectance_hausdorff = float(max_reflectance);
    metric.reflectance_hausdorff_psnr = getPSNR(metric.reflectance_hausdorff, std::numeric_limits<unsigned short>::max());
  }

#if PRINT_TIMING
  clock_t t3 = clock();
  cout << "   Error computing takes " << (t3 - t2) / CLOCKS_PER_SEC << " seconds (in CPU time)." << endl;
#endif
}

/*
 ***********************************************
   Implementation of exposed functions and classes
 ***********************************************
 */

/**!
 * **************************************
 *  Class commandPar
 *
 *  Dong Tian <tian@merl.com>
 * **************************************
 */

commandPar::commandPar()
{
  file1 = "";
  file2 = "";
  normIn = "";
  singlePass = false;
  hausdorff = false;
  c2c_only = false;
  bColor = false;
  bLidar = false;

  resolution = 0.0;
  dropDuplicates = 0;
  neighborsProc = 0;
}

/**!
 * **************************************
 *  Class qMetric
 *
 *  Dong Tian <tian@merl.com>
 * **************************************
 */

qMetric::qMetric()
{
  c2c_acd = 0;
  c2c_hausdorff = 0;
  c2p_acd = 0;
  c2p_hausdorff = 0;

  color_mse[0] = color_mse[1] = color_mse[2] = 0.0;
  color_psnr[0] = color_psnr[1] = color_psnr[2] = 0.0;

  color_rgb_hausdorff[0] = color_rgb_hausdorff[1] = color_rgb_hausdorff[2] = 0.0;
  color_rgb_hausdorff_psnr[0] = color_rgb_hausdorff_psnr[1] = color_rgb_hausdorff_psnr[2] = 0.0;

  reflectance_hausdorff = 0.0;
  reflectance_hausdorff_psnr = 0.0;

  memset(y_hist, 0, sizeof(y_hist));
  hybrid_gc = 0;
}

/**!
 * **************************************
 *  Function computeQualityMetric
 *
 *  Dong Tian <tian@merl.com>
 * **************************************
 */

/**!
 * function to compute the symmetric quality metric: Point-to-Point and Point-to-Plane
 *   @param cloudA: point cloud, original version
 *   @param cloudNormalA: point cloud normals, original version
 *   @param cloudB: point cloud, decoded/reconstructed version
 *   @param cPar: input parameters
 *   @param qual_metric: quality metric, to be returned
 *
 * \author
 *   Dong Tian, MERL
 */
void pcc_quality::computeQualityMetric(PccPointCloud &cloudA, PccPointCloud &cloudNormalsA, PccPointCloud &cloudB, commandPar &cPar, qMetric &qual_metric)
{
  float pPSNR;

  if (cPar.resolution != 0.0)
  {
    cout << "Imported intrinsic resoluiton: " << cPar.resolution << endl;
    pPSNR = cPar.resolution;
  }
  else // Compute the peak value on the fly
  {
    double minDist;
    double maxDist;
    findNNdistances(cloudA, minDist, maxDist);
    pPSNR = float(maxDist);
    cout << "Minimum and maximum NN distances (intrinsic resolutions): " << minDist << ", " << maxDist << endl;
  }

  cout << "Peak distance for PSNR: " << pPSNR << endl;
  qual_metric.pPSNR = pPSNR;

  if (cPar.file2 != "")
  {
    // Check cloud size
    size_t orgSize = cloudA.size;
    size_t newSize = cloudB.size;
    float ratio = float(1.0) * newSize / orgSize;
    cout << "Point cloud sizes for org version, dec version, and the scaling ratio: " << orgSize << ", " << newSize << ", " << ratio << endl;
  }

  if (cPar.file2 == "") // If no file2 provided, return just after checking the NN
    return;

  // Based on normals on original point cloud, derive normals on reconstructed point cloud
  PccPointCloud cloudNormalsB;
  if (!cPar.c2c_only)
    scaleNormals(cloudNormalsA, cloudB, cloudNormalsB, cPar.bAverageNormals);
  cout << "Normals prepared." << endl;
  cout << endl;

  if (cPar.bColor && (!cloudA.bRgb || !cloudB.bRgb))
  {
    cout << "WARNING: no color properties in input files, disabling color metrics.\n";
    cPar.bColor = false;
  }

  if (cPar.bLidar && (!cloudA.bLidar || !cloudB.bLidar))
  {
    cout << "WARNING: no reflectance property in input files, disabling reflectance metrics.\n";
    cPar.bLidar = false;
  }

  if (cPar.bLidar && cPar.neighborsProc)
  {
    cout << "WARNING: reflectance metrics are computed without neighborsProc parameter.\n";
  }

  // Use "a" as reference
  cout << "1. Use infile1 (A) as reference, loop over A, use normals on B. (A->B).\n";
  qMetric metricA;
  metricA.pPSNR = pPSNR;
  findMetric(cloudA, cloudB, cPar, cloudNormalsB, metricA);

  cout << "   ACD1      (p2point): " << metricA.c2c_acd << endl;
  if (!cPar.c2c_only)
  {
    cout << "   ACD1      (p2plane): " << metricA.c2p_acd << endl;
  }
  if (cPar.hausdorff)
  {
    cout << "   h.       1(p2point): " << metricA.c2c_hausdorff << endl;
    if (!cPar.c2c_only)
    {
      cout << "   h.       1(p2plane): " << metricA.c2p_hausdorff << endl;
    }
  }
  if (cPar.bColor)
  {
    cout << "   c[0],    1         : " << metricA.color_mse[0] << endl;
    cout << "   c[1],    1         : " << metricA.color_mse[1] << endl;
    cout << "   c[2],    1         : " << metricA.color_mse[2] << endl;
    cout << "   c[0],PSNR1         : " << metricA.color_psnr[0] << endl;
    cout << "   c[1],PSNR1         : " << metricA.color_psnr[1] << endl;
    cout << "   c[2],PSNR1         : " << metricA.color_psnr[2] << endl;
    if (cPar.hausdorff)
    {
      cout << " h.c[0],    1         : " << metricA.color_rgb_hausdorff[0] << endl;
      cout << " h.c[1],    1         : " << metricA.color_rgb_hausdorff[1] << endl;
      cout << " h.c[2],    1         : " << metricA.color_rgb_hausdorff[2] << endl;
      cout << " h.c[0],PSNR1         : " << metricA.color_rgb_hausdorff_psnr[0] << endl;
      cout << " h.c[1],PSNR1         : " << metricA.color_rgb_hausdorff_psnr[1] << endl;
      cout << " h.c[2],PSNR1         : " << metricA.color_rgb_hausdorff_psnr[2] << endl;
    }
  }
  if (cPar.bLidar)
  {
    cout << "   r,       1         : " << metricA.reflectance_mse << endl;
    cout << "   r,PSNR   1         : " << metricA.reflectance_psnr << endl;
    if (cPar.hausdorff)
    {
      cout << " h.r,       1         : " << metricA.reflectance_hausdorff << endl;
      cout << " h.r,PSNR   1         : " << metricA.reflectance_hausdorff_psnr << endl;
    }
  }

  if (!cPar.singlePass)
  {
    // Use "b" as reference
    cout << "2. Use infile2 (B) as reference, loop over B, use normals on A. (B->A).\n";
    qMetric metricB;
    metricB.pPSNR = pPSNR;
    findMetric(cloudB, cloudA, cPar, cloudNormalsA, metricB);

    cout << "   ACD2      (p2point): " << metricB.c2c_acd << endl;
    if (!cPar.c2c_only)
    {
      cout << "   ACD2      (p2plane): " << metricB.c2p_acd << endl;
    }
    if (cPar.hausdorff)
    {
      cout << "   h.       2(p2point): " << metricB.c2c_hausdorff << endl;
      if (!cPar.c2c_only)
      {
        cout << "   h.       2(p2plane): " << metricB.c2p_hausdorff << endl;
      }
    }
    if (cPar.bColor)
    {
      cout << "   c[0],    2         : " << metricB.color_mse[0] << endl;
      cout << "   c[1],    2         : " << metricB.color_mse[1] << endl;
      cout << "   c[2],    2         : " << metricB.color_mse[2] << endl;
      cout << "   c[0],PSNR2         : " << metricB.color_psnr[0] << endl;
      cout << "   c[1],PSNR2         : " << metricB.color_psnr[1] << endl;
      cout << "   c[2],PSNR2         : " << metricB.color_psnr[2] << endl;
      if (cPar.hausdorff)
      {
        cout << " h.c[0],    2         : " << metricB.color_rgb_hausdorff[0] << endl;
        cout << " h.c[1],    2         : " << metricB.color_rgb_hausdorff[1] << endl;
        cout << " h.c[2],    2         : " << metricB.color_rgb_hausdorff[2] << endl;
        cout << " h.c[0],PSNR2         : " << metricB.color_rgb_hausdorff_psnr[0] << endl;
        cout << " h.c[1],PSNR2         : " << metricB.color_rgb_hausdorff_psnr[1] << endl;
        cout << " h.c[2],PSNR2         : " << metricB.color_rgb_hausdorff_psnr[2] << endl;
      }
    }
    if (cPar.bLidar)
    {
      cout << "   r,       2         : " << metricB.reflectance_mse << endl;
      cout << "   r,PSNR   2         : " << metricB.reflectance_psnr << endl;
      if (cPar.hausdorff)
      {
        cout << " h.r,       2         : " << metricB.reflectance_hausdorff << endl;
        cout << " h.r,PSNR   2         : " << metricB.reflectance_hausdorff_psnr << endl;
      }
    }

    // Derive the final symmetric metric
    qual_metric.c2c_cd = 0.5 * (metricA.c2c_acd + metricB.c2c_acd);
    qual_metric.c2p_cd = 0.5 * (metricA.c2p_acd + metricB.c2p_acd);
    qual_metric.c2c_cd_psnr = getPSNR(qual_metric.c2c_cd, qual_metric.pPSNR, 1.0);
    qual_metric.c2p_cd_psnr = getPSNR(qual_metric.c2p_cd, qual_metric.pPSNR, 1.0);

    qual_metric.c2c_hausdorff = max(metricA.c2c_hausdorff, metricB.c2c_hausdorff);
    qual_metric.c2p_hausdorff = max(metricA.c2p_hausdorff, metricB.c2p_hausdorff);
    qual_metric.c2c_hausdorff_psnr = getPSNR(qual_metric.c2c_hausdorff, qual_metric.pPSNR, 1.0);
    qual_metric.c2p_hausdorff_psnr = getPSNR(qual_metric.c2p_hausdorff, qual_metric.pPSNR, 1.0);

    if (cPar.bColor)
    {
      qual_metric.color_mse[0] = max(metricA.color_mse[0], metricB.color_mse[0]);
      qual_metric.color_mse[1] = max(metricA.color_mse[1], metricB.color_mse[1]);
      qual_metric.color_mse[2] = max(metricA.color_mse[2], metricB.color_mse[2]);

      qual_metric.color_psnr[0] = min(metricA.color_psnr[0], metricB.color_psnr[0]);
      qual_metric.color_psnr[1] = min(metricA.color_psnr[1], metricB.color_psnr[1]);
      qual_metric.color_psnr[2] = min(metricA.color_psnr[2], metricB.color_psnr[2]);

      qual_metric.color_rgb_hausdorff[0] = max(metricA.color_rgb_hausdorff[0], metricB.color_rgb_hausdorff[0]);
      qual_metric.color_rgb_hausdorff[1] = max(metricA.color_rgb_hausdorff[1], metricB.color_rgb_hausdorff[1]);
      qual_metric.color_rgb_hausdorff[2] = max(metricA.color_rgb_hausdorff[2], metricB.color_rgb_hausdorff[2]);

      qual_metric.color_rgb_hausdorff_psnr[0] = min(metricA.color_rgb_hausdorff_psnr[0], metricB.color_rgb_hausdorff_psnr[0]);
      qual_metric.color_rgb_hausdorff_psnr[1] = min(metricA.color_rgb_hausdorff_psnr[1], metricB.color_rgb_hausdorff_psnr[1]);
      qual_metric.color_rgb_hausdorff_psnr[2] = min(metricA.color_rgb_hausdorff_psnr[2], metricB.color_rgb_hausdorff_psnr[2]);

      if (!cPar.c2c_only)
      {
        // calculate Pablo's metric
        double accu_yhist = 0;
        for (int i = 0; i < 256; i++)
        {
          accu_yhist += pow(metricA.y_hist[i] - metricB.y_hist[i], 2);
        }
        qual_metric.hybrid_gc = cPar.hybrid_alpha * qual_metric.c2p_cd + (1 - cPar.hybrid_alpha) * sqrt(accu_yhist);
      }
    }
    if (cPar.bLidar)
    {
      qual_metric.reflectance_mse = max(metricA.reflectance_mse, metricB.reflectance_mse);
      qual_metric.reflectance_psnr = min(metricA.reflectance_psnr, metricB.reflectance_psnr);
      qual_metric.reflectance_hausdorff = max(metricA.reflectance_hausdorff, metricB.reflectance_hausdorff);
      qual_metric.reflectance_hausdorff_psnr = min(metricA.reflectance_hausdorff_psnr, metricB.reflectance_hausdorff_psnr);
    }

    cout << "3. Final (symmetric).\n";
    cout << "   CD        (p2point): " << qual_metric.c2c_cd << endl;
    cout << "   CD,PSNR   (p2point): " << qual_metric.c2c_cd_psnr << endl;
    if (!cPar.c2c_only)
    {
      cout << "   CD        (p2plane): " << qual_metric.c2p_cd << endl;
      cout << "   CD,PSNR   (p2plane): " << qual_metric.c2p_cd_psnr << endl;
    }
    if (cPar.hausdorff)
    {
      cout << "   h.        (p2point): " << qual_metric.c2c_hausdorff << endl;
      cout << "   h.,PSNR   (p2point): " << qual_metric.c2c_hausdorff_psnr << endl;
      if (!cPar.c2c_only)
      {
        cout << "   h.        (p2plane): " << qual_metric.c2p_hausdorff << endl;
        cout << "   h.,PSNR   (p2plane): " << qual_metric.c2p_hausdorff_psnr << endl;
      }
    }
    if (cPar.bColor)
    {
      cout << "   c[0],    F         : " << qual_metric.color_mse[0] << endl;
      cout << "   c[1],    F         : " << qual_metric.color_mse[1] << endl;
      cout << "   c[2],    F         : " << qual_metric.color_mse[2] << endl;
      cout << "   c[0],PSNRF         : " << qual_metric.color_psnr[0] << endl;
      cout << "   c[1],PSNRF         : " << qual_metric.color_psnr[1] << endl;
      cout << "   c[2],PSNRF         : " << qual_metric.color_psnr[2] << endl;
      if (cPar.hausdorff)
      {
        cout << " h.c[0],    F         : " << qual_metric.color_rgb_hausdorff[0] << endl;
        cout << " h.c[1],    F         : " << qual_metric.color_rgb_hausdorff[1] << endl;
        cout << " h.c[2],    F         : " << qual_metric.color_rgb_hausdorff[2] << endl;
        cout << " h.c[0],PSNRF         : " << qual_metric.color_rgb_hausdorff_psnr[0] << endl;
        cout << " h.c[1],PSNRF         : " << qual_metric.color_rgb_hausdorff_psnr[1] << endl;
        cout << " h.c[2],PSNRF         : " << qual_metric.color_rgb_hausdorff_psnr[2] << endl;
      }
      if (!cPar.c2c_only)
      {
        cout << "   hybrid geo-color   : " << qual_metric.hybrid_gc << endl;
      }
    }
    if (cPar.bLidar)
    {
      cout << "   r,       F         : " << qual_metric.reflectance_mse << endl;
      cout << "   r,PSNR   F         : " << qual_metric.reflectance_psnr << endl;
      if (cPar.hausdorff)
      {
        cout << " h.r,       F         : " << qual_metric.reflectance_hausdorff << endl;
        cout << " h.r,PSNR   F         : " << qual_metric.reflectance_hausdorff_psnr << endl;
      }
    }
  }
}

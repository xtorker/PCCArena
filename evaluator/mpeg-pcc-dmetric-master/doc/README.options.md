General options
---------------

The parsing options process have been updated to uniformize the PCC softwares and used: dependencies/program-options-lite. 
This library defined a parsing process different than the Boost library, previously used 

The command line options must be updated and:

  * the short options without parameters must be updated and now take an argument: ( "-c" => "-c 1")
  * the long options are required to use the "--option=value" form, rather than the previous "--option value" form.


The next table presents the software options.
 

\begin{longtable}{p{4cm}p{1cm}p{8cm}}
\hline
{\bf Parameter }  & {\bf Value} & {\bf Usage} \\ \hline
        --help=0           & 0   & This help text                                       \\ \hline
  -a,   --fileA=""         & ""  & Input file 1, original version                       \\ \hline
  -b,   --fileB=""         & ""  & Input file 2, processed version                      \\ \hline
  -n,   --inputNorm=""     & ""  & File name to import the normals of original point    \\ 
                           &     & cloud, if different from original file 1n            \\ \hline
  -s,   --singlePass=0     & 0   & Force running a single pass, where the loop is       \\ 
                           &     & over the original point cloud                        \\ \hline
  -d,   --hausdorff=0      & 0   & Send the Haursdorff metric as well                   \\ \hline
  -c,   --color=0          & 0   & Check color distortion as well                       \\ \hline
  -l,   --lidar=0          & 0   & Check lidar reflectance as well                      \\ \hline
  -r,   --resolution=0     & 0   & Specify the intrinsic resolution                     \\ \hline
        --dropdups=2       & 2   & 0(detect), 1(drop), 2(average) subsequent points     \\ 
                           &     & with same coordinates                                \\ \hline
        --neighborsProc=1  & 1   & 0(undefined), 1(average), 2(weighted average),       \\ 
                           &     & 3(min), 4(max) neighbors with same geometric         \\ 
                           &     & distance                                             \\ \hline
        --averageNormals=1 & 1   & 0(undefined), 1(average normal based on neighbors    \\ 
                           &     & with same geometric distance)                        \\ \hline
        --mseSpace=1       & 1   & colour space used for mse calculation                \\
                           &     & 0(identity), 1(Rec. ITU-R BT.709), 8(YCgCo-R)        \\ \hline
        --nbThreads=1      & 1   & Number of threads used for parallel processin        \\ \hline
\end{longtable}

 
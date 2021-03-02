Using the mpeg-pcc-dmetric
===============

Usage
---------------

```console
./test/pc_error  [--help] [-c config.cfg] [--parameter=value]
```

The metrics takes as input a PLY files: source(A), test(B) and soruce normal(N) 
and compute the distance between A and B accordring the normal stored in N. 

The outputs are writing in the terminal as trace and can be catch in log files. 

Examples
---------------

```console
./test/pc_error --help

./test/pc_error 
 --fileA=./queen/frame_0010.ply 
 --fileB=./S22C2AIR01_queen_dec_0010.ply 
 --inputNorm=./queen_n/frame_0010_n.ply 
 --color=1 
 --resolution=1023
 
``` 



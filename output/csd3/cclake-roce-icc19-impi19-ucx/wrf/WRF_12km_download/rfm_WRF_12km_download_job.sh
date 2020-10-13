#!/bin/bash
module load rhel7/default-ccl
export UCX_NET_DEVICES=mlx5_1:1
export WRF_DIR=$HOME/wrf-build-icc19-impi19-hsw/WRFV3.8.1
 echo Done.

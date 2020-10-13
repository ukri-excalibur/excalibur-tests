#!/bin/bash

_onerror()
{
    exitcode=$?
    echo "-reframe: command \`$BASH_COMMAND' failed (exit code: $exitcode)"
    exit $exitcode
}

trap _onerror ERR

module load rhel7/default-ccl
export UCX_NET_DEVICES=mlx5_1:1
mpicc mpi_nxnlatbw.c -o nxnlatbw

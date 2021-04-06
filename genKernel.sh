#!/bin/bash

BASEFOLDER="/home/graph_collection/independentset_instances"
# BASEFOLDER="instances"
KERNELFOLDER="/home/jholten/kernels"

for graph in `ls $BASEFOLDER/*.graph`; do
    GRAPHNAME=`basename $graph`
    GRAPHNAME=${GRAPHNAME%.*}
    # echo $GRAPHNAME
    echo "deploy/weighted_branch_reduce $BASEFOLDER/$graph --kernel=$KERNELFOLDER/$GRAPHNAME.kernel" 
done
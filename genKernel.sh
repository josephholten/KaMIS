#!/bin/bash

BASEFOLDER="/home/graph_collection/independentset_instances"
# BASEFOLDER="instances"
KERNELFOLDER="/home/jholten/kernels"

for graph in `find $BASEFOLDER -name '*.graph'`; do
    GRAPHNAME=`basename $graph`
    GRAPHNAME=${GRAPHNAME%.*}
    # echo $GRAPHNAME
    echo "deploy/weighted_branch_reduce $graph --weight_source=uniform --kernel=$KERNELFOLDER/$GRAPHNAME.uniform.kernel" 
done
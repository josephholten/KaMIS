#!/bin/bash

BASEFOLDER="/home/graph_collection/independentset_instances"
# BASEFOLDER="instances"
KERNELFOLDER="/home/jholten/kernels"

for graph in `find $BASEFOLDER -name '*.graph'`; do
    GRAPHNAME=`basename $graph`
    GRAPHNAME=${GRAPHNAME%.*}
    # echo $GRAPHNAME
    echo "deploy/weighted_branch_reduce $BASEFOLDER/$graph --weight_source=uniform --time_limit=3600.0 --kernel=$KERNELFOLDER/$GRAPHNAME.kernel" 
done
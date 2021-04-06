#!/bin/bash

BASEFOLDER="/home/graph_collection/independentset_instances"
# BASEFOLDER="instances"
MISFOLDER="/home/jholten/mis"

for graph in `find $BASEFOLDER -name '*.graph'`; do
    GRAPHNAME=`basename $graph`
    GRAPHNAME=${GRAPHNAME%.*}
    # echo $GRAPHNAME
    echo "deploy/weighted_branch_reduce $graph --weight_source=uniform --time_limit=3600.0 --output=$MISFOLDER/$GRAPHNAME.mis" 
done
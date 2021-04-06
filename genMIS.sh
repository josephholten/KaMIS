#!/bin/bash

BASEFOLDER="/home/graph_collection/independentset_instances"
# BASEFOLDER="instances"
MISFOLDER="/home/jholten/mis"

for graph in $BASEFOLDER/*.graph; do
    GRAPHNAME=`basename $graph`
    GRAPHNAME=${GRAPHNAME%.*}
    # echo $GRAPHNAME
    echo "deploy/weighted_branch_reduce $BASEFOLDER/$graph --output=$MISFOLDER/$GRAPHNAME.mis" 
done
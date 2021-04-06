#!/bin/bash

# BASEFOLDER = "/home/graph_collection/independentset_instances"
BASEFOLDER="instances"

for graph in `ls $BASEFOLDER/*.graph`; do
    GRAPHNAME=`basename $graph`
    GRAPHNAME=${GRAPHNAME%.*}}
    echo $GRAPHNAME
done
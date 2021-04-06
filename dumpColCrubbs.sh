#!/bin/bash

BASEFOLDER="/home/graph_collection/dynmatching"
for reps in 1; do
for eps in 1 0.5 0.1; do 
for g in `ls $BASEFOLDER/dyn_collection_prelim/*.graph`; do 
for seed in `seq 1 10`; do
                   GRAPHNAME=`echo $g | awk 'BEGIN {FS="/"} {print $6}'`
                   #echo $GRAPHNAME
                   #less randomwalks/$GRAPHNAME.seq.output.reps$reps.eps$eps.seed$seed | grep took | grep -v io | awk '{print $2}'
                   less crubbs/$GRAPHNAME.seq.unweightedDynBlossom.output.reps$reps.eps$eps.seed$seed | grep "matching size" | awk '{print $4}' >> crubbsResultBlossom.$reps.eps$eps
                   less crubbs/$GRAPHNAME.seq.unweightedRW.output.reps$reps.eps$eps.seed$seed | grep "matching size" | awk '{print $4}' >> crubbsResultRW.$reps.eps$eps
done
done
done
done

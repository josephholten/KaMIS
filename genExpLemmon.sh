#!/bin/bash

BASEFOLDER="/home/graph_collection/dynmatching"

for seed in `seq 1 10`; do
for g in `ls $BASEFOLDER/dyn_collection_prelim/*.graph`; do 
                   GRAPHNAME=`echo $g | awk 'BEGIN {FS="/"} {print $6}'`
                   #echo $GRAPHNAME
                   echo "../deploy/gmatchLemon --file $BASEFOLDER/dyn_collection_prelim_seed_$seed/$GRAPHNAME.seq.weighted.seq.graph > lemon/$GRAPHNAME.seq.output.seed$seed"
done
done
for seed in `seq 1 10`; do
for g in `ls $BASEFOLDER/final_real_dyn/*.graph`; do 
                   GRAPHNAME=`echo $g | awk 'BEGIN {FS="/"} {print $6}'`
                   #echo $GRAPHNAME
                   echo "../deploy/gmatchLemon --file $BASEFOLDER/final_real_dyn/$GRAPHNAME > lemon_finaldyn/$GRAPHNAME.seq.output.seed$seed"
done
done
for ud in 0.5 0.1 0.05 0.1; do 
for seed in `seq 1 10`; do
for g in `ls $BASEFOLDER/final_real_dyn_$ud/*.graph`; do 
                   GRAPHNAME=`echo $g | awk 'BEGIN {FS="/"} {print $6}'`
                   #echo $GRAPHNAME
                   echo "../deploy/gmatchLemon --file $BASEFOLDER/final_real_dyn_$ud/$GRAPHNAME > lemon_finaldyn/$GRAPHNAME.$ud.seq.output.seed$seed"
done
done
done

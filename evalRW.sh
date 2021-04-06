#!/bin/bash


echo "WALSHAW NETWORK"
for reps in 1 5 10 20; do
for eps in 1 0.1 0.01 0.001; do 
INST=`ls ~/projects/graph_collection/all_walschaw_graphs_rndweight/*.graph | wc -l`
TIME=`less ~/projects/graph_collection/all_walschaw_graphs_rndweight/*.seq.output.reps$reps.eps$eps | grep took | grep -v io | awk 'BEGIN {G=1} {G*=($2^(1/34))} END {printf "%f\n",G}'`
QUALITY=`less ~/projects/graph_collection/all_walschaw_graphs_rndweight/*.seq.output.reps$reps.eps$eps | grep matching | grep size | awk 'BEGIN {G=1} {G*=($4^(1/34))} END {printf "%d\n",G}'`
QUALITYOPT=`less ~/projects/graph_collection/all_walschaw_graphs_rndweight/*.glemon*| grep matching | sed 's/)//g' | awk 'BEGIN {G=1} {G*=($8^(1/34))} END {printf "%d\n",G}'`
TIMEOPT=`less ~/projects/graph_collection/all_walschaw_graphs_rndweight/*.glemon*| grep took | awk 'BEGIN {G=1} {G*=($2^(1/34))} END {printf "%f\n",G}'`
QUALITYRELOPT=`echo "scale=4;$QUALITY/$QUALITYOPT" | bc`
TIMERELOPT=`echo "scale=4;$TIME/$TIMEOPT" | bc`
echo -e "reps $reps eps $eps $QUALITY $TIME RELTOOPT $QUALITYRELOPT tRELOPT $TIMERELOPT OPT: $QUALITYOPT $TIMEOPT"
done
done
#echo "SOCIAL NETWORK"
#for reps in 1 5 10 20; do
#for eps in 1 0.1 0.01 0.001; do 
#INST=`ls ~/projects/graph_collection/snw_paper_rndweight/*.graph | wc -l`
#TIME=`less ~/projects/graph_collection/snw_paper_rndweight/*.seq.output.reps$reps.eps$eps | grep took | grep -v io | awk 'BEGIN {G=1} {G*=($2^(1/21))} END {printf "%f\n",G}'`
#QUALITY=`less ~/projects/graph_collection/snw_paper_rndweight/*.seq.output.reps$reps.eps$eps | grep matching | grep size | awk 'BEGIN {G=1} {G*=($4^(1/21))} END {printf "%d\n",G}'`
#QUALITYOPT=`less ~/projects/graph_collection/snw_paper_rndweight/*.glemon*| grep matching | sed 's/)//g' | awk 'BEGIN {G=1} {G*=($8^(1/21))} END {printf "%d\n",G}'`
#TIMEOPT=`less ~/projects/graph_collection/snw_paper_rndweight/*.glemon*| grep took | awk 'BEGIN {G=1} {G*=($2^(1/21))} END {printf "%f\n",G}'`
#QUALITYRELOPT=`echo "scale=4;$QUALITY/$QUALITYOPT" | bc`
#TIMERELOPT=`echo "scale=4;$TIME/$TIMEOPT" | bc`
#echo -e "reps $reps eps $eps $QUALITY $TIME RELTOOPT $QUALITYRELOPT tRELOPT $TIMERELOPT OPT: $QUALITYOPT $TIMEOPT"
#done
#done

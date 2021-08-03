#!/bin/bash

for graph in /home/jholten/test_graphs/*.graph; do
    name=$(basename $graph)
    n=$(awk 'NR==1{print $1; exit}'  $graph)
    m=$(awk 'NR==1{print $2}'  $graph)
    kernel=$(awk 'NR==3{print $1; exit}' /home/jholten/perf_test/$name.kernel)
    kamis=$(echo "scale=3; $kernel / $n" | bc -l)
    ml_ker=$(awk 'NR==3{print $1; exit}' /home/jholten/perf_test/$name.kernel.ml_kernel95.kernel)
    ml=$(echo "scale=3; $ml_ker / $n" | bc -l)
    opt_sol=$(cat /home/jholten/perf_test/$name.mis | paste -sd+ | bc -l)
    
    if [ -s /home/jholten/perf_test/$name.kernel.ml_kernel95.kernel.mis ]; then
        ml_sol="0"
    else
        ml_sol=$(cat /home/jholten/perf_test/$name.kernel.ml_kernel95.kernel.mis | paste -sd+ | bc -l)
    fi
    offset=$(expr $(awk 'NR==2{print $2; exit}' /home/jholten/perf_test/$name.kernel) + $(awk 'NR==2{print $2; exit}' /home/jholten/perf_test/$name.kernel.ml_kernel95.kernel))
    ml_sol=$(expr $ml_sol + $offset)

    qual=$(echo "scale=3; $ml_sol / $opt_sol" | bc -l)

    echo "${name%%.*} & $n & $m & $kamis & $ml & $qual"
done


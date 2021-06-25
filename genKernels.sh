#!/bin/bash
for graph_path in $(find /home/graph_collection/independentset_instances/ -name '*sorted.graph'); do
	echo "deploy/weighted_branch_reduce $graph_path --kernel=/home/jholten/kernels/$(basename -- $graph_path).kernel"
done

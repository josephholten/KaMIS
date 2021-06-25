for graph in $(find /home/graph_collection/independentset_instances -type f -name '*.graph'); do
	echo "deploy/features $graph /home/jholten/graph_files 10"
done

for graph in $(find $1 -maxdepth 1 -type f); do
	echo "deploy/features $graph /home/jholten/graph_files 10"
done

for graph in `find $1 -maxdepth 1 -type f -name '*97'`; do
	echo "deploy/weighted_branch_reduce $graph --out=/home/jholten/mis/ml_reduce_results/${graph##*/}.mis"
done


for graph in `find $1 -type f -maxdepth 1`; do
	echo "deploy/weighted_branch_reduce $graph --out=/home/jholten/mis/kamis_results/${graph##*/}.mis"
done


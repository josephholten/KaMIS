for graph in `find /home/jholten/kernels/ml_reduce_kernels/ -type f -maxdepth 1`; do
	echo "deploy/weighted_branch_reduce $graph --out=/home/jholten/mis/ml_reduce_results/${graph##*/}.mis"
done


for graph in `find $1 -maxdepth 1 -type f -name "$graph*"`; do
	for q in {5..9}; do
		echo "deploy/weighted_branch_reduce /home/jholten/kernels/ml_reduce_kernels/$(basename $graph).ml_kernel9$q --out=/home/jholten/mis/ml_reduce_results/${graph##*/}.mis"
	done
done


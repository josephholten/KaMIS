KERNELS=/home/jholten/kernels
for graph in $(find /home/jholten/test_graphs/ -type f); do
	graph_basename=$(basename $graph)
	graph_name=${graph_basename%%.*}

	read -r n m < <(awk 'NR==1{print $1,$2}' $graph)

	size_frac=$(awk -v n="$n" -v ml=$(awk 'NR==1{print $1; exit}' $KERNELS/ml_reduce_kernels/$graph_basename.ml_kernel95) 'BEGIN{printf "%.3f", ml/n}')

	kernel_frac=$(awk -v ker=$(awk 'NR==2{print $1; exit}' $KERNELS/kamis_kernels/$graph_basename.kernel) -v ml_rem_ker=$(awk 'NR==2{print $1; exit}' $KERNELS/ml_reduce_kernels/$graph_basename.ml_kernel95.kernel) 'BEGIN{printf "%.3f", ml_rem_ker/ker}')

	quality=$(awk -v og=$(cat /home/jholten/mis/kamis_results/$graph_basename.mis | paste -sd+ | bc) \
		      -v ml=$(cat /home/jholten/mis/ml_reduce_results/$graph_basename.ml_kernel95.mis | paste -sd+ | bc) \
		      -v offset=$(awk 'NR==1{print $3; exit}' $KERNELS/ml_reduce_kernels/$graph_basename.ml_offset95) 'BEGIN{printf "%.3f", (ml)/og}')

	echo "$graph_name & $n & $m & $size_frac & $kernel_frac & $quality \\\\"
done

for test_file in `find /home/jholten/test_graphs -type f`; do
	# for q in {5..9}; do
	q=7
	echo "python3 preprocessing/ml_reduce_c.py $test_file 0.9$q"
	# done
done


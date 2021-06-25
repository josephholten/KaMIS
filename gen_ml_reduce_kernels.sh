for test_file in `cat test_graphs.txt`; do
	for q in {5..9}; do
		name=${test_file##*/}
		echo "python3 preprocessing/ml_reduce_c.py $test_file 0.9$q"
	done
done


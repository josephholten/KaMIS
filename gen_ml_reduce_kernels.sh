for test_file in `find /home/jholten/test_graphs -type f`; do
	echo "python3 preprocessing/ml_reduce_c.py $test_file $1"
done


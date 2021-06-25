cat graphs_missing_mis | while read line; do
	echo "deploy/weighted_branch_reduce $line --out=/home/jholten/mis/kamis_results/${line##*/}.mis"
done


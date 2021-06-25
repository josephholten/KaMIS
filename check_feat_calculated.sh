for file in `find /home/jholten/graph_files -type f`; do
	echo "${file%.feat}"
	if [[ -f /home/jholten/graphs/${file%.feat} ]]; then
		echo "" > /dev/null
	fi
done

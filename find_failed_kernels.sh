#!/usr/bin/bash
for file in /home/jholten/kernels/kamis_kernels/*; do
	basename=${file##*/}
	if [[ $(find /home/jholten/graph_files/* -name "$(echo "$basename" | cut -f 1 -d '.')*") ]]; then
		echo "" > /dev/null
	else
		echo -n "$basename "
	fi
done
echo ""


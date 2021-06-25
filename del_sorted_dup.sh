for file in `find $1 -type f`; do 
	if [[ $file == *"-sorted"* ]]; then
		if [[ -f "${file//-sorted/}" ]]; then
			rm -rf "${file//-sorted/}"
		fi
	fi
done

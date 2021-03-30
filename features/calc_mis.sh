if [ ! -f "$2" ]; then          # "$1" is graph_path, "$2" is graph_mis_path 
    echo "calculating MIS for $1 ..."
    deploy/weighted_branch_reduce "$1" --output="$2" --weight_source=uniform
else
    echo "MIS already calculated for" "$1"
fi
echo -n "" > instances/graph_correctness.txt
for graph in instances/*.graph; do 
    echo -n "$graph " >> instances/graph_correctness.txt 
    deploy/graphchecker "$graph" > instances/check_status.txt 
    if grep -q "The graph format seems correct." instances/check_status.txt; then
        echo "1" >> instances/graph_correctness.txt
        echo "$graph correct"
    else 
        echo "$graph incorrect"

        echo "sorting $graph ..."
        deploy/sort_adjacencies "$graph" > "sorted.graph"
        rm "$graph"
        mv "sorted.graph" "$graph"

        if deploy/graphchecker "$graph" | grep -q "The graph format seems correct." ; then
            echo "now format is correct"
            echo "1" >> instances/graph_correctness.txt
        else
            echo "$graph still incorrect format!!!"
            cat instances/check_status.txt
            echo "0" >> instances/graph_correctness.txt
        fi
    fi
done
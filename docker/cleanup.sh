#!/bin/bash

CLUSTER=("./config/192.168.1.21/" "./config/192.168.1.31/" "./config/192.168.1.102/" "./config/192.168.1.242/")
# DELETE=("tree_graph_node")

for dir in ${CLUSTER[*]}
do
    real_path=`realpath $dir`
	found=$(ls $dir);
    for f in ${found[*]}
    do
        case $f in
        "tree_graph_node")
            rm -rf  $dir$f
            if [ $? -eq 0 ]; then
                echo "delete $real_path/$f success!";
            fi
            ;;  # equals break
        # "bin")
        #     rm -rf  $dir$f/*
        #     if [ $? -eq 0 ]; then
        #         echo "delete $real_path/$f/* success!";
        #     fi
        #     ;;
        esac
    done
done


# function main() {
#     read_dir $root_dir
# }

# main $#


#!/bin/bash
set -e

while :
    do
        git clone https://github.com/CGair23/ufs.git /ufs
        if ($?) then 
            break
        fi
    done

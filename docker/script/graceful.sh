#!/bin/bash
set -e

trap 'echo "Goodbye, Init"; kill -TERM $PID1' TERM INT

/file_server.sh &
PID1=$!     # $!表示上个子进程的进程号
wait $PID1 

EXIT_STATUS=$?

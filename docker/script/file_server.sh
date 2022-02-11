#!/bin/bash
set -e
trap 'echo "Goodbye, File server"; kill $PID'  INT TERM

echo "File server running"

# Start the file server
nohup ufs start > /ufs/logs/ufs.log 2>&1 &
PID=$!

wait $PID

#!/bin/bash
set -e

# Start the file server
nohup ufs start > /ufs/logs/ufs.log 2>&1 &
ps aux |grep ufs |grep -q -v grep
PROCESS_STATUS=$?
if [ $PROCESS_STATUS -ne 0 ]; then
    echo "Failed to start file server process: $PROCESS_STATUS"
    exit $PROCESS_STATUS
fi
# Check if a process is running every 60 seconds
while sleep 60; do
    ps aux |grep ufs |grep -q -v grep
    PROCESS_STATUS=$?
# If the greps above find anything, they exit with 0 status
# If they are not both 0, then something is wrong
if [ $PROCESS_STATUS -ne 0 ]; then
    echo "The file server processes has already exited."
    exit 1
fi

# just keep this script running
# while [[ true ]]; do
#     sleep 1
# done
# 缺点是不能拉起 crash 的进程,也就是只能拉起运行不能”守护”
# 不关心进程 crash 问题可以用这种方式

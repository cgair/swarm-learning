FROM ubuntu:18.04

RUN apt-get update && apt-get install -q -y \
    net-tools \
    iputils-ping \
    vim \
    tree

RUN mkdir -p /tree-graph

# ADD ./bin/conflux_production /tree-graph  # if we mount a volume, we just ensure the executable is in the mounted directory.
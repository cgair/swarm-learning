# ============================================================================
#
# THIS IS A GENERATED DOCKERFILE.
#
# This file was assembled from multiple pieces, whose use is documented
# throughout. Please refer to the TensorFlow dockerfiles documentation
# for more information.
ARG UBUNTU_VERSION=18.04
FROM ubuntu:${UBUNTU_VERSION} AS base

# You use this mode when you need zero interaction while installing or upgrading the system via apt. 
# It accepts the default answer for all questions. It might mail an error message to the root user, but that’s it all. 
# Otherwise, it is totally silent and humble, a perfect frontend for automatic installs. 
# One can use such mode in Dockerfile, shell scripts, cloud-init script, and more.
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y curl \
    wget \
    # iputils-ping
    python3 \
    python3-pip \
    python3-tk 

# RUN apt-get clean

# Downloading the dumb-init binary directly
# RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_x86_64
# RUN chmod +x /usr/local/bin/dumb-init

# run script
# RUN mkdir -p /script/
# COPY script/file_server.sh /script/
# RUN chmod +x /script/file_server.sh

# ENV UFS_LOG=debug
# RUN mkdir -p /ufs/SMLNODE/fs
# RUN mkdir -p /ufs/config
# ADD default.toml /ufs/config/
# ADD bin/ufs /usr/sbin/
# RUN mkdir -p /ufs/logs

# See http://bugs.python.org/issue19846
ENV LANG C.UTF-8

# RUN python3 -m pip --no-cache-dir install --upgrade \
#     "pip<20.3" \
#     setuptools
RUN python3 -m pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Some TF tools expect a "python" binary
RUN ln -s $(which python3) /usr/local/bin/python

# Options:
#   tensorflow
#   tensorflow-gpu
#   tf-nightly
#   tf-nightly-gpu
# Set --build-arg TF_PACKAGE_VERSION=1.11.0rc0 to install a specific version.
# Installs the latest version by default.
ARG TF_PACKAGE=tensorflow
ARG TF_PACKAGE_VERSION=

# change pip source
RUN python3 -m pip install --no-cache-dir --index-url https://pypi.doubanio.com/simple/ ${TF_PACKAGE}${TF_PACKAGE_VERSION:+==${TF_PACKAGE_VERSION}}
COPY bashrc /etc/bash.bashrc
RUN chmod a+rwx /etc/bash.bashrc

RUN mkdir -p /sdk/python
RUN mkdir -p /sdk/rust/coder
RUN mkdir -p /tools/port-ethabi
RUN mkdir -p /third_party/ethabi
# If the source of the COPY/ADD command is a folder, the contents of the folder are copied instead of itself
COPY python-sdk/ /sdk/python
COPY rust-sdk/coder/ /sdk/rust/coder
COPY port-ethabi/ /tools/port-ethabi
COPY ethabi/ /third_party/ethabi

# Get Rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustup update

WORKDIR /sdk/python
RUN python3 -m pip install --upgrade pip
RUN python3 setup.py install

WORKDIR /sdk/rust/coder
RUN python3 setup.py install

RUN mkdir -p /swarm
WORKDIR /swarm
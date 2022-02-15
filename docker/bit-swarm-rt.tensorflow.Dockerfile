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
    python3 \
    python3-pip 

# Downloading the dumb-init binary directly
# RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_x86_64
# RUN chmod +x /usr/local/bin/dumb-init

# rust env
# ENV PATH="/root/.cargo/bin:${PATH}"
# install rust
#     build-essential \
#     git 
# RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
# RUN rustup update

# run script
RUN mkdir -p /script/
COPY script/file_server.sh /script/
RUN chmod +x /script/file_server.sh

ENV UFS_LOG=debug
RUN mkdir -p /ufs/SMLNODE/fs
RUN mkdir -p /ufs/config
ADD default.toml /ufs/config/
ADD ufs /usr/sbin/
RUN mkdir -p /ufs/logs

# See http://bugs.python.org/issue19846
ENV LANG C.UTF-8

RUN python3 -m pip --no-cache-dir install --upgrade \
    "pip<20.3" \
    setuptools

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

RUN mkdir -p /swarm
WORKDIR /swarm

# ENTRYPOINT ["/usr/local/bin/dumb-init", "--", "/file_server.sh"]
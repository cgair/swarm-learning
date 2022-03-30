#!/usr/bin/env python3
# Copyright 2019-2020 Conflux Foundation. All rights reserved.
# TreeGraph is free software and distributed under Apache License 2.0.
# See https://www.apache.org/licenses/LICENSE-2.0
import socket

def get_ip_address():
    return [int(i) for i in socket.gethostbyname(socket.gethostname()).split('.')]


def get_peer_addr(connection):
    return "{}:{}".format(connection.ip, connection.port)

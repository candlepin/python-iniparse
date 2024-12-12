#!/bin/bash

source /etc/os-release
# This repository is required for python3-pytest and python3-test
# on Centos Stream
if [[ $ID == "centos" ]]; then
  dnf config-manager --enable crb
fi

dnf install -y python3-setuptools python3-pip python3-devel python3-pytest python3-test

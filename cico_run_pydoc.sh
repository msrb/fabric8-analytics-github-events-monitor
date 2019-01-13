#!/bin/bash

set -ex

prep() {
    yum -y update
    yum -y install epel-release https://centos7.iuscommunity.org/ius-release.rpm
    yum -y install python36u which
}

prep
./check-docstyle.sh

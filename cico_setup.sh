#!/bin/bash -ex

here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

prep() {
    yum -y update
    yum -y install epel-release https://centos7.iuscommunity.org/ius-release.rpm
    yum -y install git gcc python36u python36u-devel python36u-pip which
}

prep

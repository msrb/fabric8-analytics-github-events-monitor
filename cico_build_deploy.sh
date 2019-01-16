#!/bin/bash

set -ex

. cico_setup.sh

./run-tests.sh

build_image

push_image

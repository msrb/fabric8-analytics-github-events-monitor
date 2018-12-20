#!/bin/bash

set -ex

here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

#TODO: . ${here}/cico_setup.sh

${here}/run-tests.sh


#!/bin/bash

set -e

pytest models.py monitor.py gopkg/translate.py

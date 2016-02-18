#!/usr/bin/env bash

# Set ${STACK_AFW} to the path of the built/installed afw package
# e.g. /lsstsw/stack/Linux64/afw/2015_10.0-14-g7c5ed66

ltd-mason --manifest manifest.yaml \
    --build-dir ../../ltd_mason_test \
    --config config.yaml

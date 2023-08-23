#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/../env.sh
RANGER_VERSION=2.3.0

if [ ! -d "$SCRIPT_DIR/ranger-${RANGER_VERSION}-trino-plugin" ]
then
    curl https://github.com/aakashnand/trino-ranger-demo/releases/download/trino-ranger-demo-v1.0/ranger-${RANGER_VERSION}-trino-plugin.tar.gz --output $SCRIPT_DIR/ranger-${RANGER_VERSION}-trino-plugin.tar.gz -L
    (cd $SCRIPT_DIR && tar xf ranger-${RANGER_VERSION}-trino-plugin.tar.gz &&
    yes | cp -rf trino-ranger-install.properties ranger-${RANGER_VERSION}-trino-plugin/install.properties)
fi

if [ ! -d "$SCRIPT_DIR/plugins" ]; then
    (cd $SCRIPT_DIR/../.. && make trino-plugins)
fi

TAG=trino-ranger

docker build . -t $REPO_NAME/$TAG

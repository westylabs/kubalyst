#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/../env.sh

RANGER_VERSION=3.0.0-SNAPSHOT
RANGER_TAR=ranger-${RANGER_VERSION}-trino-plugin-405-406.tar.gz

if [ ! -d "$SCRIPT_DIR/ranger-${RANGER_VERSION}-trino-plugin" ]
then
    curl https://github.com/aakashnand/trino-ranger-demo/releases/download/trino-ranger-demo-v1.0/$RANGER_TAR \
      --output $SCRIPT_DIR/ranger-${RANGER_VERSION}-trino-plugin.tar.gz -L && \
    (cd $SCRIPT_DIR && tar xf ranger-${RANGER_VERSION}-trino-plugin.tar.gz)
fi

(cd $SCRIPT_DIR && \
yes | cp -rf trino-ranger-install.properties ranger-${RANGER_VERSION}-trino-plugin/install.properties)

if [ ! -d "$SCRIPT_DIR/plugins" ]; then
    (cd $SCRIPT_DIR/../.. && make trino-plugins)
fi

TAG=trino-ranger

docker build . -t $REPO_NAME/$TAG

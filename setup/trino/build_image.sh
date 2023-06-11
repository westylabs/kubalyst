#!/bin/bash

set -e

RANGER_VERSION=2.3.0

if [ ! -d "ranger-${RANGER_VERSION}-trino-plugin" ]
then
    curl https://github.com/aakashnand/trino-ranger-demo/releases/download/trino-ranger-demo-v1.0/ranger-${RANGER_VERSION}-trino-plugin.tar.gz --output ranger-${RANGER_VERSION}-trino-plugin.tar.gz -L
    tar xvf ranger-${RANGER_VERSION}-trino-plugin.tar.gz
    yes | cp -rf trino-ranger-install.properties ranger-${RANGER_VERSION}-trino-plugin/install.properties
fi

REPONAME=gfee
TAG=trino-ranger

docker build . -t $REPONAME/$TAG

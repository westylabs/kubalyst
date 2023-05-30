#!/bin/bash

set -e

REPONAME=gfee
TAG=hive-metastore

docker build . -t $REPONAME/$TAG


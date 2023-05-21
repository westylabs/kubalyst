#!/bin/bash

set -e

REPONAME=gfee
TAG=ranger-admin

docker build . -t $REPONAME/$TAG


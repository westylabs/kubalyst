# kubalyst

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![](https://github.com/westylabs/kubalyst/actions/workflows/python-package.yml/badge.svg)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

**Status: not stable, under development, contributions welcome**

Simplify the creation, deployment, monitoring and management of data infrastructure architectural
patterns. Leverages the [cdk8](https://cdk8s.io) library to generate kubernetes yaml files and a local k8s environment
with a stack that contains the following:

* Trino
* Hive Metastore backed by Mariadb
* Minio (local S3)
* Apache Ranger backed by Elasticsearch and Mariadb
* SQLPad

## Local Environment Setup

Ensure you have Python 3.9 installed, and then:

```shell
make venv
. ./venv/bin/activate
```

Then follow the steps in [GETTING_STARTED.txt](GETTING_STARTED.txt).

## Starting Services

Start running the commands in `setup/start_services.sh` one by one. This will:

* Build docker images
* Generate k8s yaml
* Start minikube
* Run yaml services
* Execute integration tests

TODO: break this into executable scripts

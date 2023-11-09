# kubalyst

**Status: not stable, under development**

Simplify the creation, deployment, monitoring and management of data infrastructure architectural patterns. Generates kubernetes yaml files and a local k8s environment with a stack that contains the following:

* Trino
* Hive Metastore backed by Mariadb
* Minio (local S3)
* Apache Ranger backed by Elastic Search and Mariadb
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

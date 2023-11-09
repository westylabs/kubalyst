# build images
eval $(minikube -p minikube docker-env)
(cd hive-metastore && ./build_image.sh)
(cd trino && ./build_image.sh)
(cd ranger-admin && ./build_image.sh)

# Set paths in yaml files to point to the current users project root
./fix-k8s-paths.py *.yaml

### Start k8s mini cluster
# on a laptop memory and cpu might need to be reduced. if you don't have enough resources, increase
# them in the Docker Desktop settings
minikube start --memory 22000 --cpus 8 --disk-size 80g --driver docker

### Minio Setup
# create bucket
kubectl apply -f ./minio_dev.yaml

### Metastore setup
# maria for the db
kubectl apply -f ./maria_deployment.yaml

# build image
kubectl apply -f ./metastore.yaml

### Ranger setup - must start maria first
kubectl apply -f ./es_deployment.yaml
kubectl apply -f ./ranger_admin.yaml

### Trino setup
cd .. && make k8s-config-gen
kubectl apply -f ../k8s/dist/trino-cfgs.k8s.yaml
kubectl apply -f ../k8s/dist/trino.k8s.yaml


# Sqlpad
#kubectl apply -f ./sqlpad.yaml

# Setup port forwards in a different terminal
. venv/bin/activate
query-cli setup-port-forwards
# (leave this running and open a new terminal)

# SETUP COMPLETE

# Validate your setup
# TODO: refactor integration tests to not use the snowflake connector but to validate trino
# and others directly. The tests in query_cli/tests/integration as written will not pass
. venv/bin/activate
python -m pytest query_cli/tests/integration


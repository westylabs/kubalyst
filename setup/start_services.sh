minikube start --memory 16000 --cpus 8 --disk-size 80g --driver docker

# build images
eval $(minikube -p minikube docker-env)
cd hive-metastore-docker && ./build_image.sh && cd ..
cd trino && ./build_image.sh && cd ..

### Minio Setup
kubectl apply -f ./minio_dev.yaml
# create bucket

### Metastore setup
# maria for the db
kubectl apply -f ./maria_deployment.yaml

# build image
kubectl apply -f ./metastore.yaml

### Ranger setup - must start maria first
kubectl apply -f ./es_deployment.yaml
kubeclt apply -f ./ranger_admin.yaml

### Trino setup
kubectl apply -f ./trino-ranger-cfgs.yaml
kubectl apply -f ./trino-ranger.yaml

# Setup port forwards in a different terminal
cd query_cli
. venv/bin/activate
./query_cli setup-port-forwards

# Setup hive bucket
aws s3api create-bucket --bucket hive --endpoint-url http://localhost:9000

# Setup roles and users
cd query_cli
. venv/bin/activate
./query_cli create-default-users -o org123
./query_cli create-default-roles -o org123

# TODO: run all the non-kube services

# SETUP COMPLETE

# Validate setup

./query_cli 

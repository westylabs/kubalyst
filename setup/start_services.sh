minikube start --memory 16000 --cpus 8 --disk-size 80g --driver docker

# build images
eval $(minikube -p minikube docker-env)
cd hive-metastore-docker && ./build_image.sh && cd ..
cd trino && ./build_image.sh && cd ..
cd trino-ranger-demo/ranger-admin && ./build_image.sh && cd ../..
cd ../sqlpad/ && ./build_image.sh && cd ../setup

# Set paths in yaml files to point to the current project root.
# Otherwise they'll point to `/Users/gfee/code/collosus`
./fix-k8s-paths.py *.yaml

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
kubectl apply -f ./ranger_admin.yaml

### Trino setup
kubectl apply -f ./trino-ranger-cfgs.yaml
kubectl apply -f ./trino-ranger.yaml

# Redis setup
kubectl apply -f ./redis.yaml

# Sqlpad
kubectl apply -f ./sqlpad.yaml

# Setup port forwards in a different terminal
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
pip install -e .
query-cli setup-port-forwards
# (leave this running and open a new terminal)

# These commands need to run from repo root
make create-orddata-db
make deploy-orgdata-schema-updates
make create-query-db
make deploy-query-schema-updates

# Setup hive bucket
aws s3api create-bucket --bucket hive --endpoint-url http://localhost:9000

# Run all the non-kube services
# Orgdata service
# (new terminal)
. venv/bin/activate
orgdata

# taskman service
# (new terminal)
. venv/bin/activate
taskman
# (new terminal)
. venv/bin/activate
taskman-worker

# query service
# (new terminal)
. venv/bin/activate
query

# web ui
. venv/bin/activate
session

# web ui
. venv/bin/activate
webui

# Setup roles and users
# (new terminal)
. venv/bin/activate
query-cli create-default-users -o org123
query-cli create-default-roles -o org123

# SETUP COMPLETE

# Validate your setup
. venv/bin/activate
python -m pytest query_cli/tests/integration

http://localhost:7786/login
# Follow the instructions to create an org

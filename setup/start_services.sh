minikube start --memory 16000 --cpus 8 --disk-size 80g --driver docker

# build images
eval $(minikube -p minikube docker-env)
cd hive-metastore-docker && ./build_image.sh && cd ..
cd trino && ./build_image.sh && cd ..
cd trino-ranger-demo/ranger-admin && ./build_image.sh && cd ../..

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

# Setup port forwards in a different terminal
cd ../query_cli
virtualenv venv
. venv/bin/activate
pip install -r requirements3.txt
./query_cli setup-port-forwards
# (leave this running and open a new terminal)

# Setup hive bucket
aws s3api create-bucket --bucket hive --endpoint-url http://localhost:9000

# Run all the non-kube services
# Orgdata service 
# (new terminal)
cd ../orgdata
virtualenv venv
. venv/bin/activate
pip install -r requirements3.txt
python main.py

# taskman service
# (new terminal)
cd ../taskman
virtualenv venv
. venv/bin/activate
pip install -r requirements3.txt
python main.py
# (new terminal)
. venv/bin/activate
rq worker --with-schedule

# query service
# (new terminal)
cd ../query
virtualenv venv
. venv/bin/activate
pip install -r requirements3.txt
python main.py

# Setup roles and users
# (new terminal)
cd ../query_cli
. venv/bin/activate
./query_cli create-default-users -o org123
./query_cli create-default-roles -o org123

# SETUP COMPLETE

- Install precommit
  - Ubuntu
    ```bash
    sudo apt install pre-commit
    pre-commit install
    ```
  - OSX
    ```bash
    brew install pre-commit
    pre-commit install
    ```
- Setup docker
  - Ubuntu
    ```bash
    sudo apt-get install docker
    ```
  - OSX
    ```bash
    brew install docker
    ```
- Setup kubernetes
  - Ubuntu
    ```bash
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    sudo install minikube-linux-amd64 /usr/local/bin/minikube
    sudo apt-get install -y kubectl
    ```
  - OSX
    - Enable Kubernetes on Docker desktop
    ```bash
    brew install minikube
    ```
- Install python 3.9.5
- Install mysql client
  - Ubuntu
    ```bash
    sudo apt-get install mysql-client
    ```
  - OSX
    ```bash
    brew install mysql
    ```
- Install aws-cli
  - Ubuntu
    ```bash
    sudo snap install awscli
    ```
  - OSX
    ```bash
    brew install awscli
    ```
- Install cdk8s
    - Ubuntu
      ```bash
      sudo snap install cdk8s
      ```
    - OSX
      ```bash
      brew install cdk8s
      ```
- Configure aws-cli credentials
  - Create the file `~/.aws/credentials` and make its contents:
    ```
    [default]
    aws_access_key_id = minio_root_user
    aws_secret_access_key = minio_root_password123
    ```
- Start running the commands in `setup/start_services.sh` one by one

kubectl delete -f ./sqlpad.yaml
kubectl apply -f ./sqlpad.yaml
sleep 1
query-cli setup-port-forwards

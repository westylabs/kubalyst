#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <pod_namee>"
  echo "Opens a shell on a running k8s pod"
  exit -1
fi

POD=$1
kubectl exec --stdin --tty $POD -- /bin/bash

from typing import Dict, Any, List, Optional
import subprocess
import json



def _find(kubectl_output: Dict[str, Any], label: str) -> Optional[str]:
    found_items = [
        item["metadata"]["name"]
        for item in kubectl_output["items"]
        if item["metadata"]["labels"].get("app") == label
    ] 
    if len(found_items) == 0:
        return None
    if len(found_items) != 1:
        raise ValueError("Found wrong number of pods = {}".format(",".join(found_items)))
    return found_items[0]


def _run_port_forward(pod_name: Optional[str], target_port: int) -> Any:
    if pod_name is None:
        return None
    return subprocess.Popen(["kubectl", "port-forward", pod_name, "{}:{}".format(target_port, target_port)])


def create_forwards() -> List[Any]:
    kubectl_output = subprocess.check_output(["kubectl", "get", "po", "-A", "-o=json"])

    kubectl_output_parsed = json.loads(kubectl_output)

    trino_coordinator_pod_name = _find(kubectl_output_parsed, "trino-coordinator")
    ranger_admin_pod_name = _find(kubectl_output_parsed, "ranger-admin")    
    maria_pod_name = _find(kubectl_output_parsed, "mariadb")
    minio_pod_name = _find(kubectl_output_parsed, "minio")
    redis_pod_name = _find(kubectl_output_parsed, "redis")

    trino_process = _run_port_forward(trino_coordinator_pod_name, 8080)
    ranger_process = _run_port_forward(ranger_admin_pod_name, 6080)
    maria_process = _run_port_forward(maria_pod_name, 3306)
    minio_process = _run_port_forward(minio_pod_name, 9000)
    redis_process = _run_port_forward(redis_pod_name, 6379)

    return list(filter(None, [trino_process, ranger_process, maria_process, minio_process, redis_process]))

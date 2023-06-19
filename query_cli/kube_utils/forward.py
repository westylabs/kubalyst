import json
import subprocess
import time
from threading import Lock
from threading import Thread
from typing import Any
from typing import List
from typing import Optional


def _find_pod_name(pod_name: str) -> Optional[str]:
    kubectl_output = subprocess.check_output(["kubectl", "get", "po", "-A", "-o=json"])
    kubectl_output_parsed = json.loads(kubectl_output)
    found_items = [
        item["metadata"]["name"]
        for item in kubectl_output_parsed["items"]
        if item["metadata"]["labels"].get("app") == pod_name
    ]
    if len(found_items) == 0:
        return None
    if len(found_items) != 1:
        raise ValueError(
            "Found wrong number of pods = {}".format(",".join(found_items))
        )
    return found_items[0]


class _PortForward:
    def __init__(self, pod_name: str, target_port: int) -> None:
        self.lock = Lock()
        self.proc: Optional[subprocess.Popen] = None

        if pod_name is not None:
            self.thread = Thread(target=self._loop, args=[pod_name, target_port])
            self.thread.start()

    def terminate(self) -> None:
        with self.lock:
            if self.proc is not None:
                self.proc.terminate()

    def _loop(self, nominal_pod_name: str, target_port: str) -> None:
        while True:
            pod_name = _find_pod_name(nominal_pod_name)
            if pod_name is None:
                time.sleep(1)
                continue

            with self.lock:
                self.proc = subprocess.Popen(
                    [
                        "kubectl",
                        "port-forward",
                        pod_name,
                        f"{target_port}:{target_port}",
                    ],
                )

            assert self.proc is not None
            retcode = self.proc.wait()
            if retcode < 0:
                # Negative retcodes typically mean the process was killed
                # with an external signal (e.g. -15 for SIGTERM).
                # We don't want to rerun in such a case.
                break
            time.sleep(1)


def create_forwards() -> List[Any]:
    trino_process = _PortForward("trino-coordinator", 8080)
    ranger_process = _PortForward("ranger-admin", 6080)
    maria_process = _PortForward("mariadb", 3306)
    minio_process = _PortForward("minio", 9000)
    redis_process = _PortForward("redis", 6379)

    return list(
        filter(
            None,
            [
                trino_process,
                ranger_process,
                maria_process,
                minio_process,
                redis_process,
            ],
        )
    )

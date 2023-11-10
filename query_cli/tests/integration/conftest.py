import os
import signal
import subprocess
import time
from typing import Any
from typing import Callable
from typing import List
from typing import Tuple

import psutil
import requests


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEBUG = False


def _debug(msg):
    if DEBUG:
        print(msg)


PROCESS_HANDLER = Callable[[psutil.Process], None]


def kill(process: psutil.Process) -> None:
    process.kill()


def sigint(process: psutil.Process) -> None:
    process.send_signal(signal.SIGINT)


def _process_processor(
    procs_and_labels: List[Tuple[Any, str]], handler: PROCESS_HANDLER
):
    for proc, label in procs_and_labels:
        _debug("Terminating {}".format(label))
        if proc is None:
            continue
        try:
            parent = psutil.Process(proc.pid)
            for child in parent.children(
                recursive=True
            ):  # or parent.children() for recursive=False
                _debug("killing child")
                handler(child)
            _debug("killing parent")
            handler(parent)
        except Exception as e:
            # No matter what we want to try the next one
            _debug("Something went weird terminating {}".format(label))
            _debug(e)
            pass


class TestState:
    def __init__(self) -> None:
        self._processes_to_kill: List[Tuple[Any, str]] = []
        self._processes_to_signal: List[Tuple[Any, str]] = []

    def add_kill(self, pid_label: Tuple[Any, str]) -> None:
        self._processes_to_kill.append(pid_label)

    def add_signal(self, pid: Any, label: str) -> None:
        self._processes_to_signal.append((pid, label))

    def cleanup(self):
        _process_processor(self._processes_to_kill, kill)
        _process_processor(self._processes_to_signal, sigint)


def check_for_healthy(label: str, port: int) -> bool:
    try:
        _debug("Performing healthcheck for {}".format(label))
        url = "http://localhost:{}/healthcheck".format(port)
        r = requests.get(
            url=url,
            headers={
                "Accept": "application/json",
            },
        )
        if r.status_code == 200:
            return True
        return False
    except requests.exceptions.ConnectionError:
        return False


def wait_for_healthy(label: str, port: int):
    success = False
    for try_num in range(30):
        time.sleep(1)
        if check_for_healthy(label, port):
            success = True
            break

    if not success:
        raise ValueError("Unable to start {} process".format(label))


def _run_service(dir_name, port_num) -> Tuple[Any, str]:
    if not check_for_healthy(dir_name, port_num):
        p = subprocess.Popen(
            ["python", "-m", "{}.main".format(dir_name)],
            cwd=os.path.join(SCRIPT_DIR, "../../../"),
        )
        wait_for_healthy(dir_name, port_num)
        return p, dir_name
    else:
        return None, dir_name

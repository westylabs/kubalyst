from typing import List, Tuple, Any
import subprocess
import os
import requests
import time

import psutil
import pytest


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEBUG = False


def _debug(msg):
    if DEBUG:
        print(msg)


def process_terminator(procs_and_labels: List[Tuple[Any, str]]):
    for proc, label in procs_and_labels:
        try:
            _debug("Terminating {}".format(label))
            parent = psutil.Process(proc.pid)
            for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                _debug("killing child")
                child.kill()
            _debug("killing parent")
            parent.kill()
        except Exception as e:
            # No matter what we want to try the next one
            _debug("Something went weird terminating {}".format(label))
            _debug(e)
            pass


def wait_for_healthy(label: str, port: int):
    success = False
    for try_num in range(30):
        try:
            _debug("Performing healthcheck for {}".format(label))
            url = "http://localhost:{}/healthcheck".format(port)
            r = requests.get(
                url=url,
                headers={
                    'Accept': 'application/json',
                },
            )
            if r.status_code == 200:
                success = True
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)

    if not success:
        raise ValueError("Unable to start {} process".format(label))


def _run_service(dir_name, port_num) -> Tuple[Any, str]:
    p = subprocess.Popen(
        [os.path.join(SCRIPT_DIR, "../../../{}/run_service.sh".format(dir_name))],
        cwd=os.path.join(SCRIPT_DIR, "../../../{}/".format(dir_name)),
        shell=True
    )
    wait_for_healthy(dir_name, port_num)
    return p, dir_name


def _run_orgdata() -> List[Tuple[Any, str]]:
    return [_run_service("orgdata", 7784)]


def _run_query() -> List[Tuple[Any, str]]:
    return [_run_service("query", 7782)]


def _run_taskman() -> List[Tuple[Any, str]]:
    p_tuple = _run_service("taskman", 7785)
    p2 = subprocess.Popen(
        [os.path.join(SCRIPT_DIR, "../../../taskman/run_worker.sh")],
        cwd=os.path.join(SCRIPT_DIR, "../../../taskman/"),
        shell=True
    )
    return [p_tuple, (p2, "taskman_worker")]


def _run_session() -> List[Tuple[Any, str]]:
    return [_run_service("session", 7783)]


@pytest.fixture(scope='session')
def orgdata():
    procs_and_labels = _run_orgdata()
    yield procs_and_labels
    process_terminator(procs_and_labels)


@pytest.fixture(scope='session')
def query():
    procs_and_labels = _run_query()
    yield procs_and_labels
    process_terminator(procs_and_labels)


@pytest.fixture(scope='session')
def taskman():
    procs_and_labels = _run_taskman()
    yield procs_and_labels
    process_terminator(procs_and_labels)


@pytest.fixture(scope='session')
def session():
    procs_and_labels = _run_session()
    yield procs_and_labels
    process_terminator(procs_and_labels)


@pytest.fixture(scope='session')
def all_services():
    p1 = _run_orgdata()
    p2 = _run_query()
    p3 = _run_taskman()
    p4 = _run_session()
    procs_and_labels = p1 + p2 + p3 + p4
    yield procs_and_labels
    process_terminator(procs_and_labels)

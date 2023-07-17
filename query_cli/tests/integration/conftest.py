import os
import subprocess
import time
from typing import Any
from typing import List
from typing import Tuple

import psutil
import pytest
import requests
import snowflake.connector


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEBUG = False


def _debug(msg):
    if DEBUG:
        print(msg)


def process_terminator(procs_and_labels: List[Tuple[Any, str]]):
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
                child.kill()
            _debug("killing parent")
            parent.kill()
        except Exception as e:
            # No matter what we want to try the next one
            _debug("Something went weird terminating {}".format(label))
            _debug(e)
            pass


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


def _run_orgdata() -> List[Tuple[Any, str]]:
    return [_run_service("orgdata", 7784)]


def _run_query() -> List[Tuple[Any, str]]:
    return [_run_service("query", 7782)]


def _run_taskman() -> List[Tuple[Any, str]]:
    p_tuple = _run_service("taskman", 7785)
    p2 = subprocess.Popen(
        "taskman_worker",
        cwd=os.path.join(SCRIPT_DIR, "../../../taskman/"),
        shell=True,
    )
    return [p_tuple, (p2, "taskman_worker")]


def _run_session() -> List[Tuple[Any, str]]:
    return [_run_service("session", 7783)]


def _run_webui() -> List[Tuple[Any, str]]:
    return [_run_service("webui", 7786)]


@pytest.fixture(scope="session")
def orgdata():
    procs_and_labels = _run_orgdata()
    yield procs_and_labels
    process_terminator(procs_and_labels)


@pytest.fixture(scope="session")
def query():
    procs_and_labels = _run_query()
    yield procs_and_labels
    process_terminator(procs_and_labels)


@pytest.fixture(scope="session")
def taskman():
    procs_and_labels = _run_taskman()
    yield procs_and_labels
    process_terminator(procs_and_labels)


@pytest.fixture(scope="session")
def session():
    procs_and_labels = _run_session()
    yield procs_and_labels
    process_terminator(procs_and_labels)


@pytest.fixture(scope="session")
def webui():
    procs_and_labels = _run_webui()
    yield procs_and_labels
    process_terminator(procs_and_labels)


@pytest.fixture(scope="session")
def all_services():
    p1 = _run_orgdata()
    p2 = _run_query()
    p3 = _run_taskman()
    p4 = _run_session()
    p5 = _run_webui()
    procs_and_labels = p1 + p2 + p3 + p4 + p5
    yield procs_and_labels
    process_terminator(procs_and_labels)


@pytest.fixture(scope="module")
def con() -> snowflake.connector.SnowflakeConnection:
    con = snowflake.connector.connect(
        host="localhost",
        port=7782,
        protocol="http",
        user="dude@sweet.com",
        password="XXXX",
        account="org123",
        session_parameters={
            "QUERY_TAG": "EndOfMonthFinancials",
        },
    )
    try:
        yield con
    finally:
        con.close()

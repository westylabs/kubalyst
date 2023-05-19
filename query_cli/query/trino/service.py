from typing import Dict, Any
import time

import requests
from requests.auth import HTTPBasicAuth

from query.trino.client import Session

TRINO_URL = "http://localhost:8080/"


def make_request(session: Session, query: str) -> requests.Response:
    requests_session = requests.Session()
    prepared_request = session.build_request(query)
    response = requests_session.send(prepared_request)
    if response.status_code != 200:
        print("FAILED = {}".format(response.text))
        raise ValueError(response.status_code)

    session.process_response(response)
    return response
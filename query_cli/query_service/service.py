from typing import Any
from typing import Dict

import requests
from requests.auth import HTTPBasicAuth

from query_cli.query_service.models import StatementsModel


QUERY_URL = "http://localhost:7782"


def query(command_str: str) -> Dict[str, Any]:
    model = StatementsModel()
    model.statement = command_str
    r = requests.post(
        url="{}/api/v2/statements".format(QUERY_URL),
        auth=HTTPBasicAuth("dude", "sweet"),
        json=vars(model),
        headers={
            "Accept": "application/json",
        },
    )

    if r.status_code != 200:
        print("status code = {}".format(r.status_code))
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def get_status(statement_handle: str) -> Dict[str, Any]:
    url = "{}/api/v2/statements/{}".format(QUERY_URL, statement_handle)
    r = requests.get(
        url=url,
        headers={
            "Accept": "application/json",
        },
    )

    if r.status_code != 200:
        print("status code = {}".format(r.status_code))
        print(r.text)
        raise ValueError("Nope")
    return r.json()

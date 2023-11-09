from typing import Any
from typing import List
from typing import Optional

import requests

from query_cli.trino import client
from query_cli.trino import service


TRINO_URL = "http://localhost:8080"


class QueryResponse:
    def __init__(
        self,
        session: client.Session,
    ) -> None:
        self.session = session
        self.columns: List[str] = []
        self.data: List[List[Any]] = []


def query(
    org_id: str, statement: str, session: Optional[client.Session] = None
) -> QueryResponse:
    if session is None:
        session = client.Session.new(TRINO_URL, org_id)
    else:
        if org_id != session.org_id:
            raise ValueError("Session is for another org")

    response = service.make_request(session, statement)

    if response.status_code != 200:
        raise ValueError("nope")

    response_body = response.json()
    print(response.text)
    query_response = QueryResponse(session)

    while "nextUri" in response_body:
        response = requests.get(
            response_body["nextUri"],
            auth=client.BASIC_AUTH,
        )

        if response.status_code != 200:
            raise ValueError("subsequent nope")
        session.process_response(response)

        response_body = response.json()
        if response_body.get("stats", {}).get("state") == "FAILED":
            raise ValueError(
                "Query failed: {}".format(response_body["error"]["message"])
            )
        if "columns" in response_body:
            query_response.columns = response_body["columns"]
        if "data" in response_body:
            query_response.data.extend(response_body["data"])
        print(response.text)

    return query_response

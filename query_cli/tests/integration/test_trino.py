from datetime import datetime
from typing import Union

import pytest
from trino.client import ClientSession
from trino.client import TrinoQuery
from trino.client import TrinoRequest
from trino.client import TrinoResult


@pytest.fixture
def session() -> ClientSession:
    return ClientSession(
        user="admin",
        catalog="hive",
        schema="default",
    )


@pytest.fixture
def trino_request(session: ClientSession) -> TrinoRequest:
    return TrinoRequest(
        host="localhost",
        port=8080,
        client_session=session,
    )


def assert_results(result: TrinoResult, expected: list[list[Union[str, int]]]):
    assert len(result.rows) == len(expected), "Unexpected number of results returned"
    assert result.rows == expected, "Unexpected row value(s)"


def assert_column_types(query: TrinoQuery, expected: list[str]):
    assert len(query.columns) == len(expected), "Unexpected number of columns returned"
    assert [c["type"] for c in query.columns] == expected, "Unexpected column type(s)"


def assert_column_names(query: TrinoQuery, expected: list[str]):
    assert len(query.columns) == len(expected), "Unexpected number of columns returned"
    assert [c["name"] for c in query.columns] == expected, "Unexpected column names(s)"


def test_trino_query_table(trino_request):
    TrinoQuery(trino_request, """DROP TABLE IF EXISTS users""").execute()
    TrinoQuery(
        trino_request,
        """CREATE TABLE users (
        insertion_timestamp TIMESTAMP,
        name VARCHAR(20),
        age INTEGER,
        is_active BOOLEAN)""",
    ).execute()

    now = datetime.now().replace(microsecond=0)
    TrinoQuery(
        trino_request,
        f"INSERT INTO users VALUES (timestamp '{now}', 'joe', 25, false)",
    ).execute()

    query = TrinoQuery(trino_request, "SELECT * FROM users")
    result = query.execute()
    assert_results(result, [[now, "joe", 25, False]])
    assert_column_names(query, ["insertion_timestamp", "name", "age", "is_active"])
    assert_column_types(query, ["timestamp(3)", "varchar(20)", "integer", "boolean"])

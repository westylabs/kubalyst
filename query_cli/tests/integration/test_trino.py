
from query.trino import query as trino_query


def test_basic_query() -> None:
    response1 = trino_query.query("fake_org_id", "USE hive.greg")
    response3 = trino_query.query("fake_org_id", "show tables", response1.session)
    print(response3.columns)    
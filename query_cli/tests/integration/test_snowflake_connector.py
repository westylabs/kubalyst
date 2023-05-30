

import snowflake.connector

from tests.integration.conftest import orgdata


def test_basic_error(all_services):
    con = snowflake.connector.connect(
        host="localhost",
        port=7782,
        protocol="http",
        user='XXXX',
        password='XXXX',
        account='XXXX',
        session_parameters={
            'QUERY_TAG': 'EndOfMonthFinancials',
        }
    )

    try:
        all_data = con.cursor().execute("select * from test").fetchall()
        assert False
    except snowflake.connector.errors.ProgrammingError:
        pass


def test_basic_ddl(all_services):
    con = snowflake.connector.connect(
        host="localhost",
        port=7782,
        protocol="http",
        user='XXXX',
        password='XXXX',
        account='XXXX',
        session_parameters={
            'QUERY_TAG': 'EndOfMonthFinancials',
        }
    )

    con.cursor().execute("create or replace schema test1")


def test_basic_query(all_services):
    con = snowflake.connector.connect(
        host="localhost",
        port=7782,
        protocol="http",
        user='XXXX',
        password='XXXX',
        account='XXXX',
        session_parameters={
            'QUERY_TAG': 'EndOfMonthFinancials',
        }
    )

def test_data_types(all_services):
    con = snowflake.connector.connect(
        host="localhost",
        port=7782,
        protocol="http",
        user='XXXX',
        password='XXXX',
        account='XXXX',
        session_parameters={
            'QUERY_TAG': 'EndOfMonthFinancials',
        }
    )

    for statement in [
        "drop table if exists test1.test1",
        "create table test1.test1 (a int, b int, c varchar)",
        "insert into test1.test1 (a, b, c) values (123, 456, 'hello world')",
        "select * from test1.test1",
    ]:
        print(f"executing statement {statement}")
        con.cursor().execute(statement).fetchall()

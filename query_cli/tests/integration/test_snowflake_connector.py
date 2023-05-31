

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
        user='dude@sweet.com',
        password='XXXX',
        account='org123',
        session_parameters={
            'QUERY_TAG': 'EndOfMonthFinancials',
        }
    )

    con.cursor().execute("create or replace database testdb1")  
    con.cursor().execute("use database testdb1")  
    con.cursor().execute("create or replace schema test1")


def test_basic_fetchall(all_services):
    con = snowflake.connector.connect(
        host="localhost",
        port=7782,
        protocol="http",
        user='dude@sweet.com',
        password='XXXX',
        account='org123',
        session_parameters={
            'QUERY_TAG': 'EndOfMonthFinancials',
        }
    )
    
    result = con.cursor().execute("create or replace database testdb1").fetchall()
    assert len(result) == 1
    assert 'successfully' in result[0][0]
    

def test_data_types(all_services):
    con = snowflake.connector.connect(
        host="localhost",
        port=7782,
        protocol="http",
        user='dude@sweet.com',
        password='XXXX',
        account='org123',
        session_parameters={
            'QUERY_TAG': 'EndOfMonthFinancials',
        }
    )

    for statement in [
        "create or replace database testdb1",
        "use database testdb1",
        "create schema if not exists test1",
        "drop table if exists testdb1.test1.testtable",
        "create table testdb1.test1.testtable (a int, b int, c varchar)",
        "insert into test1.testtable (a, b, c) values (123, 456, 'hello world')",
        "select * from test1.testtable",
    ]:
        print(f"executing statement {statement}")
        values = con.cursor().execute(statement).fetchall()

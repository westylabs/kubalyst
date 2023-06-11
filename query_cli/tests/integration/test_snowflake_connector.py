from decimal import Decimal
from typing import List, Optional, Any, Tuple
from datetime import datetime

import pytz

import snowflake.connector


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
        con.cursor().execute("select * from test").fetchall()
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
    con.cursor().execute("create or replace schema test2")


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
        con.cursor().execute(statement).fetchall()


class Statement():
    def __init__(
        self,
        sql_statement: str,
        expected_result: Optional[List[List[Any]]] = None,
        error: Optional[Tuple[str, str, str]] = None
    ) -> None:
        assert expected_result is None or error is None
        self.sql_statement = sql_statement
        self.expected_results = expected_result
        self.error = error


def _connect() -> snowflake.connector.SnowflakeConnection:
    return snowflake.connector.connect(
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


def _run_statement(con: snowflake.connector.SnowflakeConnection, statement: Statement) -> None:
    try:
        cursor = con.cursor().execute(statement.sql_statement)
        if statement.expected_results is not None:
            result = cursor.fetchall()
            assert len(result) == len(statement.expected_results)
            for result_row, expected_result_row in zip(result, statement.expected_results):
                assert len(result_row) == len(expected_result_row)
                not_equal = []
                for i, (result_field, expected_result_field) in enumerate(zip(result_row, expected_result_row)):
                    if result_field != expected_result_field:
                        not_equal.append((i, result_field, expected_result_field))
                assert not_equal == []
    except snowflake.connector.errors.ProgrammingError as e:
        assert statement.error is not None, e
        assert e.errno == statement.error[0]
        assert e.sqlstate == statement.error[1]
        assert statement.error[2] in e.msg


def _run_test(statements: List[Statement]) -> None:
    con = _connect()

    for statement in statements:
        _run_statement(con, statement)


def test_schema_lifetime(all_services) -> None:
    _run_test([
        Statement(
            "create or replace database testdb",
        ),
        Statement(
            "use database testdb",
            expected_result=[["Statement executed successfully."]],
        ),
        Statement(
            "drop schema if exists testschema1",
        ),
        Statement(
            "drop schema if exists testschema1",
            expected_result=[["Drop statement executed successfully (TESTSCHEMA1 already dropped)."]],
        ),
        Statement(
            "create schema testschema1",
            expected_result=[["Schema TESTSCHEMA1 successfully created."]],
        ),
        Statement(
            "drop schema if exists testschema1",
            expected_result=[["TESTSCHEMA1 successfully dropped."]],
        ),
    ])

    _run_test([
        Statement(
            "create or replace database testdb",
        ),
        Statement(
            "use database testdb",
            expected_result=[["Statement executed successfully."]],
        ),
        Statement(
            "drop if exists schema",
            error=(1003, "42000", "SQL compilation error:\nsyntax error line 1 at position 5 unexpected 'if'."),
        ),
    ])


def test_table_describe(all_services) -> None:
    _run_test([
        Statement(
            "create or replace database testdb",
        ),
        Statement(
            "use database testdb",
            expected_result=[["Statement executed successfully."]],
        ),
        Statement(
            "create schema if not exists test1",
        ),
        Statement(
            "use schema test1",
            expected_result=[["Statement executed successfully."]],
        ),
        Statement(
            "CREATE OR REPLACE TABLE test_fixed(num NUMBER, num10 NUMBER(10,1), dec DECIMAL(20,2), numeric NUMERIC(30,3), int INT, integer INTEGER);",
            expected_result=[["Table TEST_FIXED successfully created."]],
        ),
        Statement(
            "DESC TABLE test_fixed",
            expected_result=[
                ('NUM', 'NUMBER(38,0)', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
                ('NUM10', 'NUMBER(10,1)', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
                ('DEC', 'NUMBER(20,2)', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
                ('NUMERIC', 'NUMBER(30,3)', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
                ('INT', 'NUMBER(38,0)', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
                ('INTEGER', 'NUMBER(38,0)', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
            ],
        ),
        Statement(
            "CREATE OR REPLACE TABLE test_float(d DOUBLE, f FLOAT, dp DOUBLE PRECISION, r REAL);",
            expected_result=[["Table TEST_FLOAT successfully created."]]
        ),
        Statement(
            "DESC TABLE test_float",
            expected_result=[
                ('D', 'FLOAT', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
                ('F', 'FLOAT', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
                ('DP', 'FLOAT', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
                ('R', 'FLOAT', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
            ],
        ),
    ])


def test_table_query_numbers(all_services) -> None:
    _run_test([
        Statement(
            "create or replace database testdb",
        ),
        Statement(
            "use database testdb",
            expected_result=[["Statement executed successfully."]],
        ),
        Statement(
            "create schema if not exists test1",
        ),
        Statement(
            "use schema test1",
            expected_result=[["Statement executed successfully."]],
        ),
        Statement(
            "CREATE OR REPLACE TABLE test_fixed(num NUMBER, num10 NUMBER(10,1), dec DECIMAL(20,2), numeric NUMERIC(30,3), int INT, integer INTEGER);",
            expected_result=[["Table TEST_FIXED successfully created."]],
        ),
        Statement(
            "INSERT INTO test_fixed VALUES(1.234E2, 15, 9, 1.234E+2, 11, 12)",
            expected_result=[[1]]
        ),
        Statement(
            "select * from test_fixed",
            expected_result=[
                (123, Decimal('15.0'), Decimal('9.00'), Decimal('1.234E+2'), 11, 12)
            ]
        ),
        Statement(
            "select num, dec, int from test_fixed",
            expected_result=[
                (123, Decimal('9'), 11)
            ]
        ),
        Statement(
            "CREATE OR REPLACE TABLE test_float(d DOUBLE, f FLOAT, dp DOUBLE PRECISION, r REAL);",
            expected_result=[["Table TEST_FLOAT successfully created."]]
        ),
        Statement(
            "INSERT INTO test_float VALUES(+1.34, 0.1, -1.2, 15e-03)",
            expected_result=[[1]]
        ),
        Statement(
            "select * from test_float",
            expected_result=[
                (+1.34, 0.1, -1.2, 15e-03),
            ]
        ),
    ])


def test_table_timestamp(all_services) -> None:
    con = _connect()
    _run_statement(
        con,
        Statement(
            "create or replace database testdb",
        )
    )
    _run_statement(
        con,
        Statement(
            "use database testdb",
            expected_result=[["Statement executed successfully."]],
        )
    )
    _run_statement(
        con,
        Statement(
            "create schema if not exists test1",
        )
    )
    _run_statement(
        con,
        Statement(
            "use schema test1",
            expected_result=[["Statement executed successfully."]],
        )
    )
    _run_statement(
        con,
        Statement(
            "CREATE OR REPLACE TABLE test_ts(tsltz timestamp_ltz, tsntz timestamp_ntz, tstz timestamp_tz);",
            expected_result=[["Table TEST_TS successfully created."]],
        )
    )
    _run_statement(
        con,
        Statement(
            "INSERT INTO test_ts VALUES(to_timestamp('2023-01-01 01:01:01'), to_timestamp('2023-02-02 02:02:02'), to_timestamp('2023-03-03 03:03:03'))",
            expected_result=[[1]]
        )
    )
    _run_statement(
        con,
        Statement(
            "select tsltz, tsntz, tstz from test_ts",
            expected_result=[
                (
                    datetime(2023, 1, 1, 1, 1, 1, tzinfo=pytz.timezone('America/Los_Angeles')),
                    datetime(2023, 2, 2, 2, 2, 2),
                    datetime(2023, 3, 3, 3, 3, 3, tzinfo=pytz.FixedOffset(-480)),
                )
            ]
        )
    )
    _run_statement(
        con,
        Statement(
            "describe table test_ts",
            expected_result=[
                ('TSLTZ', 'TIMESTAMP_LTZ', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
                ('TSNTZ', 'TIMESTAMP_NTZ', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
                ('TSTZ', 'TIMESTAMP_TZ', 'COLUMN', "Y", None, "N", "N", None, None, None, None),
            ],
        )
    )

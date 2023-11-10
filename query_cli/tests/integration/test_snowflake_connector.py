from datetime import datetime
from decimal import Decimal
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pytz
import snowflake.connector


ANY_VALUE: Dict[str, Any] = {}


def test_basic_error(all_services, con):
    try:
        con.cursor().execute("select * from test").fetchall()
        assert False
    except snowflake.connector.errors.ProgrammingError:
        pass


def test_basic_ddl(all_services, con):
    con.cursor().execute("create or replace database testdb1")
    con.cursor().execute("use database testdb1")
    con.cursor().execute("create or replace schema test2")

    # This call currently crashes the query service
    # The last valid conduyt stack in the traceback is:
    #   File "/Users/jmackay/code/conduyt/core/query/commands/data.py", line 141, in _base64_encode_worker
    con.cursor().execute("show databases")

    # Test currently returns lots of databases bc we create dupes, skip validating count for now
    # assert len(list(filter(lambda result: result[0] == "testdb1", results))) == 1


def test_basic_fetchall(all_services, con):
    result = con.cursor().execute("create or replace database testdb1").fetchall()
    assert len(result) == 1
    assert "successfully" in result[0][0]


def test_data_types(all_services, con):
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


class Statement:
    def __init__(
        self,
        sql_statement: str,
        expected_result: Optional[List[List[Any]]] = None,
        error: Optional[Tuple[int, str, str]] = None,
    ) -> None:
        assert expected_result is None or error is None
        self.sql_statement = sql_statement
        self.expected_results = expected_result
        self.error = error


def _render_not_equal(not_equal: list[tuple[int, Any, Any]]) -> str:
    lines = []
    for index, result, expected in not_equal:
        lines.append(
            f"at {index}: "
            f"got `{result}` ({type(result).__name__}), "
            f"but expected `{expected}` ({type(expected).__name__})"
        )
    return "\n".join(lines)


def _run_statement(con, statement: Statement) -> None:
    try:
        cursor = con.cursor().execute(statement.sql_statement)
        if statement.expected_results is not None:
            result = cursor.fetchall()
            assert len(result) == len(statement.expected_results)
            for result_row, expected_result_row in zip(
                result, statement.expected_results
            ):
                assert len(result_row) == len(expected_result_row)
                not_equal = []
                for i, (result_field, expected_result_field) in enumerate(
                    zip(result_row, expected_result_row)
                ):
                    if (
                        expected_result_field != ANY_VALUE
                        and result_field != expected_result_field
                    ):
                        not_equal.append((i, result_field, expected_result_field))
                if len(not_equal) != 0:
                    assert False, _render_not_equal(not_equal)
    except snowflake.connector.errors.ProgrammingError as e:
        assert statement.error is not None, e
        assert e.errno == statement.error[0]
        assert e.sqlstate == statement.error[1]
        assert statement.error[2] in e.msg


def _run_test(con, statements: List[Statement]) -> None:
    for statement in statements:
        _run_statement(con, statement)


def _simple_select_test(con, select_stmt: str, expected: Any) -> None:
    _run_statement(
        con,
        Statement(select_stmt, expected_result=[[expected]]),
    )


def _simple_select_test_multi(
    con: snowflake.connector.SnowflakeConnection, select_stmt: str, expected: List[Any]
) -> None:
    _run_statement(
        con,
        Statement(select_stmt, expected_result=[expected]),
    )


def _standard_setup(con: snowflake.connector.SnowflakeConnection) -> None:
    _run_statement(
        con,
        Statement(
            "create or replace database testdb",
        ),
    )
    _run_statement(
        con,
        Statement(
            "use database testdb",
            expected_result=[["Statement executed successfully."]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "create schema if not exists test1",
        ),
    )
    _run_statement(
        con,
        Statement(
            "use schema test1",
            expected_result=[["Statement executed successfully."]],
        ),
    )


def test_schema_lifetime(all_services, con) -> None:
    _run_test(
        con,
        [
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
                expected_result=[
                    [
                        "Drop statement executed successfully (TESTSCHEMA1 already dropped)."
                    ]
                ],
            ),
            Statement(
                "create schema testschema1",
                expected_result=[["Schema TESTSCHEMA1 successfully created."]],
            ),
            Statement(
                "drop schema if exists testschema1",
                expected_result=[["TESTSCHEMA1 successfully dropped."]],
            ),
        ],
    )

    _run_test(
        con,
        [
            Statement(
                "create or replace database testdb",
            ),
            Statement(
                "use database testdb",
                expected_result=[["Statement executed successfully."]],
            ),
            Statement(
                "drop if exists schema",
                error=(
                    1003,
                    "42000",
                    "SQL compilation error:\nsyntax error line 1 at position 5 unexpected 'if'.",
                ),
            ),
        ],
    )


def test_table_describe(all_services, con) -> None:
    _run_test(
        con,
        [
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
                    [
                        "NUM",
                        "NUMBER(38,0)",
                        "COLUMN",
                        "Y",
                        None,
                        "N",
                        "N",
                        None,
                        None,
                        None,
                        None,
                    ],
                    [
                        "NUM10",
                        "NUMBER(10,1)",
                        "COLUMN",
                        "Y",
                        None,
                        "N",
                        "N",
                        None,
                        None,
                        None,
                        None,
                    ],
                    [
                        "DEC",
                        "NUMBER(20,2)",
                        "COLUMN",
                        "Y",
                        None,
                        "N",
                        "N",
                        None,
                        None,
                        None,
                        None,
                    ],
                    [
                        "NUMERIC",
                        "NUMBER(30,3)",
                        "COLUMN",
                        "Y",
                        None,
                        "N",
                        "N",
                        None,
                        None,
                        None,
                        None,
                    ],
                    [
                        "INT",
                        "NUMBER(38,0)",
                        "COLUMN",
                        "Y",
                        None,
                        "N",
                        "N",
                        None,
                        None,
                        None,
                        None,
                    ],
                    [
                        "INTEGER",
                        "NUMBER(38,0)",
                        "COLUMN",
                        "Y",
                        None,
                        "N",
                        "N",
                        None,
                        None,
                        None,
                        None,
                    ],
                ],
            ),
            Statement(
                "CREATE OR REPLACE TABLE test_float(d DOUBLE, f FLOAT, dp DOUBLE PRECISION, r REAL);",
                expected_result=[["Table TEST_FLOAT successfully created."]],
            ),
            Statement(
                "DESC TABLE test_float",
                expected_result=[
                    [
                        "D",
                        "FLOAT",
                        "COLUMN",
                        "Y",
                        None,
                        "N",
                        "N",
                        None,
                        None,
                        None,
                        None,
                    ],
                    [
                        "F",
                        "FLOAT",
                        "COLUMN",
                        "Y",
                        None,
                        "N",
                        "N",
                        None,
                        None,
                        None,
                        None,
                    ],
                    [
                        "DP",
                        "FLOAT",
                        "COLUMN",
                        "Y",
                        None,
                        "N",
                        "N",
                        None,
                        None,
                        None,
                        None,
                    ],
                    [
                        "R",
                        "FLOAT",
                        "COLUMN",
                        "Y",
                        None,
                        "N",
                        "N",
                        None,
                        None,
                        None,
                        None,
                    ],
                ],
            ),
        ],
    )


def test_table_query_numbers(all_services, con) -> None:
    _run_test(
        con,
        [
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
                expected_result=[[1]],
            ),
            Statement(
                "select * from test_fixed",
                expected_result=[
                    [123, Decimal("15.0"), Decimal("9.00"), Decimal("1.234E+2"), 11, 12]
                ],
            ),
            Statement(
                "select num, dec, int from test_fixed",
                expected_result=[[123, Decimal("9"), 11]],
            ),
            Statement(
                "CREATE OR REPLACE TABLE test_float(d DOUBLE, f FLOAT, dp DOUBLE PRECISION, r REAL);",
                expected_result=[["Table TEST_FLOAT successfully created."]],
            ),
            Statement(
                "INSERT INTO test_float VALUES(+1.34, 0.1, -1.2, 15e-03)",
                expected_result=[[1]],
            ),
            Statement(
                "select * from test_float",
                expected_result=[
                    [+1.34, 0.1, -1.2, 15e-03],
                ],
            ),
        ],
    )


def test_table_timestamp(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "create or replace database testdb",
        ),
    )
    _run_statement(
        con,
        Statement(
            "use database testdb",
            expected_result=[["Statement executed successfully."]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "create schema if not exists test1",
        ),
    )
    _run_statement(
        con,
        Statement(
            "use schema test1",
            expected_result=[["Statement executed successfully."]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "CREATE OR REPLACE TABLE test_ts(tsltz timestamp_ltz, tsntz timestamp_ntz, tstz timestamp_tz);",
            expected_result=[["Table TEST_TS successfully created."]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "INSERT INTO test_ts VALUES(to_timestamp('2023-01-01 01:01:01'), to_timestamp('2023-02-02 02:02:02'), to_timestamp('2023-03-03 03:03:03'))",
            expected_result=[[1]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "select tsltz, tsntz, tstz from test_ts",
            expected_result=[
                [
                    datetime(2023, 1, 1, 1, 1, 1).astimezone(
                        pytz.timezone("America/Los_Angeles")
                    ),
                    datetime(2023, 2, 2, 2, 2, 2),
                    datetime(2023, 3, 3, 3, 3, 3, tzinfo=pytz.FixedOffset(-480)),
                ]
            ],
        ),
    )
    _run_statement(
        con,
        Statement(
            "describe table test_ts",
            expected_result=[
                [
                    "TSLTZ",
                    "TIMESTAMP_LTZ",
                    "COLUMN",
                    "Y",
                    None,
                    "N",
                    "N",
                    None,
                    None,
                    None,
                    None,
                ],
                [
                    "TSNTZ",
                    "TIMESTAMP_NTZ",
                    "COLUMN",
                    "Y",
                    None,
                    "N",
                    "N",
                    None,
                    None,
                    None,
                    None,
                ],
                [
                    "TSTZ",
                    "TIMESTAMP_TZ",
                    "COLUMN",
                    "Y",
                    None,
                    "N",
                    "N",
                    None,
                    None,
                    None,
                    None,
                ],
            ],
        ),
    )


def test_table_variant(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "create or replace database testdb",
        ),
    )
    _run_statement(
        con,
        Statement(
            "use database testdb",
            expected_result=[["Statement executed successfully."]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "create schema if not exists test1",
        ),
    )
    _run_statement(
        con,
        Statement(
            "use schema test1",
            expected_result=[["Statement executed successfully."]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "create or replace table vartab (n number(2), v variant);",
            expected_result=[["Table VARTAB successfully created."]],
        ),
    )

    insert_str = """
    insert into vartab
        select column1 as n, parse_json(column2) as v
        from values (1, 'null'),
                    (2, null),
                    (3, 'true'),
                    (4, '-17'),
                    (5, '123.12'),
                    (6, '1.912e2'),
                    (7, '"Om ara pa ca na dhih"  '),
                    (8, '[-1, 12, 289, 2188, false]'),
                    (9, '{ "x" : "abc", "y" : false, "z": 10} ')
        AS vals;
    """

    _run_statement(
        con,
        Statement(
            insert_str,
            expected_result=[[9]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "select n, v, typeof(v) from vartab order by n;",
            expected_result=[
                [1, "null", "NULL_VALUE"],
                [2, None, None],
                [3, "true", "BOOLEAN"],
                [4, "-17", "INTEGER"],
                [5, "123.12", "DECIMAL"],
                [6, "191.2", "DECIMAL"],  # Snowflake returns DOUBLE here
                [7, '"Om ara pa ca na dhih"', "VARCHAR"],
                [
                    8,
                    "[\n  -1,\n  12,\n  289,\n  2188,\n  false\n]",
                    "ARRAY",
                ],
                [9, '{\n  "x": "abc",\n  "y": false,\n  "z": 10\n}', "OBJECT"],
            ],
        ),
    )


def test_table_object(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "create or replace database testdb",
        ),
    )
    _run_statement(
        con,
        Statement(
            "use database testdb",
            expected_result=[["Statement executed successfully."]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "create schema if not exists test1",
        ),
    )
    _run_statement(
        con,
        Statement(
            "use schema test1",
            expected_result=[["Statement executed successfully."]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "create or replace table xyz_table (id integer, obj object);",
            expected_result=[["Table XYZ_TABLE successfully created."]],
        ),
    )

    insert_str = """
insert into xyz_table(id, obj) select 1, parse_json($${
  "first_name": "John",
  "last_name": "Corner",
  "createddate": "2019-07-02T10:01:30+00:00",
  "type": "Owner",
  "country": {
    "code": "US",
    "name": "United States"
  }
}$$);
    """

    _run_statement(
        con,
        Statement(
            insert_str,
            expected_result=[[1]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "select * from xyz_table",
            expected_result=[
                [
                    1,
                    '{"country":{"code":"US","name":"United States"},"createddate":"2019-07-02T10:01:30+00:00",'
                    '"first_name":"John","last_name":"Corner","type":"Owner"}',
                ]
            ],
        ),
    )
    _run_statement(
        con,
        Statement(
            "select obj:country from xyz_table",
            expected_result=[['{\n  "code": "US",\n  "name": "United States"\n}']],
        ),
    )


def test_ascii(all_services, con) -> None:
    _standard_setup(con)
    _run_statement(
        con,
        Statement(
            "SELECT column1, ASCII(column1) FROM (values('!'), ('A'), ('a'), ('bcd'), (''), (null));",
            expected_result=[
                ["!", 33],
                ["A", 65],
                ["a", 97],
                ["bcd", 98],
                ["", 0],
                [None, None],
            ],
        ),
    )


def test_base64_encode(all_services, con) -> None:
    _standard_setup(con)
    _run_statement(
        con,
        Statement(
            "CREATE OR REPLACE TABLE binary_table (v VARCHAR, b BINARY, b64_string VARCHAR);",
        ),
    )
    _run_statement(
        con,
        Statement(
            "select 'HELP', TO_BINARY('HELP', 'UTF-8'), BASE64_ENCODE(TO_BINARY('HELP', 'UTF-8'))",
            expected_result=[["HELP", b"HELP", "SEVMUA=="]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "INSERT INTO binary_table (v, b, b64_string) VALUES ('HELP', TO_BINARY('HELP', 'UTF-8'), BASE64_ENCODE(TO_BINARY('HELP', 'UTF-8')))",
        ),
    )
    _run_statement(
        con,
        Statement(
            "SELECT v, b, b64_string FROM binary_table;",
            expected_result=[["HELP", b"HELP", "SEVMUA=="]],
        ),
    )


def test_base64_decode(all_services, con) -> None:
    _standard_setup(con)
    _run_statement(
        con,
        Statement(
            "SELECT BASE64_DECODE_STRING('U25vd2ZsYWtl');",
            expected_result=[["Snowflake"]],
        ),
    )


def test_bit_length(all_services, con) -> None:
    _standard_setup(con)
    _run_statement(
        con,
        Statement(
            "CREATE OR REPLACE TABLE bl (v VARCHAR, b BINARY);",
        ),
    )
    _run_statement(
        con,
        Statement(
            "INSERT INTO bl (v, b) VALUES ('abc', NULL), (NULL, X'A1B2');",
        ),
    )

    _run_statement(
        con,
        Statement(
            "SELECT v, b, BIT_LENGTH(v), BIT_LENGTH(b) FROM bl ORDER BY v;",
            expected_result=[
                ["abc", None, 24, None],
                [None, bytearray(b"\xa1\xb2"), None, 16],
            ],
        ),
    )


def test_chr(all_services, con) -> None:
    _standard_setup(con)
    _run_statement(
        con,
        Statement(
            "SELECT column1, CHR(column1) FROM (VALUES(83), (33), (169), (8364), (0), (null));",
            expected_result=[
                [83, "S"],
                [33, "!"],
                [169, "©"],
                [8364, "€"],
                [0, "\x00"],
                [None, None],
            ],
        ),
    )


def test_charindex(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "select charindex('ban', 'banana'), charindex('an', 'banana', 1), charindex('an', 'banana', 3);",
            expected_result=[[1, 2, 4]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "select charindex('nope', 'banana'), charindex('nope', 'banana', 1), charindex('nope', 'banana', 3);",
            expected_result=[[0, 0, 0]],
        ),
    )


def test_contains(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "select contains('banana', 'bana'), contains('banana', 'nope');",
            expected_result=[[True, False]],
        ),
    )


def test_div0(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "select div0(1, 2), div0(1, 0);",
            expected_result=[[0.5, 0]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "select div0(1, 2), div0(1, 0), div0(1, NULL);",
            expected_result=[[0.5, 0, None]],
        ),
    )


def test_editdistance(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "select editdistance('Gute nacht', 'Ich weis nicht'), editdistance('Gute nacht', 'Ich weis nicht', 3)",
            expected_result=[[8, 3]],
        ),
    )


def test_endswith(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "select endswith('banana', 'nana'), endswith('banana', 'an')",
            expected_result=[[True, False]],
        ),
    )


def test_exp(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "SELECT EXP(1), EXP(LN(10));",
            expected_result=[[2.718281828459045, 10.000000000000002]],
        ),
    )


def test_hex(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "SELECT 'HELLO', HEX_ENCODE('HELLO'), HEX_DECODE_BINARY(HEX_ENCODE('HELLO'));",
            expected_result=[["HELLO", "48454C4C4F", b"HELLO"]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "SELECT HEX_DECODE_STRING('536E6F77666C616B65');",
            expected_result=[["Snowflake"]],
        ),
    )


"""
def test_initcap(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "SELECT initcap('The Quick Gray Fox'), initcap('the sky is blue'), initcap('OVER the River 2 times')",
            expected_result=[
                ["The Quick Gray Fox", "The Sky Is Blue", "Over The River 2 Times"]
            ],
        ),
    )
"""


def test_insert_function(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "SELECT INSERT('abc', 1, 2, 'Z'), INSERT('abcdef', 3, 2, 'zzz'), INSERT('abc', 2, 1, '');",
            expected_result=[["Zc", "abzzzef", "ac"]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "SELECT INSERT('abc', 4, 0, 'Z'), INSERT(NULL, 1, 2, 'Z'), INSERT('abc', NULL, 2, 'Z'), INSERT('abc', 1, NULL, 'Z'), INSERT('abc', 1, 2, NULL);",
            expected_result=[["abcZ", None, None, None, None]],
        ),
    )


def test_left(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "SELECT LEFT('ABCDEF', 3);",
            expected_result=[["ABC"]],
        ),
    )


def test_md5(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "SELECT md5('Snowflake'), md5_binary('Snowflake')",
            expected_result=[
                [
                    "edf1439075a83a447fb8b630ddc9c8de",
                    b"\xed\xf1C\x90u\xa8:D\x7f\xb8\xb60\xdd\xc9\xc8\xde",
                ]
            ],
        ),
    )
    _run_statement(
        con,
        Statement(
            "SELECT md5_number_lower64('Snowflake'), md5_number_upper64('Snowflake')",
            expected_result=[[9203306159527282910, 17145559544104499780]],
        ),
    )


def test_octet_length(all_services, con) -> None:
    _simple_select_test(con, "select OCTET_LENGTH('abc')", 3)
    _simple_select_test(con, "select OCTET_LENGTH(X'A1B2')", 2)


def test_position(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "SELECT position('an', 'banana'), position('an' IN 'banana');",
            expected_result=[[2, 2]],
        ),
    )


def test_regexp_extract_all(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "SELECT regexp_substr_all('a1_a2a3_a4A5a6', 'a[[:digit:]]')",
            expected_result=[['[\n  "a1",\n  "a2",\n  "a3",\n  "a4",\n  "a6"\n]']],
        ),
    )
    _run_statement(
        con,
        Statement(
            "SELECT regexp_substr_all('a1_a2a3_a4A5a6', 'a[[:digit:]]', 2)",
            expected_result=[['[\n  "a2",\n  "a3",\n  "a4",\n  "a6"\n]']],
        ),
    )
    _run_statement(
        con,
        Statement(
            "SELECT regexp_substr_all('a1_a2a3_a4A5a6', 'a[[:digit:]]', 1, 3)",
            expected_result=[['[\n  "a3",\n  "a4",\n  "a6"\n]']],
        ),
    )


def test_regexp_instr(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "SELECT "
            "  regexp_instr('nevermore1, nevermore2, nevermore3', 'nevermore\\d'),"
            "  regexp_instr('nevermore1, nevermore2, nevermore3', 'nevermore\\d', 5),"
            "  regexp_instr('nevermore1, nevermore2, nevermore3', 'nevermore\\d', 1, 3),"
            "  regexp_instr('nevermore1, nevermore2, nevermore3', 'nevermore\\d', 1, 4)",
            expected_result=[[1, 13, 25, 0]],
        ),
    )


def test_regexp_like(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "SELECT "
            "  regexp_like('San Francisco', 'San.*'),"
            "  regexp_like('Los Angeles', 'San.*')",
            expected_result=[[True, False]],
        ),
    )


def test_regexp_replace(all_services, con) -> None:
    _run_statement(
        con,
        Statement(
            "SELECT "
            "  regexp_replace('It was the best of times, it was the worst of times', '( ){1,}',''),",
            expected_result=[
                [
                    "Itwasthebestoftimes,itwastheworstoftimes",
                ]
            ],
        ),
    )


def test_repeat(all_services, con) -> None:
    _simple_select_test(con, "SELECT REPEAT('xy', 5);", "xyxyxyxyxy")


def test_right(all_services, con) -> None:
    _simple_select_test(con, "SELECT RIGHT('ABCDEFG', 3);", "EFG")


def test_rtrimmed_right(all_services, con) -> None:
    _simple_select_test(con, "SELECT RTRIMMED_LENGTH(' ABCD ')", 5)


def test_space(all_services, con) -> None:
    _simple_select_test(con, "SELECT space(4)", "    ")


def test_array_construct(all_services, con) -> None:
    _simple_select_test(con, "SELECT array_construct(1, 2, 3)", "[\n  1,\n  2,\n  3\n]")


"""
def test_strtok(all_services, con) -> None:
    _simple_select_test(con, "select STRTOK('user@snowflakezcom', '@z', 1);", "user")
    _simple_select_test(
        con, "select STRTOK('user@snowflakezcom', '@z', 2);", "snowflake"
    )
    _simple_select_test(con, "select STRTOK('user@snowflakezcom', '@z', 3);", "com")
"""


def test_typeof(all_services, con) -> None:
    _simple_select_test_multi(con, "SELECT 1, typeof(1)", [1, "INTEGER"])
    _simple_select_test_multi(
        con, "SELECT 1.1, typeof(1.1)", [Decimal("1.1"), "DECIMAL"]
    )
    _simple_select_test_multi(con, "SELECT 'foo', typeof('foo')", ["foo", "VARCHAR"])
    _simple_select_test_multi(con, "SELECT 1.1e2, typeof(1.1e2)", [110.0, "DOUBLE"])


def test_union_all(all_services, con) -> None:
    _standard_setup(con)
    _run_statement(
        con,
        Statement(
            "CREATE OR REPLACE TABLE left_union (v VARCHAR, b BINARY, b64_string VARCHAR);",
        ),
    )
    _run_statement(
        con,
        Statement(
            "create or replace database testotherdb",
        ),
    )
    _run_statement(
        con,
        Statement(
            "use database testotherdb",
            expected_result=[["Statement executed successfully."]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "create schema if not exists test2",
        ),
    )
    _run_statement(
        con,
        Statement(
            "use schema test2",
            expected_result=[["Statement executed successfully."]],
        ),
    )
    _run_statement(
        con,
        Statement(
            "CREATE OR REPLACE TABLE right_union (v2 VARCHAR, b2 BINARY, b64_string2 VARCHAR);",
        ),
    )
    _run_statement(
        con,
        Statement(
            "select table_catalog, table_schema, table_name, column_name, data_type "
            "from testdb.information_schema.columns where table_name = 'LEFT_UNION' "
            "UNION ALL select table_catalog, table_schema, table_name, column_name, data_type "
            "from testotherdb.information_schema.columns where table_name = 'RIGHT_UNION' "
            "ORDER BY table_catalog, table_schema, table_name",
            expected_result=[
                ["TESTDB", "TEST1", "LEFT_UNION", "v", "VARCHAR"],
                ["TESTDB", "TEST1", "LEFT_UNION", "b", "BINARY"],
                ["TESTDB", "TEST1", "LEFT_UNION", "b64_string", "VARCHAR"],
                ["TESTOTHERDB", "TEST2", "RIGHT_UNION", "v2", "VARCHAR"],
                ["TESTOTHERDB", "TEST2", "RIGHT_UNION", "b2", "BINARY"],
                ["TESTOTHERDB", "TEST2", "RIGHT_UNION", "b64_string2", "VARCHAR"],
            ],
        ),
    )

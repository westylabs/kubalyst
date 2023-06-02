from typing import List, Optional, Any, Tuple
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
        values = con.cursor().execute(statement).fetchall()



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


def _run_test(statements: List[Statement]) -> None:
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

    for statement in statements:
        try:
            cursor = con.cursor().execute(statement.sql_statement)
            if statement.expected_results is not None:
                result = cursor.fetchall()
                assert len(result) == len(statement.expected_results)
                for result_row, expected_result_row in zip(result, statement.expected_results):
                    assert len(result_row) == len(expected_result_row)
                    for result_field, expected_result_field in zip(result_row, expected_result_row):
                        assert result_field == expected_result_field
        except snowflake.connector.errors.ProgrammingError as e:
            assert statement.error is not None
            assert e.errno == statement.error[0]
            assert e.sqlstate == statement.error[1]
            assert statement.error[2] in e.msg


def test_schema_lifetime() -> None:
    _run_test([
        Statement(
            "create or replace database testdb",
        ),
        Statement(
            "use database testdb",
            expected_result=[["Statement executed successfully."]],
        ),
        Statement(
            "drop schema if exists test1",
        ),        
        Statement(
            "drop schema if exists test1",
            expected_result=[["Drop statement executed successfully (TEST1 already dropped)."]],
        ),  
        Statement(
            "create schema test1",
            expected_result=[["Schema TEST1 successfully created."]],
        ),          
        Statement(
            "drop schema if exists test1",
            expected_result=[["TEST1 successfully dropped."]],
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

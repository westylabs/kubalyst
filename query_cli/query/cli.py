from typing import Optional, Dict
import json
import time

import click
import snowflake.connector

from query import services
from query.entities import users, roles
from query.ranger import service as ranger_service
from query.ranger import service2 as ranger_service2
from query.trino import query as trino_query
from query.s3 import service as s3_service
from query.query_service import service as query_service
from query.kube_utils import forward


def _templatize_script(
    script_content: str,
    replacements: Dict[str, str],
) -> str:
    intermediate_script = script_content
    for key, value in replacements.items():
        intermediate_script = intermediate_script.replace(
            "${" + key + "}",
            value,
        )
    assert "${" not in intermediate_script
    return intermediate_script


@click.command()
def get_all_roles() -> None:
    print(ranger_service.get_roles())    


@click.command()
def get_all_users() -> None:
    print(users.get_all_users())  


@click.command()
def create_default_bucket() -> None:
    s3_service.ensure_hive_bucket()


@click.command()
def create_trino_ranger_service() -> None:
    if ranger_service2.get_service("trino") is None:
        ranger_service2.create_trino_service()


@click.command()
@click.option(
    '--org-id', '-o',
    required=True,
    default=None,
    help='The target org id',
)
def create_default_roles(org_id: str) -> None:
    roles.create_default_roles(org_id)


@click.command()
@click.option(
    '--org-id', '-o',
    required=True,
    default=None,
    help='The target org id',
)
def create_default_users(org_id: str) -> None:
    users.create_default_users(org_id)


@click.command()
@click.option(
    '--org-id', '-o',
    required=True,
    default=None,
    help='The target org id',
)
def show_tables(org_id: str) -> None:
    response1 = trino_query.query(org_id, "USE sf10")
    response2 = trino_query.query(org_id, "show tables", response1.session)
    print(response2.data)    


@click.command()
@click.option(
    '--command', '-c',
    required=True,
    default=None,
    help='The command to run',
)
def execute(command) -> None:
    response = query_service.query(command)
    if 'statementHandle' not in response:
        print("No statement handle found")
        return
    
    next_response = query_service.get_status(response['statementHandle'])
    if 'data' in next_response:
        print("Results:")
        for entry in next_response['data']:
            print(entry)


@click.command()
@click.option(
    '--command', '-c',
    required=True,
    default=None,
    help='The command to run',
)
def execute_sql(command) -> None:
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
        
    all_data = con.cursor().execute(command).fetchall()
    print("DATA = {}".format(all_data))


@click.command()
@click.option(
    '--name', '-n',
    required=True,
    default=None,
    help='The command to run',
)
@click.option(
    '--org-id', '-o',
    required=True,
    default=None,
    help='The target org id',
)
def get_policy(name, org_id) -> None:
    print(json.dumps(
        ranger_service.get_policy("{}_{}".format(org_id, name)),
        indent=2,
    ))


@click.command()
def setup_port_forwards() -> None:
    processes = forward.create_forwards()
    time.sleep(2)
    input("Press Enter to terminate...")
    for process in processes:
        process.terminate()


@click.command()
def run_services() -> None:
    processes = services.run_services()
    time.sleep(2)
    input("Press Enter to terminate...")
    for process in processes:
        process.terminate()        


@click.group()
def cli() -> None:
    pass


cli.add_command(get_policy)
cli.add_command(get_all_roles)
cli.add_command(get_all_users)
cli.add_command(create_default_roles)
cli.add_command(create_default_users)
cli.add_command(create_default_bucket)
cli.add_command(create_trino_ranger_service)
cli.add_command(show_tables)
cli.add_command(execute)
cli.add_command(execute_sql)
cli.add_command(get_policy)
cli.add_command(setup_port_forwards)
cli.add_command(run_services)


if __name__ == '__main__':
    cli()
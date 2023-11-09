from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests

from query_cli.orgdata.entities import CreateOrgModel
from query_cli.orgdata.entities import DescribeTableModel
from query_cli.orgdata.entities import MultiDescribeTableModel
from query_cli.orgdata.entities import QueryHistoryModel
from query_cli.orgdata.entities import StreamModel
from query_cli.orgdata.entities import TaskModel
from query_cli.orgdata.entities import UserModel
from query_cli.orgdata.entities import WarehouseModel


ORGDATA_URL = "http://localhost:7784"


def get_all_warehouses() -> Dict[str, Any]:
    r = requests.get(
        "{}/private_api/v1/warehouses".format(ORGDATA_URL),
        headers={
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def create_warehouse(warehouse: WarehouseModel) -> None:
    r = requests.post(
        "{}/api/v1/warehouse".format(ORGDATA_URL),
        headers={
            "Accept": "application/json",
        },
        json=vars(warehouse),
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")


def get_warehouse(org_id: str, warehouse_name: str) -> Optional[Dict[str, Any]]:
    r = requests.get(
        "{}/api/v1/warehouse/{}/{}".format(
            ORGDATA_URL,
            org_id,
            warehouse_name,
        ),
        headers={
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def delete_warehouse(org_id: str, warehouse_name: str) -> None:
    r = requests.delete(
        "{}/api/v1/warehouse/{}/{}".format(
            ORGDATA_URL,
            org_id,
            warehouse_name,
        ),
        headers={
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")


def get_all_streams() -> Dict[str, Any]:
    r = requests.get(
        "{}/private_api/v1/streams".format(ORGDATA_URL),
        headers={
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def create_stream(stream: StreamModel) -> None:
    r = requests.post(
        "{}/api/v1/stream".format(ORGDATA_URL),
        headers={
            "Accept": "application/json",
        },
        json=vars(stream),
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def drop_stream(org_id: str, stream_name: str) -> None:
    r = requests.delete(
        "{}/api/v1/stream/{}/{}".format(ORGDATA_URL, org_id, stream_name),
        headers={
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def get_all_tasks() -> Dict[str, Any]:
    r = requests.get(
        "{}/private_api/v1/tasks".format(ORGDATA_URL),
        headers={
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def create_task(task: TaskModel) -> None:
    r = requests.post(
        "{}/api/v1/task".format(ORGDATA_URL),
        headers={
            "Accept": "application/json",
        },
        json=vars(task),
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def put_describe_table(columns: List[DescribeTableModel]) -> None:
    put_val = [vars(column) for column in columns]
    r = requests.post(
        "{}/api/v1/describe_table".format(ORGDATA_URL),
        headers={
            "ContentType": "application/json",
            "Accept": "application/json",
        },
        json=put_val,
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def get_describe_table(org_id: str, table_name: str) -> MultiDescribeTableModel:
    r = requests.get(
        "{}/api/v1/describe_table/{}/{}".format(
            ORGDATA_URL,
            org_id,
            table_name,
        ),
        headers={
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")
    return MultiDescribeTableModel.from_json(r.json())


def drop_describe_table(org_id: str, table_name: str) -> None:
    r = requests.delete(
        "{}/api/v1/describe_table/{}/{}".format(
            ORGDATA_URL,
            org_id,
            table_name,
        ),
        headers={
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")


def put_query_history(query: QueryHistoryModel) -> None:
    query.serialize_internal_status()
    r = requests.post(
        "{}/api/v1/query_history".format(ORGDATA_URL),
        headers={
            "Accept": "application/json",
        },
        json=query.as_dict(),
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")


def get_query_history(org_id: str, query_id: str) -> Optional[QueryHistoryModel]:
    r = requests.get(
        "{}/api/v1/query_history/{}/{}".format(ORGDATA_URL, org_id, query_id),
        headers={
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")

    response_body = r.json()
    if len(response_body) == 0:
        return None

    model = QueryHistoryModel()
    model.id = response_body["_id"]
    model.org_id = response_body["_org_id"]
    model.body = response_body["_body"]
    model.occurred_at = response_body["_occurred_at"]
    model.status = response_body["_status"]
    model.internal_status = response_body["_internal_status"]
    return model


def create_org(model: CreateOrgModel) -> bool:
    r = requests.post(
        "{}/api/v1/create_org".format(ORGDATA_URL),
        headers={
            "Accept": "application/json",
        },
        json=vars(model),
    )
    if r.status_code != 200:
        print(r.text)
        return False

    return True


def validate_user(email: str, password: str) -> Optional[UserModel]:
    r = requests.get(
        "{}/api/v1/validate_org_user/{}/{}".format(ORGDATA_URL, email, password),
        headers={
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")

    r_json = r.json()
    if "user" in r_json and r_json["user"] is not None:
        return UserModel.from_json(r_json["user"])
    else:
        return None

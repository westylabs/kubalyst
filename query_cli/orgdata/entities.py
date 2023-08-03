import json
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


class WarehouseModel:
    org_id: str
    name: str
    size: str
    type: str
    auto_suspend: bool
    auto_resume: bool
    initially_suspended: bool
    comment: str


class StreamModel:
    org_id: str
    name: str
    target_table: str


class TaskModel:
    org_id: str
    name: str
    warehouse: str
    schedule: str
    when: str
    as_statement: str
    status: str


class DescribeTableModel:
    @staticmethod
    def from_json(input_dict: Dict[str, Any]) -> "DescribeTableModel":
        return DescribeTableModel(
            org_id=input_dict["org_id"],
            table_name=input_dict["table_name"],
            column_name=input_dict["column_name"],
            type=input_dict["type"],
            kind=input_dict["kind"],
            null_question=input_dict["null_question"],
            default=input_dict["default"],
            primary_key=input_dict["primary_key"],
            unique_key=input_dict["unique_key"],
            check=input_dict["check"],
            expression=input_dict["expression"],
            comment=input_dict["comment"],
            policy_name=input_dict["policy_name"],
        )

    def __init__(
        self,
        org_id: str,
        table_name: str,
        column_name: str,
        type: str,
        kind: str,
        null_question: bool,
        default: Optional[str],
        primary_key: bool,
        unique_key: bool,
        check: Optional[str],
        expression: Optional[str],
        comment: Optional[str],
        policy_name: Optional[str],
    ) -> None:
        self.org_id = org_id
        self.table_name = table_name
        self.column_name = column_name
        self.type = type
        self.kind = kind
        self.null_question = null_question
        self.default = default
        self.primary_key = primary_key
        self.unique_key = unique_key
        self.check = check
        self.expression = expression
        self.comment = comment
        self.policy_name = policy_name


class MultiDescribeTableModel:
    @staticmethod
    def from_json(input_dict: Dict[str, Any]) -> "MultiDescribeTableModel":
        return MultiDescribeTableModel(
            columns=[
                DescribeTableModel.from_json(model_dict)
                for model_dict in input_dict["columns"]
            ]
        )

    def __init__(self, columns: List[DescribeTableModel]) -> None:
        self.columns = columns

    def vars(self) -> Dict[str, Any]:
        return {"columns": [vars(column) for column in self.columns]}

    def column(self, name: str) -> DescribeTableModel:
        column = self.try_column(name)
        if column is None:
            raise ValueError("No match found")
        return column

    def try_column(self, name: str) -> Optional[DescribeTableModel]:
        for column in self.columns:
            if column.column_name.lower() == name.lower():
                return column
        return None


class InternalStatus:
    def __init__(
        self,
        trino_status: Optional[str],
        trino_next_uri: Optional[str],
        trino_error_message: Optional[str],
    ) -> None:
        self.trino_status = trino_status
        self.trino_next_uri = trino_next_uri
        self.trino_error_message = trino_error_message


class QueryHistoryModel:
    id: str
    org_id: str
    body: str
    occurred_at: str
    status: str
    internal_status: str

    def __init__(self) -> None:
        self._parsed_internal_status: Optional[InternalStatus] = None

    def parsed_internal_status(self) -> InternalStatus:
        if self._parsed_internal_status is None:
            self._parsed_internal_status = InternalStatus(
                **json.loads(self.internal_status)
            )
        return self._parsed_internal_status

    def set_default_internal_status(self) -> None:
        self._parsed_internal_status = InternalStatus(None, None, None)

    def serialize_internal_status(self) -> None:
        if self._parsed_internal_status is not None:
            self.internal_status = json.dumps(vars(self._parsed_internal_status))

    def as_dict(self) -> Dict[str, Any]:
        self_vars = dict(vars(self))
        for key in list(self_vars.keys()):
            if key.startswith("_"):
                del self_vars[key]
        return self_vars


class CreateOrgModel:
    def __init__(
        self,
        org_name: str,
        user_name: str,
        user_email: str,
        user_password: str,
    ) -> None:
        self.org_name = org_name
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = user_password


class UserModel:
    @staticmethod
    def from_json(value: Dict[str, Any]) -> "UserModel":
        return UserModel(**value)

    def __init__(
        self,
        user_id: str,
        account_id: str,
        org_id: str,
        name: str,
        email: str,
        password: Optional[str],
        state: str,
        created_date: str,
    ) -> None:
        self.user_id = user_id
        self.account_id = account_id
        self.org_id = org_id
        self.name = name
        self.email = email
        self.password = password
        self.state = state
        self.created_date = datetime.fromisoformat(created_date)

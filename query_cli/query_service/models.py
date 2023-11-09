from typing import Optional


class StatementsModel:
    statement: Optional[str]
    timeout: Optional[int]
    database: Optional[str]
    schema_: Optional[str]
    warehouse: Optional[str]
    role: Optional[str]

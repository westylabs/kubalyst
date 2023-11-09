from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from query_cli.ranger import service as ranger_service


SYSADMIN_NAME_TEMPLATE = "{}_SYSADMIN"
SYSADMIN_ROLE_TEMPLATE = {
    "createdByUser": "admin",
    "name": SYSADMIN_NAME_TEMPLATE,
    "description": "Sysadmin role for {}",
    "isEnabled": True,
}

SECURITYADMIN_TEMPLATE = "{}_SECURITYADMIN"
SECURITYADMIN_ROLE_TEMPLATE = {
    "createdByUser": "admin",
    "name": SECURITYADMIN_TEMPLATE,
    "description": "Security admin role for {}",
    "isEnabled": True,
}


ACCOUNTADMIN_TEMPLATE = "{}_ACCOUNTADMIN"
ACCOUNTADMIN_ROLE_TEMPLATE = {
    "createdByUser": "admin",
    "name": ACCOUNTADMIN_TEMPLATE,
    "description": "Account admin role for {}",
    "isEnabled": True,
}


def _sysadmin_role_config(org_id: str) -> Dict[str, Any]:
    final_val = dict(SYSADMIN_ROLE_TEMPLATE)
    final_val["name"] = final_val["name"].format(org_id)  # type: ignore
    final_val["description"] = final_val["description"].format(org_id)  # type: ignore
    return final_val


def sysadmin_role_name(org_id: str) -> str:
    return SYSADMIN_NAME_TEMPLATE.format(org_id)


def _securityadmin_role_config(org_id: str) -> Dict[str, Any]:
    final_val = dict(SECURITYADMIN_ROLE_TEMPLATE)
    final_val["name"] = final_val["name"].format(org_id)  # type: ignore
    final_val["description"] = final_val["description"].format(org_id)  # type: ignore
    return final_val


def securityadmin_role_name(org_id: str) -> str:
    return SECURITYADMIN_TEMPLATE.format(org_id)


def _accountadmin_role_config(org_id: str) -> Dict[str, Any]:
    final_val = dict(ACCOUNTADMIN_ROLE_TEMPLATE)
    final_val["name"] = final_val["name"].format(org_id)  # type: ignore
    final_val["description"] = final_val["description"].format(org_id)  # type: ignore
    return final_val


def accountadmin_role_name(org_id: str) -> str:
    return ACCOUNTADMIN_TEMPLATE.format(org_id)


def create_default_roles(org_id: str) -> None:
    existing_roles = get_roles(org_id)
    sysadmin_role = _sysadmin_role_config(org_id)
    securityadmin_role = _securityadmin_role_config(org_id)
    accountadmin_role = _accountadmin_role_config(org_id)
    if sysadmin_role["name"] not in existing_roles:
        ranger_service.create_role(role_config=sysadmin_role)
    if securityadmin_role["name"] not in existing_roles:
        ranger_service.create_role(role_config=securityadmin_role)
    if accountadmin_role["name"] not in existing_roles:
        ranger_service.create_role(role_config=accountadmin_role)


def create_role(
    name: str,
    created_by: str,
    comment: Optional[str],
) -> None:
    role_config = {
        "createdByUser": created_by,
        "name": name,
        "description": comment,
        "isEnabled": True,
    }
    ranger_service.create_role(role_config=role_config)


def get_all_roles() -> List[str]:
    return [entry["name"] for entry in ranger_service.get_roles()]


def get_roles(org_id: str) -> List[str]:
    return [role for role in get_all_roles() if role.startswith(org_id)]

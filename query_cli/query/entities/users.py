from typing import Dict, Any, List


from query.ranger import service as ranger_service


SYSADMIN_NAME_TEMPLATE = "{}_SYSADMIN"
SYSADMIN_CONFIG_TEMPLATE: Dict[str, Any] = {
    "loginId": SYSADMIN_NAME_TEMPLATE,
    "name": SYSADMIN_NAME_TEMPLATE,
    "status": 1,
    "isVisible": 1,
    "password": "admin123",
    "emailAddress": None,
    "firstName": "SysAdmin",
    "lastName": "{}",
    "publicScreenName": "{} Sysadmin",
    "notes": "Sysdamin for {}",
    "userSource": 0,
}


def _sysadmin_user_config(org_id: str) -> Dict[str, Any]:
    final_val = dict(SYSADMIN_CONFIG_TEMPLATE)
    final_val['loginId'] = final_val['loginId'].format(org_id)  # type: ignore
    final_val['name'] = final_val['name'].format(org_id)  # type: ignore
    final_val['lastName'] = final_val['lastName'].format(org_id)  # type: ignore
    final_val['publicScreenName'] = final_val['publicScreenName'].format(org_id)  # type: ignore
    return final_val


def create_default_users(org_id: str) -> None:
    sysadmin_user_config = _sysadmin_user_config(org_id)
    all_org_users = ranger_service.get_users(org_id)
    if sysadmin_user_config['loginId'] not in all_org_users:
        ranger_service.create_user(sysadmin_user_config)


def get_all_users() -> List[str]:
    response = ranger_service.get_all_users()

    return [user['loginId'] for user in response]


def get_users(org_id: str) -> List[str]:
    return [user for user in get_all_users() if user.startswith(org_id)]

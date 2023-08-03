from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth

RANGER_ADMIN_URL = "http://localhost:6080/"


def get_roles() -> List[Dict[str, Any]]:
    r = requests.get(
        url="{}service/public/v2/api/roles".format(RANGER_ADMIN_URL),
        auth=HTTPBasicAuth("admin", "Rangeradmin1"),
    )
    if r.status_code != 200:
        print("status code = {}".format(r.status_code))
        print(r.text)
        raise ValueError("Nope")

    return r.json()


def create_role(role_config: Dict[str, Any]) -> Dict[str, Any]:
    r = requests.post(
        url="{}service/public/v2/api/roles/".format(RANGER_ADMIN_URL),
        auth=HTTPBasicAuth("admin", "Rangeradmin1"),
        json=role_config,
    )

    if r.status_code != 200:
        print("status code = {}".format(r.status_code))
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def grant_role(role: str, target_role: str) -> Dict[str, Any]:
    r = requests.put(
        url="{}service/public/v2/api/roles/grant/trino".format(RANGER_ADMIN_URL),
        auth=HTTPBasicAuth("admin", "Rangeradmin1"),
        json={
            "roles": [role],
            "targetRoles": [target_role],
        },
    )

    if r.status_code != 200:
        print("status code = {}".format(r.status_code))
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def get_all_users() -> List[Dict[str, Any]]:
    r = requests.get(
        url="{}service/users".format(RANGER_ADMIN_URL),
        auth=HTTPBasicAuth("admin", "Rangeradmin1"),
        headers={"Accept": "application/json"},
    )
    if r.status_code != 200:
        print("status code = {}".format(r.status_code))
        print(r.text)
        raise ValueError("Nope")
    retval = r.json()["vXPortalUsers"]
    return retval


def get_users(org_id: str) -> List[str]:
    return [
        entry["loginId"]
        for entry in get_all_users()
        if entry["loginId"].startswith(org_id)
    ]


def _create_user_worker(
    url: str, user_config: Dict[str, Any]
) -> Optional[List[Dict[str, Any]]]:
    r = requests.post(
        url="{}{}".format(RANGER_ADMIN_URL, url),
        auth=HTTPBasicAuth("admin", "Rangeradmin1"),
        json=user_config,
        headers={
            "Accept": "application/json",
            "Content-type": "application/json",
        },
    )

    if r.status_code != 200:
        print("status code = {}".format(r.status_code))
        print(r.text)
        return None
    return r.json()


def create_user(user_config: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    return _create_user_worker("service/users", user_config)


def get_policy(id: str) -> Dict[str, Any]:
    r = requests.get(
        "{}service/public/v2/api/policy?policyName={}".format(RANGER_ADMIN_URL, id),
        auth=HTTPBasicAuth("admin", "Rangeradmin1"),
        headers={
            "Accept": "application/json",
        },
    )
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")
    return r.json()


def create_policy(
    policy: Dict[str, Any],
) -> None:
    r = requests.post(
        "{}service/public/v2/api/policy".format(RANGER_ADMIN_URL),
        auth=HTTPBasicAuth("admin", "Rangeradmin1"),
        json=policy,
    )
    print(f"Status Code: {r.status_code}, Response: {r.json()}")
    if r.status_code != 200:
        print(r.text)
        raise ValueError("Nope")

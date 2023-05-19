from typing import Optional

from apache_ranger.model.ranger_service import RangerService
from apache_ranger.client.ranger_client import RangerClient
from apache_ranger.model.ranger_policy import RangerPolicy


RANGER_URL  = 'http://localhost:6080'
RANGER_AUTH = ('admin', 'Rangeradmin1')
RANGER_CLIENT = RangerClient(RANGER_URL, RANGER_AUTH)



def get_service(service_name: str) -> Optional[RangerService]:
    return RANGER_CLIENT.get_service(serviceName=service_name)


def create_trino_service() -> RangerService:
    service  = RangerService()
    service.name = 'trino'
    service.type = 'trino'
    service.configs = {
        'username':'admin', 
        'jdbc.driverClassName': 'io.trino.jdbc.TrinoDriver', 
        'jdbc.url': 'jdbc:trino://trino:8080', 
    }

    print('Creating service: name=' + service.name)

    return RANGER_CLIENT.create_service(service)


def create_policy(policy: RangerPolicy) -> Optional[RangerPolicy]:
    return RANGER_CLIENT.create_policy(policy)


def update_policy(policy: RangerPolicy) -> Optional[RangerPolicy]:
    return RANGER_CLIENT.update_policy("trino", policy.name, policy)


def get_policy(policy_name: str) -> Optional[RangerPolicy]:
    return RANGER_CLIENT.get_policy("trino", policy_name)

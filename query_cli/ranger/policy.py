from typing import Dict
from typing import List
from typing import Optional

from apache_ranger.model.ranger_policy import RangerPolicy
from apache_ranger.model.ranger_policy import RangerPolicyItem
from apache_ranger.model.ranger_policy import RangerPolicyItemAccess
from apache_ranger.model.ranger_policy import RangerPolicyResource

from query_cli.ranger import service2


class AccessBuilder:
    def __init__(
        self,
        users: List[str] = [],
        roles: List[str] = [],
        groups: List[str] = [],
    ) -> None:
        self._users = users
        self._roles = roles
        self._groups = groups
        self._accesses: List[RangerPolicyItemAccess] = []

    def usage(self) -> "AccessBuilder":
        self._accesses.append(RangerPolicyItemAccess({"type": "select"}))
        return self

    def access(self, rights: List[str]) -> "AccessBuilder":
        for right in rights:
            self._accesses.append(RangerPolicyItemAccess({"type": right}))
        return self

    def _build(self, ranger_policy: RangerPolicy) -> None:
        policy_item = RangerPolicyItem()
        if len(self._users) > 0:
            policy_item.users = self._users
        if len(self._roles) > 0:
            policy_item.roles = self._roles
        if len(self._groups) > 0:
            policy_item.groups = self._groups
        policy_item.accesses = self._accesses
        if ranger_policy.policyItems is None:
            ranger_policy.policyItems = []
        ranger_policy.policyItems.append(policy_item)


class PolicyBuilder:
    def __init__(
        self,
    ) -> None:
        self._description: Optional[str] = None
        self._access_builders: List[AccessBuilder] = []
        self._resources: List[Dict[str, RangerPolicyResource]] = []

    def description(self, description: str) -> "PolicyBuilder":
        self._description = description
        return self

    def database_resource(self, database_name: str) -> "PolicyBuilder":
        self._resources.append(
            {
                "catalog": RangerPolicyResource({"values": ["delta"]}),
                "schema": RangerPolicyResource({"values": [database_name]}),
                "table": RangerPolicyResource({"values": ["*"]}),
            }
        )
        return self

    def schema_resource(self, database_name: str, schema_name: str) -> "PolicyBuilder":
        self._resources.append(
            {
                "catalog": RangerPolicyResource({"values": ["delta"]}),
                "schema": RangerPolicyResource(
                    {"values": ["{}_{}".format(database_name, schema_name)]}
                ),
                "table": RangerPolicyResource({"values": ["*"]}),
            }
        )
        return self

    def all_tables_resource(
        self, database_name: str, schema_name: str
    ) -> "PolicyBuilder":
        return self.schema_resource(database_name, schema_name)

    def roles(self, roles: List[str]) -> AccessBuilder:
        access_builder = AccessBuilder(
            roles=roles,
        )
        self._access_builders.append(access_builder)
        return access_builder

    def _policy_name(self) -> str:
        resource_strs = []
        for resource in self._resources:
            resource_strs.append(
                ",".join(
                    [
                        "{}={}".format(key, ",".join(value.values))
                        for key, value in resource.items()
                    ]
                )
            )

        return "|".join(resource_strs)

    def create_or_update(self) -> Optional[RangerPolicy]:
        policy_name = self._policy_name()
        ranger_policy = service2.get_policy(policy_name)
        if ranger_policy is None:
            create = True
            ranger_policy = RangerPolicy()
            ranger_policy.service = "trino"
            ranger_policy.name = policy_name
            for resource in self._resources:
                ranger_policy.add_resource(resource)
        else:
            create = False

        ranger_policy.description = self._description

        for access_builder in self._access_builders:
            access_builder._build(ranger_policy)

        if create:
            return service2.create_policy(ranger_policy)
        else:
            return service2.update_policy(ranger_policy)

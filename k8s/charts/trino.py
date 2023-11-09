import os
from typing import Literal

from cdk8s import ApiObjectMetadata
from cdk8s import Chart
from cdk8s import Duration
from cdk8s import Size
from cdk8s_plus_27 import ConfigMap
from cdk8s_plus_27 import ContainerProps
from cdk8s_plus_27 import ContainerSecurityContextProps
from cdk8s_plus_27 import Cpu
from cdk8s_plus_27 import CpuResources
from cdk8s_plus_27 import Deployment
from cdk8s_plus_27 import DeploymentStrategy
from cdk8s_plus_27 import EnvValue
from cdk8s_plus_27 import ImagePullPolicy
from cdk8s_plus_27 import LabelSelector
from cdk8s_plus_27 import MemoryResources
from cdk8s_plus_27 import PersistentVolumeAccessMode
from cdk8s_plus_27 import PersistentVolumeClaim
from cdk8s_plus_27 import Pod
from cdk8s_plus_27 import PodSecurityContextProps
from cdk8s_plus_27 import Probe
from cdk8s_plus_27 import Protocol
from cdk8s_plus_27 import RestartPolicy
from cdk8s_plus_27 import Service
from cdk8s_plus_27 import ServiceType
from cdk8s_plus_27 import StatefulSet
from cdk8s_plus_27 import Volume
from cdk8s_plus_27 import VolumeMount
from constructs import Construct

USER = os.getenv("USER")
TRINO_IMAGE = f"{USER}/trino-ranger:latest"
IMAGE_PULL_POLICY = ImagePullPolicy.IF_NOT_PRESENT

# TODO: produce yaml in dirs by environment and user (e.g. dist/local/bill)
# TODO: develop environment-specific config solution
# TODO: set memory settings and image different by environment
# TODO: a lot of funny business required to get metadata and labels like app: trino-coordinator
# set properly. Experiment to see if these can be removed and if k8s still binds properly with the
# built-in labels


class Trino(Chart):
    AWS_ENV_VARIABLES: dict[str, EnvValue] = {
        "AWS_ACCESS_KEY_ID": EnvValue.from_value("minio_root_user"),
        "AWS_SECRET_ACCESS_KEY": EnvValue.from_value("minio_root_password123"),
    }

    PORT = 8080

    health_probe = Probe.from_http_get(
        path="/v1/info",
        port=PORT,
        failure_threshold=5,
        period_seconds=Duration.seconds(20),
    )

    def __init__(self, scope: Construct, config_map: ConfigMap):
        super().__init__(scope, "trino")

        config_volume = Volume.from_config_map(
            self, "trino-cfg-vol", config_map, name="trino-cfg-vol"
        )

        coordinator_deployment = self._create_coordinator_deployment(
            config_volume=config_volume,
            selector_label={"app": "trino-coordinator"},
        )
        self._create_coordinator().select(selector=coordinator_deployment)
        self._create_workers(config_volume=config_volume)
        self._create_cli()

    def _create_coordinator(self) -> Service:
        coordinator = Service(
            self,
            "trino",
            type=ServiceType.NODE_PORT,
            metadata=ApiObjectMetadata(name="trino"),
        )
        coordinator.bind(port=self.PORT, target_port=self.PORT, protocol=Protocol.TCP)
        return coordinator

    def _create_coordinator_deployment(
        self, config_volume: Volume, selector_label: dict[str, str]
    ) -> Deployment:
        coordinator_deployment = Deployment(
            self,
            "trino-coordinator",
            metadata=ApiObjectMetadata(name="trino-coordinator"),
            replicas=1,
            strategy=DeploymentStrategy.recreate(),
            volumes=[config_volume],
            pod_metadata=ApiObjectMetadata(labels=selector_label),
            select=False,
            containers=[
                ContainerProps(
                    name="trino-coordinator",
                    image=TRINO_IMAGE,
                    port=self.PORT,
                    env_variables=Trino.AWS_ENV_VARIABLES,
                    resources={
                        "cpu": CpuResources(limit=Cpu.units(1)),
                        "memory": MemoryResources(limit=Size.gibibytes(4)),
                    },
                    image_pull_policy=IMAGE_PULL_POLICY,
                    security_context=ContainerSecurityContextProps(
                        ensure_non_root=False, read_only_root_filesystem=False
                    ),
                    startup=None,
                    volume_mounts=Trino._create_config_volume_mounts(
                        config_volume, "coordinator"
                    ),
                    readiness=Probe.from_command(
                        command=[
                            "bin/bash",
                            "-c",
                            f"[ $(curl -s http://localhost:{self.PORT}/v1/status | jq .processors) -gt 0 ]",
                        ],
                        initial_delay_seconds=Duration.seconds(10),
                        period_seconds=Duration.seconds(10),
                        failure_threshold=5,
                    ),
                    liveness=self.health_probe,
                )
            ],
        )
        coordinator_deployment.select(LabelSelector.of(labels=selector_label))
        return coordinator_deployment

    def _create_workers(self, config_volume: Volume) -> None:
        name = "trino-worker"
        selector_label = {"app": name}

        tmp_data_volume_claim = Volume.from_persistent_volume_claim(
            self,
            id="trino-tmp-data",
            claim=PersistentVolumeClaim(
                self,
                "trino-pv-claim",
                metadata={"name": "trino-pv-claim"},
                storage_class_name="standard",
                access_modes=[PersistentVolumeAccessMode.READ_WRITE_ONCE],
                storage=Size.gibibytes(1),
            ),
            name="trino-tmp-data",
        )

        # TODO: I don't think we need a persistent volume, but if we do, hostPath is not supported
        # in cdk8s+ so we'd need to inject it using the escape hatch:
        # https://cdk8s.io/docs/latest/basics/escape-hatches/#patching-api-objects-behind-higher-level-apis
        #   hostPath:
        #     path: "{REPO_HOME}/mnt/trino"
        # pv = PersistentVolume(
        #     self,
        #     id="trino-pv-volume",
        #     metadata=ApiObjectMetadata(name="trino-pv-volume", labels={"type": "local"}),
        #     access_modes=[PersistentVolumeAccessMode.READ_WRITE_ONCE],
        #     storage=Size.gibibytes(4),
        #     storage_class_name="manual",
        # )

        worker = StatefulSet(
            self,
            name,
            metadata=ApiObjectMetadata(name=name),
            replicas=1,
            volumes=[config_volume, tmp_data_volume_claim],
            pod_metadata=ApiObjectMetadata(labels=selector_label),
            security_context=PodSecurityContextProps(fs_group=1000),
            select=False,
            containers=[
                ContainerProps(
                    name="trino",
                    image=TRINO_IMAGE,
                    port=self.PORT,
                    env_variables=Trino.AWS_ENV_VARIABLES,
                    resources={
                        "cpu": CpuResources(limit=Cpu.units(1)),
                        "memory": MemoryResources(limit=Size.gibibytes(2)),
                    },
                    image_pull_policy=IMAGE_PULL_POLICY,
                    startup=None,
                    volume_mounts=Trino._create_config_volume_mounts(
                        config_volume, "worker"
                    ),
                    security_context=ContainerSecurityContextProps(
                        ensure_non_root=False, read_only_root_filesystem=False
                    ),
                    readiness=self.health_probe,
                    liveness=self.health_probe,
                )
            ],
        )
        worker.select(LabelSelector.of(labels=selector_label))

    def _create_cli(self):
        name = "trino-cli"
        Pod(
            self,
            name,
            metadata=ApiObjectMetadata(name=name),
            restart_policy=RestartPolicy.ALWAYS,
            containers=[
                ContainerProps(
                    name=name,
                    image=TRINO_IMAGE,
                    command=["tail", "-f", "/dev/null"],
                    image_pull_policy=IMAGE_PULL_POLICY,
                    security_context=ContainerSecurityContextProps(
                        ensure_non_root=False,
                        read_only_root_filesystem=False,
                    ),
                ),
            ],
        )

    @staticmethod
    def _create_config_volume_mounts(
        config_volume: Volume, node_type: Literal["coordinator", "worker"]
    ) -> list[VolumeMount]:
        volume_mounts: list[VolumeMount] = []

        def add_mount(sub_path: str, path: str):
            volume_mounts.append(
                VolumeMount(volume=config_volume, path=path, sub_path=sub_path)
            )

        add_mount("jvm.config", "/etc/trino/jvm.config")
        add_mount(f"config.properties.{node_type}", "/etc/trino/config.properties")
        add_mount("node.properties", "/etc/trino/node.properties")
        add_mount("hive.properties", "/etc/trino/catalog/hive.properties")
        add_mount("iceberg.properties", "/etc/trino/catalog/iceberg.properties")
        add_mount("mysql.properties", "/etc/trino/catalog/mysql.properties")

        return volume_mounts

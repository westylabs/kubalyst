import os
from typing import Literal

from cdk8s_plus_27 import (
    ImagePullPolicy,
    MemoryResources,
    CpuResources,
    Cpu,
    EnvValue,
    Deployment,
    ServiceType,
    Service,
    Protocol,
    ConfigMap,
    Volume,
    VolumeMount,
    DeploymentStrategy,
    LabelSelector,
    StatefulSet,
    ContainerProps,
    PodSecurityContextProps,
    ContainerSecurityContextProps,
    PersistentVolumeAccessMode,
    PersistentVolumeClaim,
    Pod,
    RestartPolicy,
)
from constructs import Construct
from cdk8s import Chart, Size, ApiObjectMetadata

USER = os.getenv("USER")
TRINO_IMAGE = f"{USER}/trino-ranger:latest"
IMAGE_PULL_POLICY = ImagePullPolicy.IF_NOT_PRESENT

# TODO: test with hive metastore
# TODO: produce yaml in dirs by environment and user (e.g. dist/local/bill, dist/local/gfee)
# TODO: develop environment-specific config solution
# TODO: set memory settings and image different by environment
# TODO: why is ranger causing an issue?
# TODO: startup, readiness, liveness probes
# TODO: a lot of funny business required to get metadata and labels like app: trino-coordinator
# set properly. Experiment to see if these can be removed and if k8s still binds properly with the
# built-in labels


class Trino(Chart):
    AWS_ENV_VARIABLES: dict[str, EnvValue] = {
        "AWS_ACCESS_KEY_ID": EnvValue.from_value("minio_root_user"),
        "AWS_SECRET_ACCESS_KEY": EnvValue.from_value("minio_root_password123"),
    }

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
        coordinator.bind(port=8080, target_port=8080, protocol=Protocol.TCP)
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
                    port=8080,
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

        # TODO: verify if we need a persistent volume or not. If we do, hostPath is not supported
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
                    port=8080,
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

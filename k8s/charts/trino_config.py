from textwrap import dedent

from cdk8s_plus_27 import ConfigMap
from constructs import Construct
from cdk8s import Chart


class TrinoConfig(Chart):
    def __init__(self, scope: Construct):
        super().__init__(scope, "trino-cfgs")
        self.config_map = ConfigMap(
            self,
            "trino-configs",
            metadata={"name": "trino-configs"},
            immutable=True,
            data={
                "jvm.config": dedent(
                    """\
                    -server
                    -Xmx16G
                    -XX:-UseBiasedLocking
                    -XX:+UseG1GC
                    -XX:G1HeapRegionSize=32M
                    -XX:+ExplicitGCInvokesConcurrent
                    -XX:+ExitOnOutOfMemoryError
                    -XX:+UseGCOverheadLimit
                    -XX:+HeapDumpOnOutOfMemoryError
                    -XX:ReservedCodeCacheSize=512M
                    -Djdk.attach.allowAttachSelf=true
                    -Djdk.nio.maxCachedBufferSize=2000000
                    """
                ),
                "config.properties.coordinator": dedent(
                    """\
                    coordinator=true
                    node-scheduler.include-coordinator=false
                    http-server.http.port=8080
                    query.max-memory=200GB
                    query.max-memory-per-node=8GB
                    query.max-stage-count=200
                    task.writer-count=4
                    discovery.uri=http://trino:8080
                    """
                ),
                "config.properties.worker": dedent(
                    """\
                    coordinator=false
                    http-server.http.port=8080
                    query.max-memory=200GB
                    query.max-memory-per-node=10GB
                    query.max-stage-count=200
                    task.writer-count=4
                    discovery.uri=http://trino:8080
                    """
                ),
                "node.properties": dedent(
                    """\
                    node.environment=test
                    spiller-spill-path=/tmp
                    max-spill-per-node=4TB
                    query-max-spill-per-node=1TB
                    """
                ),
                "hive.properties": dedent(
                    """\
                    connector.name=hive
                    hive.metastore.uri=thrift://hive-metastore:9083
                    hive.allow-drop-table=true
                    hive.s3.endpoint=http://minio:9000
                    hive.s3.aws-access-key=minio_root_user
                    hive.s3.aws-secret-key=minio_root_password123
                    hive.s3.path-style-access=true
                    hive.s3.ssl.enabled=false
                    hive.s3.max-connections=100
                    """
                ),
                "iceberg.properties": dedent(
                    """\
                    connector.name=iceberg
                    hive.metastore.uri=thrift://hive-metastore:9083
                    hive.s3.endpoint=http://minio:9000
                    hive.s3.aws-access-key=minio_root_user
                    hive.s3.aws-secret-key=minio_root_password123
                    hive.s3.path-style-access=true
                    hive.s3.ssl.enabled=false
                    hive.s3.max-connections=100
                    """
                ),
                "mysql.properties": dedent(
                    """\
                    connector.name=mysql
                    connection-url=jdbc:mysql://metastore-db.default.svc.cluster.local:3306
                    connection-user=root
                    connection-password=mypass
                    """
                ),
            },
        )

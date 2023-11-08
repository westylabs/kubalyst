#!/bin/sh

export HADOOP_HOME=/opt/hadoop-3.2.0
export HADOOP_CLASSPATH=${HADOOP_HOME}/share/hadoop/tools/lib/aws-java-sdk-bundle-1.11.375.jar:${HADOOP_HOME}/share/hadoop/tools/lib/hadoop-aws-3.2.0.jar
export JAVA_HOME=/usr/local/openjdk-8

# Make sure mariadb is ready
# MAX_TRIES=8
#CURRENT_TRY=1
#SLEEP_BETWEEN_TRY=4
#until [ "$(telnet mariadb 3306 | sed -n 2p)" = "Connected to mariadb." ] || [ "$CURRENT_TRY" -gt "$MAX_TRIES" ]; do
#    echo "Waiting for mariadb server..."
#    sleep "$SLEEP_BETWEEN_TRY"
#    CURRENT_TRY=$((CURRENT_TRY + 1))
#done

#if [ "$CURRENT_TRY" -gt "$MAX_TRIES" ]; then
#  echo "WARNING: Timeout when waiting for mariadb."
#fi

# Check if schema exists
/opt/apache-hive-metastore-3.0.0-bin/bin/schematool -dbType mysql -info

if [ $? -ne 0 ]; then
  echo "Get schema info failed. Probably not initialized. Initializing..."
  /opt/apache-hive-metastore-3.0.0-bin/bin/schematool -dbType mysql -initSchema -verbose
else
  echo "Schema already initialized."
fi

/opt/apache-hive-metastore-3.0.0-bin/bin/start-metastore

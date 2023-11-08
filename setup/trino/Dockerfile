# See this trino/ranger compatability chart:
# https://github.com/aakashnand/trino-ranger-demo/releases
FROM trinodb/trino:406
ARG RANGER_VERSION=3.0.0-SNAPSHOT

USER root
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-add-repository -y https://packages.debian.org/bookworm/jq && \
    apt-get install -y jq

COPY --chown=trino:trino ranger-${RANGER_VERSION}-trino-plugin/ /root/ranger-${RANGER_VERSION}-trino-plugin/

# Snowflake plugin now needs to be compiled with jdk 11 comppatability to work
COPY --chown=trino:trino plugins/snowflake-compat /usr/lib/trino/plugin/snowflake-compat

RUN /root/ranger-${RANGER_VERSION}-trino-plugin/enable-trino-plugin.sh

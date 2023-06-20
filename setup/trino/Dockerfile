FROM trinodb/trino:409

COPY --chown=trino:trino ranger-2.3.0-trino-plugin/ /root/ranger-2.3.0-trino-plugin/
COPY --chown=trino:trino plugins/snowflake-compat /usr/lib/trino/plugin/snowflake-compat

USER root
RUN /root/ranger-2.3.0-trino-plugin/enable-trino-plugin.sh

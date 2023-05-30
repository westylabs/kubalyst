FROM phusion/baseimage:focal-1.0.0
RUN apt-get clean
RUN apt-get update
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -y install wget bc python apt-transport-https gnupg
RUN wget -O /root/postgresql.jar https://jdbc.postgresql.org/download/postgresql-42.2.23.jar
COPY mysql-connector-java.jar /root/mysql-connector-java.jar
RUN : \
    && curl -s https://repos.azul.com/azul-repo.key \
        | gpg --dearmor -o /usr/share/keyrings/azul.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/azul.gpg] https://repos.azul.com/zulu/deb stable main" \
        > /etc/apt/sources.list.d/zulu.list \
    && apt-get update \
    && apt-get -y install zulu11-jdk \
    && :
WORKDIR /root
ADD https://github.com/aakashnand/trino-ranger-demo/releases/download/trino-ranger-demo-v1.0/ranger-2.1.0-admin.tar.gz /root
ENV JAVA_HOME=/usr/lib/jvm/zulu11
RUN tar xvf ranger-2.1.0-admin.tar.gz
# COPY install_postgres.properties /root/ranger-2.1.0-admin/install.properties
COPY install_mysql.properties /root/ranger-2.1.0-admin/install.properties
COPY mysql-connector-java.jar /root/
COPY entrypoint.sh /root/

ENTRYPOINT ["sh", "-c", "/root/entrypoint.sh"]   

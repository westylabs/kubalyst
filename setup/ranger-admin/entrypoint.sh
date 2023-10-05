#!/bin/bash

RANGER_VERSION=2.1.0

cd /root/ranger-${RANGER_VERSION}-admin/ && \
./setup.sh && \
ranger-admin start && \
tail -f /root/ranger-${RANGER_VERSION}-admin/ews/logs/ranger-admin-*-.log

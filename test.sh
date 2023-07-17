#!/usr/bin/env bash

set -euo pipefail

pip uninstall -y snowflake-connector-python || true
pip install '../snowflake-connector-python[pandas]'
pytest query_cli/tests/integration/test_snowflake_connector.py::test_regexp_extract_all -s

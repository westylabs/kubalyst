#!/bin/bash

set -euo pipefail

# TODO: why do we fail with the following when trying to introspect all test method names?
# AttributeError: 'Testing' object has no attribute '__jsii_ref__'
pytest k8s/test/test_synth.py::test_synth -s

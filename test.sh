#!/bin/bash

set -euo pipefail

pytest k8s/test/test_synth.py::test_synth -s

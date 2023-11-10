from os import listdir
from os.path import isfile
from os.path import join

import kubernetes_validate
import pytest
from cdk8s import Testing

from k8s.charts.trino import Trino
from k8s.charts.trino_config import TrinoConfig


@pytest.fixture
def app():
    return Testing.app()


def test_synth(app):
    trino_config = TrinoConfig(app)
    Trino(app, trino_config.config_map)

    app.synth()

    for file in listdir(app.outdir):
        full_path = join(app.outdir, file)
        if isfile(full_path):
            kubernetes_validate.validate_file(
                full_path, "1.22", quiet=False, no_warn=True, strict=True
            )

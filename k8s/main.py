#!/usr/bin/env python
from cdk8s import App
from charts.trino import Trino
from charts.trino_config import TrinoConfig


app = App()

trino_config = TrinoConfig(app)
Trino(app, trino_config.config_map)

app.synth()

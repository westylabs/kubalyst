venv: requirements.txt
	python3 -mvenv venv --prompt=kubalyst
	./venv/bin/pip install -r requirements.txt
	./venv/bin/pip install -e .

requirements: pyproject.toml requirements.in
	pip-compile --output-file=requirements.txt --resolver=backtracking pyproject.toml

.PHONY: k8s-config-gen
k8s-config-gen:
	cd k8s && cdk8s synth --validate && kubectl apply -R -f './dist' --dry-run=client

.PHONY: k8s-config-clean
k8s-config-clean:
	rm -rf k8s/dist k8s/Pipfile

.PHONY: test
test:
	./test.sh

.PHONY: forward
forward:
	query-cli setup-port-forwards

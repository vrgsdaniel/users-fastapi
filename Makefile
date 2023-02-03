.PHONY:
checks:
	tox -e checks

.PHONY:
test:
	tox -e test

.PHONY:
dep-uninstall:
	pip freeze | xargs pip uninstall -y

.PHONY:
dep-install:
	pip install -r requirements.txt && pip install -e .

.PHONY:
dep-compile:
	pip-compile --generate-hashes requirements.in

.PHONY:
start:
	uvicorn users_fastapi.main:app --port 8080

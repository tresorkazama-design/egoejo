PYTHON?=python
NPM?=npm

.PHONY: backend-test frontend-test frontend-build predeploy

backend-test:
	cd backend && DISABLE_THROTTLE_FOR_TESTS=1 DEBUG=1 $(PYTHON) -m pytest

frontend-test:
	cd frontend && $(NPM) test -- --run

frontend-build:
	cd frontend && $(NPM) run build

predeploy: backend-test frontend-test frontend-build


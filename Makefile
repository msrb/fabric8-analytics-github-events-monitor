ifeq ($(TARGET),rhel)
  DOCKERFILE := Dockerfile.rhel
  REPOSITORY := openshiftio/rhel-fabric8-analytics-github-events-monitor
else
  DOCKERFILE := Dockerfile
  REPOSITORY := openshiftio/fabric8-analytics-github-events-monitor
endif

REGISTRY := quay.io
DEFAULT_TAG=latest

.PHONY: run test get-testing-data docker-run docker-build coverage deps get-image-name get-image-repository get-push-registry

run:
	LOGLEVEL="INFO" GITHUB_TOKEN="${GITHUB_TOKEN}" SLEEP_PERIOD=2 WATCH_REPOS="msehnout/ipc_example" python3 run.py

test:
	bash run-tests.sh

get-testing-data:
	curl https://api.github.com/events > events.json

docker-run:
	docker run -e LOGLEVEL="INFO" -e GITHUB_TOKEN="${GITHUB_TOKEN}" -e SLEEP_PERIOD=10 -e WATCH_REPOS="msehnout/ipc_example" github-monitor

docker-build:
	docker build -t github-monitor .
	docker tag github-monitor $(REGISTRY)/$(REPOSITORY):$(DEFAULT_TAG)

coverage:
	pytest --cov="ghmonitor/" --cov-report html:/tmp/cov_report -vv ghmonitor/

deps:
	pip-compile --output-file requirements.txt requirements.in

get-image-name:
	@echo $(REGISTRY)/$(REPOSITORY):$(DEFAULT_TAG)

get-image-repository:
	@echo $(REPOSITORY)

get-push-registry:
	@echo $(REGISTRY)

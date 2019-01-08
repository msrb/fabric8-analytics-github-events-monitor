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

coverage:
	pytest --cov="ghmonitor/" --cov-report html:/tmp/cov_report -vv ghmonitor/

deps:
    pip-compile --output-file requirements.txt requirements.in
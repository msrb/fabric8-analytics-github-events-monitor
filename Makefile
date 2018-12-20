run:
	LOGLEVEL=INFO python3 ghmonitor/monitor.py

test:
	pytest ghmonitor/

get-testing-data:
	curl https://api.github.com/events > events.json

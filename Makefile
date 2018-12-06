run:
	LOGLEVEL=INFO python3 monitor.py

test:
	pytest --show-capture=stdout *.py 

get-testing-data:
	curl https://api.github.com/events > events.json

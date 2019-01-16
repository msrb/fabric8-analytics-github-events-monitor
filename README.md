# Github monitoring service

 * takes a list of golang package names
 * map the names from the list to Github repositories (skip everyting else)
 * periodically scan events, that occured in the repositories

Configuration:
 * use env. variables to configure Github token, repositories, log level and sleep period
 * in general you can use sth like this to find out what you can configure:
```bash
# Check all Python files in root dir
$ grep 'os.environ.get' *.py
monitor.py:    token = os.environ.get('GITHUB_TOKEN')
monitor.py:    repos = os.environ.get('WATCH_REPOS', '')
monitor.py:    LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
monitor.py:    SLEEP_PERIOD = float(os.environ.get('SLEEP_PERIOD', 30))
# Even better, use ripgrep (available in Fedora repositories or homebrew) and it
# will go recursively through all directories not listed in .gitignore (so it will
# skip venv, which is very much desired in this case ;-) )
$ rg 'os.environ.get'
monitor.py:    token = os.environ.get('GITHUB_TOKEN')
monitor.py:    repos = os.environ.get('WATCH_REPOS', '')
monitor.py:    LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
monitor.py:    SLEEP_PERIOD = float(os.environ.get('SLEEP_PERIOD', 30))
```


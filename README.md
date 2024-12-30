# Galadriel Agent

## Setup
```shell
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
# or 
pip install -e .

cp template.env .env
nano .env
```

## Run an agent
This takes the agent definition from `agents/daige.json`
```shell
python main.py
```


## Linting etc
```shell
black galadriel_agent
mypy galadriel_agent
pylint --rcfile=setup.cfg galadriel_agent/*
```
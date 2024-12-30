# Galadriel Agent

```shell
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
# or 
pip install -e .

cp template.env .env
nano .env
```

```shell
python main.py
```

```shell
black galadriel_agent
mypy galadriel_agent
pylint --rcfile=setup.cfg galadriel_agent/*
```
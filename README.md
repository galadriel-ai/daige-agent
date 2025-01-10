# Galadriel Agent

## Setup
```shell
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
# or 
pip install -e .

# Ignore cache and install the galadriel-agent locally
pip uninstall galadriel-agent
pip install --no-cache-dir -e ../galadriel-agent
```




## Deployment

```shell
./deploy.sh
```
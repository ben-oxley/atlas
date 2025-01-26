
Run 

```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Run `choco install `
Run `choco install python rust git -y`
Run `choco uninstall postgresql --params '/AllowRemote /Password:postgres' -y`
Run `git clone https://github.com/ben-oxley/atlas.git`
Run `pip install certifi`
Run `pipx install poetry` or `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`
Run `[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Users\Administrator\AppData\Roaming\Python\Scripts", "User")`
Run `poetry install` then `poetry run python .\atlas\image-collection-pipeline.py`


Interesting sources:
Sentinel 2 COGs https://registry.opendata.aws/sentinel-2-l2a-cogs/
Sentinel 2 https://registry.opendata.aws/sentinel-2/
AI Challenges for satellite data https://spacenet.ai/datasets/
Maxar open data https://registry.opendata.aws/maxar-open-data/


## Running postgres

docker run -p 5432:5432 --name some-postgis -e POSTGRES_PASSWORD=mysecretpassword -d postgis/postgis


## Data Schema

### Metrics


### Tile
- id (pk)
- zoom 
- x
- y
- datetime
- source id (fk)

### Tile Metrics
- id (pk)
- tile (fk)
- metric (Boats, trees, houses)
- model
- value
- confidence
- unit (e.g. count, percentage )

### Models
- id (pk)
- type 
- model identifier
- 

### source
- id (pk)
- source
- source url
- datetime

### Units

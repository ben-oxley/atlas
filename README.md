

Run `poetry install` then `poetry run python .\atlas\image-collection-pipeline.py`

Interesting sources:
Sentinel 2 COGs https://registry.opendata.aws/sentinel-2-l2a-cogs/
Sentinel 2 https://registry.opendata.aws/sentinel-2/
AI Challenges for satellite data https://spacenet.ai/datasets/
Maxar open data https://registry.opendata.aws/maxar-open-data/


## Running postgres

docker run -p 5432:5432 --name some-postgis -e POSTGRES_PASSWORD=mysecretpassword -d postgis/postgis
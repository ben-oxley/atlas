import json
import uvicorn
from fastapi import FastAPI
from atlas.collect import search_images
from atlas.detect import detectInPath

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

#http://localhost:8000/collect/50.7/50.9/-1.28/-1.27?number_to_process=10
@app.get("/collect/{latmin}/{latmax}/{lonmin}/{lonmax}")
async def collect(latmin:float,latmax:float,lonmin:float,lonmax:float,number_to_process: int = 1):
    search_images(latmin,latmax,lonmin,lonmax,number_to_process)

@app.get("/analyse/{source_id}")
async def analyse(source_id:int):
    detectInPath(source_id)

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("atlas.api:app", host="0.0.0.0", port=8000, reload=True)
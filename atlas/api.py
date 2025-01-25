import json
import uvicorn
from fastapi import FastAPI
from atlas.collect import search_images
from atlas.detect import detectInPath, get_change_over_time

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

@app.get("/metrics/{tile_x}/{tile_y}/{tile_z}/{metric}")
async def analyse(tile_x:int,tile_y:int,tile_z:int,metric:str):
    result = get_change_over_time(tile_x,tile_y,tile_z,metric)
    return result




def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("atlas.api:app", host="0.0.0.0", port=8000, reload=True)
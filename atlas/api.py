import json
import uvicorn
from fastapi import FastAPI
from atlas.collect import search_images
from atlas.detect import detectInPath

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

#localhost:8000/collect/50.73645513701064/50.76425935711649/-1.0986328125000033/-1.0546875000000047
@app.get("/collect/{latmin}/{latmax}/{lonmin}/{lonmax}")
async def collect(latmin:float,latmax:float,lonmin:float,lonmax:float):
    search_images(latmin,latmax,lonmin,lonmax)

@app.get("/analyse/{source_id}")
async def analyse(source_id:int):
    detectInPath(source_id)

def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("atlas.api:app", host="0.0.0.0", port=8000, reload=True)
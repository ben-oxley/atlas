import json
import uvicorn
from fastapi import FastAPI
from atlas.collect import queue_images_in_area, search_images
from atlas.detect import detectInPath, get_change_over_time
from atlas.jobengine import check_jobs

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "running"}

'''
This method queues images within a search bounding box that are available in the 
sentinel database. At the moment it only queues images that have minimal cloud cover (<20%)
'''
#http://localhost:8000/tile/queue/50.7/50.9/-1.28/-1.27
@app.get("/images/queue/{latmin}/{latmax}/{lonmin}/{lonmax}")
async def tile_queue(latmin:float,latmax:float,lonmin:float,lonmax:float):
    queue_images_in_area(latmin,latmax,lonmin,lonmax)

'''
This method checks for jobs to process. It isn't intended as the main route processing. 
Separate containers should be run, running the job engine to continually pick up and process jobs.
'''
@app.get("/jobs/check")
async def check():
    check_jobs()

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
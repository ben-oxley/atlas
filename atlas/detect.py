from typing import Dict
from PIL import Image
from ultralytics import YOLO
from pathlib import Path

from atlas.db import AtlasDBFacade
from atlas.models.tile import Tile, TileMetricTimeline


'''
This detection routine uses the file store search to filed files to process. This relies on the files
already being on the machine in the right path. However this is important for fast processing and therefore
should be used once tiles have been cached to the machines local storage or if they already exist in the path.
'''
def detectInPath(source_id):
    test_imgs = Path("tiles").glob(f'**/{source_id}-visual.tif')
    test_imgs = [str(x) for x in test_imgs]
    print(len(test_imgs))
    #https://huggingface.co/mayrajeo/marine-vessel-detection-yolov8
    # Other models to test: https://github.com/swricci/small-boat-detector
    # From https://github.com/robmarkcole/kaggle-ships-in-Google-Earth-with-YOLOv8/blob/main/models/yolov8m_best.pt
    model = YOLO(f'models\kaggle-ships\yolov8m_best.pt')
    results = model.predict(source=test_imgs, conf=0.2, save=False)
    

    dbcontext = AtlasDBFacade()

    dbcontext.connect()

    for result in results:
        avg_confidence = result.boxes.conf.mean()
        detections = len(result.boxes)
        path_arr = result.path.split('\\')
        zoom, x, y = path_arr[-4:-1]

        tile_id = dbcontext.get_tile_id(x,y,zoom,source_id)

        tile_time = dbcontext.get_tile_time(tile_id)
    
        dbcontext.metric_insert(str(tile_id),x,y,zoom,str(tile_time),'boats',str(detections))

def get_change_over_time(tile_x:int,tile_y:int,tile_z:int,metric:str):
    dbcontext = AtlasDBFacade()

    dbcontext.connect()

    return dbcontext.get_metric(tile_x,tile_y,tile_z,metric)


def get_distinct_times(tiles:Dict[Tile,TileMetricTimeline]):
    times = set([
        datapoint.time
        for tile in tiles.values()
        for datapoints in tile.values
        for datapoint in datapoints
    ])


    
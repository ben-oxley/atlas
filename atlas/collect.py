from pystac_client import Client
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from pathlib import Path
import rasterio.plot
import rasterio.mask
import os
import urllib
import uuid

from pygeotile.tile import Tile
from pygeotile.point import Point as pyPoint
from shapely.geometry import Point, Polygon

from atlas.models.tile import Tile as TileData
from atlas.db import AtlasDBFacade


'''
Search for images that intersect the lat-lon bounds provided
'''
def search_images(lat_min, lat_max, lon_min, lon_max):
    #Zoom 13 seems to be appropriate to get near-right-size tiles back when chopped up for sentinel.
    zoom = 11
    api_url = "https://earth-search.aws.element84.com/v1"
    client = Client.open(api_url)
    collection = (
        "sentinel-2-l2a"  # Sentinel-2, Level 2A, Cloud Optimized GeoTiffs (COGs)
    )
    polygon = Polygon(
        [
            Point(lon_min, lat_min),
            Point(lon_max, lat_min),
            Point(lon_max, lat_max),
            Point(lon_min, lat_max),
        ]
    )

    search = client.search(
        collections=[collection],
        intersects=polygon,
        max_items=100,
        sortby=[
            {"direction": "desc", "field": "properties.datetime"},
            {"direction": "asc", "field": "id"},
        ],
    )

    # Just use the most recent item
    item = [item for item in search.items() if item.properties["eo:cloud_cover"] < 20][
        0
    ]

    reprojected = download_and_reproject(item.id, item.assets["visual"].href)

    dbcontext = AtlasDBFacade()

    dbcontext.connect()

    source_id = dbcontext.source_insert(item.properties["datetime"],"sentinel-2-l2a",item.assets["visual"].href)

    tiles_created = tile_image(reprojected, zoom, source_id)

    for tile in tiles_created:
        dbcontext.tile_insert(tile.x,tile.y,tile.z,item.properties["datetime"],source_id)

    


def download_and_reproject(image_name, image_url):
    dst_crs = "EPSG:3857"

    file_loc = image_name + ".tif"
    file_dest = image_name + "-3857.tif"

    if not os.path.isfile(file_loc):
        urllib.request.urlretrieve(
            image_url, file_loc
        )  # Would be worth returning Scene Classification Layer (SCL)

    if not os.path.isfile(file_dest):
        with rasterio.open(file_loc) as dataset:
            # rasterio.plot.show(dataset)
            # reprojectn('EPSG:'+str(item.properties['proj:epsg']),'EPSG:3857')
            transform, width, height = calculate_default_transform(
                dataset.crs, dst_crs, dataset.width, dataset.height, *dataset.bounds
            )

            kwargs = dataset.meta.copy()

            kwargs.update(
                {"crs": dst_crs, "transform": transform, "width": width, "height": height}
            )

            with rasterio.open(file_dest, "w", **kwargs) as dst:
                for i in range(1, 4):
                    reproject(
                        source=rasterio.band(dataset, i),
                        destination=rasterio.band(dst, i),
                        src_transform=dataset.transform,
                        src_crs=dataset.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.bilinear,
                    )
    return file_dest


def tile_image(image_name, zoom, source_id):

    tiles_created = []

    with rasterio.open(image_name) as src:

        min_tile = Tile.for_meters(
            src.bounds.left, -src.bounds.top, zoom
        )
        max_tile = Tile.for_meters(
            src.bounds.right,-src.bounds.bottom, zoom
        )
        print(min_tile.tms[0] + 1,max_tile.tms[0] - 1)
        print(min_tile.tms[1] + 1, max_tile.tms[1] - 1)
        for x in range(min_tile.tms[0] + 1, max_tile.tms[0] - 1):

            for y in range(min_tile.tms[1] + 1, max_tile.tms[1] - 1):
                print(x,y)
                tile = Tile.from_google(
                    google_x=x, google_y=y, zoom=zoom
                )  # Tile Map Service (TMS) X Y and zoom

                polygon_3857 = Polygon(
                    [
                        pyPoint.from_latitude_longitude(
                            latitude=tile.bounds[0].latitude,
                            longitude=tile.bounds[0].longitude,
                        ).meters,
                        pyPoint.from_latitude_longitude(
                            latitude=tile.bounds[0].latitude,
                            longitude=tile.bounds[1].longitude,
                        ).meters,
                        pyPoint.from_latitude_longitude(
                            latitude=tile.bounds[1].latitude,
                            longitude=tile.bounds[1].longitude,
                        ).meters,
                        pyPoint.from_latitude_longitude(
                            latitude=tile.bounds[1].latitude,
                            longitude=tile.bounds[0].longitude,
                        ).meters,
                    ]
                )

                # Make directory structure
                Path(f"tiles/{str(zoom)}/{str(x)}/{str(y)}").mkdir(
                    parents=True, exist_ok=True
                )
                
                file_dest_cropped = f"tiles/{str(zoom)}/{str(x)}/{str(y)}/{source_id}-visual.tif"
                
                out_image, out_transform = rasterio.mask.mask(
                    src, [polygon_3857], crop=True
                )

                out_meta = src.meta

                out_meta.update(
                    {
                        "driver": "GTiff",
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform,
                    }
                )

                with rasterio.open(file_dest_cropped, "w", **out_meta) as dest:
                    dest.write(out_image)

                tiles_created.append(TileData(x,y,zoom))

    return tiles_created
                


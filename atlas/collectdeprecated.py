# Based on https://planetarycomputer.microsoft.com/docs/tutorials/cloudless-mosaic-sentinel2/

from multiprocessing import freeze_support
from atlas.tiles import to_tiles
import numpy as np
import xarray as xr
import rioxarray

import rasterio.features
import stackstac
import pystac_client
import planetary_computer

import xrspatial.multispectral as ms

from dask.distributed import Client



# from dask_gateway import GatewayCluster

# cluster = GatewayCluster()  # Creates the Dask Scheduler. Might take a minute.

# client = cluster.get_client()

# cluster.adapt(minimum=4, maximum=24)
# print(cluster.dashboard_link)

def process(aoa):

    client = Client()


    bbox = rasterio.features.bounds(aoa)

    stac = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    search = stac.search(
        bbox=bbox,
        datetime="2023-01-01/2023-12-31",
        collections=["sentinel-2-l2a"],
        query={"eo:cloud_cover": {"lt": 25}},
    )

    items = search.item_collection()
    print(len(items))

    data = (
        stackstac.stack(
            items,
            assets=["B04", "B03", "B02"],  # red, green, blue
            chunksize=4096
        )
        .where(lambda x: x > 0, other=np.nan)  # sentinel-2 uses 0 as nodata
        .assign_coords(band=lambda x: x.common_name.rename("band"))  # use common names
    )
    data = data.persist()

    median = data.median(dim="time").compute()
    to_tiles(median,".","tile_{}-{}.tif")
    image = ms.true_color(*median)  # expects red, green, blue DataArrays
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.set_axis_off()
    image.transpose('band', 'y', 'x').rio.to_raster("image.tif")
    image.plot.imshow(ax=ax);
    monthly = data.groupby("time.month").median().compute()
    images = [ms.true_color(*x) for x in monthly]
    for i in range(len(images)):
        images[i].transpose('band', 'y', 'x').rio.to_raster(f"image-{i}.tif")
    images = xr.concat(images, dim="time")

    g = images.plot.imshow(x="x", y="y", rgb="band", col="time", col_wrap=3, figsize=(6, 8))
    for ax in g.axes.flat:
        ax.set_axis_off()

    plt.tight_layout()

if __name__ == '__main__':
    freeze_support()
    process()
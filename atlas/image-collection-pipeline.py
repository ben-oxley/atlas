# Based on https://planetarycomputer.microsoft.com/docs/tutorials/cloudless-mosaic-sentinel2/

from multiprocessing import freeze_support
import numpy as np
import xarray as xr

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

def process():

    client = Client()

    area_of_interest = {
        "type": "Polygon",
        "coordinates": [
            [
                [-122.27508544921875, 47.54687159892238],
                [-121.96128845214844, 47.54687159892238],
                [-121.96128845214844, 47.745787772920934],
                [-122.27508544921875, 47.745787772920934],
                [-122.27508544921875, 47.54687159892238],
            ]
        ],
    }
    bbox = rasterio.features.bounds(area_of_interest)

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
            chunksize=4096,
            resolution=100,
        )
        .where(lambda x: x > 0, other=np.nan)  # sentinel-2 uses 0 as nodata
        .assign_coords(band=lambda x: x.common_name.rename("band"))  # use common names
    )
    data = data.persist()

    median = data.median(dim="time").compute()

    image = ms.true_color(*median)  # expects red, green, blue DataArrays
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.set_axis_off()
    image.plot.imshow(ax=ax);

    images = [ms.true_color(*x) for x in monthly]
    images = xr.concat(images, dim="time")

    g = images.plot.imshow(x="x", y="y", rgb="band", col="time", col_wrap=3, figsize=(6, 8))
    for ax in g.axes.flat:
        ax.set_axis_off()

    plt.tight_layout()

if __name__ == '__main__':
    freeze_support()
    process()
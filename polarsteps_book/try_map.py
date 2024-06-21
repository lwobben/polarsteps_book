# import contextily as cx
import geopandas
import matplotlib.pyplot as plt
import pandas as pd

df = pd.DataFrame(
    {
        "City": ["Buenos Aires", "Brasilia", "Santiago", "Bogota", "Caracas"],
        "Country": ["Argentina", "Brazil", "Chile", "Colombia", "Venezuela"],
        "Latitude": [-34.58, -15.78, -33.45, 4.60, 10.48],
        "Longitude": [-58.66, -47.91, -70.66, -74.08, -66.86],
    }
)

gdf = geopandas.GeoDataFrame(
    df,
    geometry=geopandas.points_from_xy(df.Longitude, df.Latitude),
    crs="EPSG:4326",  # <-- additional argument, without it gdf.crs is None
)

# world = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
world = geopandas.read_file("/Users/lianawobben/Downloads/ne_10m_urban_areas.zip")
boundaries = geopandas.read_file(
    "/Users/lianawobben/Downloads/ne_10m_admin_0_boundary_lines_land.zip"
)
physical = geopandas.read_file(
    "/Users/lianawobben/Downloads/ne_10m_geography_regions_polys.zip"
)
# this will plot South America correctly
# ax = world[world.continent == 'South America'].plot(color='white', edgecolor='black')

ax = plt.axes()
physical.plot(ax=ax)
world.plot(color="white", edgecolor="black", ax=ax)
boundaries.plot(ax=ax)

# if the CRS of gdf is None this still workss
gdf.plot(ax=ax)
plt.show()

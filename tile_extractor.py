''' This program extracts multiple NxN tiles from a stitched image '''

import rasterio
import pandas as pd
import geopandas as gpd

def tile_extractor(mosaic, data, output, N):
    """ Takes in a .tif image (which has geographic metadata) and
    a shapefile dataframe with a geometry point column and extracts tiles
    of NxN around the geometry point. The function updates the metadata and
    writes a new .tif file for the tile and the metadata.
    """

    i=0 #Setting tile counter

    for geometry in data.geometry:

        #Getting tile longitude and latitudes from point data type
        lon = geometry.x
        lat = geometry.y
        py, px = mosaic.index(lon, lat) #Define coordinates in pixels
        window = rasterio.windows.Window(px - N//2, py - N//2, N, N) #Define window

        tile = mosaic.read(window=window) #Extract window from array

        #Embedding meta data from original mosaic and updating height,width
        meta=mosaic.meta
        meta['width'], meta['height'] = N, N
        meta['transform'] = rasterio.windows.transform(window, mosaic.transform)

        #Writing tiles
        with rasterio.open(output.format(i), 'w', **meta) as dst:
            dst.write(tile)

        i=i+1 #Updating i for tile names

def main():
    #Defining file paths
    mosaic_path=r'/exports/eddie/scratch/s2225826/mosaic.tif'
    coordinate_path=r'/home/s2225826/BOA_ppl_estimated-100m.shp'
    output=r'/exports/eddie/scratch/s2225826/tiles/tile_{}.tif'


    mosaic=rasterio.open(mosaic_path) #Reading mosaic in
    shapefile = gpd.read_file(coordinate_path) #Reading coordinates dataframe
    shapefile = shapefile.to_crs(epsg=4326,inplace=False) #Convert to lat,long

    #Defining tile size in pixels
    N=200 #This should correspond to a 100m x 100mm tile, which is 200x200 pix

    tile_extractor(mosaic,shapefile, output, N)

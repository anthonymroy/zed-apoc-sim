from geopandas import GeoDataFrame
import math
from pandas import DataFrame

ZAS_COLORMAP = [[0.6, 0.0, 0.1, 1.0],
                [1.0, 1.0, 0.7, 1.0],
                [0.0, 0.4, 0.2, 1.0]]

def generate_2d_colormap(basemap, alpha_slices):    
    import copy
    cm2d = []
    alpha_step = 1.0 / alpha_slices    
    for idx in range(alpha_slices):       
        cm = copy.deepcopy(basemap) 
        for row in cm:
            row[3] = (idx+1)*alpha_step
        cm2d = cm2d + cm
    return cm2d

def generate_geo_plot_data_for_2d_colormap(src_data_list:list[DataFrame], gdf:GeoDataFrame, alpha_slices:int) -> GeoDataFrame:
    data = []
    alpha_step = 1.0 / alpha_slices
    max_pop = max(src_data_list[0]["population_h"])
    for step in range(len(src_data_list)):        
        pop_h = src_data_list[step]["population_h"]
        pop_z = src_data_list[step]["population_z"]
        x = pop_h / (pop_h + pop_z)
        y = (pop_h + pop_z) / max_pop
        alpha = alpha_step * (y * alpha_slices).apply(math.floor)
        datum = alpha_step * x + alpha
        datum.name = step
        data.append(datum)
    data_df = DataFrame(data).T
    ret_df = GeoDataFrame(        
        data = data_df,
        geometry = gdf.geometry,
        crs = gdf.crs
    )
    return ret_df

if __name__ == "__main__":
    test_cm = generate_2d_colormap(ZAS_COLORMAP, 3)
    print(test_cm)
    junk = 1
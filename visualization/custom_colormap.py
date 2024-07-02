from geopandas import GeoDataFrame
import math
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame

BASE_COLORMAP = [[1.0, 0.0, 0.2],
                [0.8, 0.8, 0.2],
                [0.0, 1.0, 0.2]]

def interpolate_rgb(x, arr0, arr1):
    ret = []
    for i in range(len(arr0)):
        y = arr0[i] + x * (arr1[i] - arr0[i])
        ret.append(y)
    return ret

def generate_custom_colormap(basemap, color_slices = 5, alpha_slices = 4):    
    arr = np.array(basemap)
    color_step = float(arr.shape[0] - 1) / (color_slices - 1)
    alpha_step = 0.6 / (alpha_slices - 1)
    colors = []    
    for j in range(alpha_slices):
        alpha = 1 - j*alpha_step
        for i in range(color_slices - 1):
            x = i*color_step
            x0 = math.floor(x)
            x1 = math.ceil(x)
            arr0 = np.concatenate((alpha*arr[x0][:3],[arr[x0][3]]))
            arr1 = np.concatenate((alpha*arr[x1][:3],[arr[x1][3]]))
            color = interpolate_rgb(x-x0, arr0, arr1)
            colors.append(color)
        colors.append(np.concatenate((alpha*arr[-1][:3],[arr[-1][3]])))
    return ListedColormap(colors, name="zas")

def plot_examples(colormaps):
    """
    Helper function to plot data with associated colormap.
    """
    data = np.array([
        [1, 2, 3, 4, 5],
        [2, 3, 4, 5, 1],
        [3, 4, 5, 1, 2],
        [4, 5, 1, 2, 3],
        [5, 1, 2, 3, 4]
    ])
    n = len(colormaps)
    fig, axs = plt.subplots(1, n, figsize=(n * 2 + 2, 3),
                            layout='constrained', squeeze=False)
    for [ax, cmap] in zip(axs.flat, colormaps):
        psm = ax.pcolormesh(data, cmap=cmap, rasterized=True, vmin=1, vmax=5)
        fig.colorbar(psm, ax=ax)
    plt.show()

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
    #plot_examples([custom_cmap])
    cl = generate_custom_colormap(BASE_COLORMAP, 15)
    junk = 1
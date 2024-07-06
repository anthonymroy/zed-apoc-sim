import math
from matplotlib.colors import ListedColormap
import numpy as np

def interpolate_rgb(x, arr0, arr1):
    ret = []
    for i in range(len(arr0)):
        y = arr0[i] + x * (arr1[i] - arr0[i])
        ret.append(y)
    return ret

def generate_custom_colormap(basemap, color_slices = 5, alpha_slices = 4):    
    arr = np.array(basemap)
    color_step = float(arr.shape[0] - 1) / (color_slices - 1)
    alpha_step = 0.7 / (alpha_slices - 1)
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

if __name__ == "__main__":
    from config import Settings
    my_settings = Settings()
    cl = generate_custom_colormap(my_settings.base_colormap)
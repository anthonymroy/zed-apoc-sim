from config import Settings
from geopandas import GeoDataFrame
import math
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame
import utils

TIME_PROGRESSION_ERROR_MESSAGE = "TIME_PROGRESSION must be 'lin' or 'log'"

def generate_custom_colormap(basemap, color_slices = 5, alpha_slices = 4):    
    arr = np.array(basemap)
    color_step = float(arr.shape[0] - 1) / (color_slices - 1)
    alpha_step = 0.9 / (alpha_slices - 1)
    colors = []    
    for j in range(alpha_slices):
        alpha = 1 - j*alpha_step
        for i in range(color_slices - 1):
            x = i*color_step
            x0 = math.floor(x)
            x1 = math.ceil(x)
            arr0 = np.concatenate((alpha*arr[x0][:3],[arr[x0][3]]))
            arr1 = np.concatenate((alpha*arr[x1][:3],[arr[x1][3]]))
            color = utils.interpolate_rgb(x-x0, arr0, arr1)
            colors.append(color)
        colors.append(np.concatenate((alpha*arr[-1][:3],[arr[-1][3]])))
    return ListedColormap(colors)

def generate_geo_plot_data(src_data_list:list[DataFrame], gdf:GeoDataFrame, settings:Settings) -> GeoDataFrame:
    data = []
    population_top_percentile = src_data_list[0]["population_h"].quantile(0.99)
    pop_scaling = utils.safe_log10(population_top_percentile)
    for step in range(len(src_data_list)):
        pop_h = src_data_list[step]["population_h"]
        pop_z = src_data_list[step]["population_z"]
        value = pop_h.apply(utils.safe_log10) / (pop_h + pop_z + 2).apply(utils.safe_log10) #Should be between [0, 1)
        level = 1 - ((pop_h + pop_z + 2).apply(utils.safe_log10) / pop_scaling).apply(min, args=(1,)) #Should be between [0, 1)
        datum = settings.color_slices*(settings.alpha_slices * level).apply(math.floor) + (settings.color_slices * value).apply(math.floor)
        datum.name = step
        data.append(datum)
    data_df = DataFrame(data).T
    ret_df = GeoDataFrame(        
        data = data_df,
        geometry = gdf.geometry,
        crs = gdf.crs
    )
    return ret_df

def get_geo_limits(data:GeoDataFrame) -> tuple[tuple[float], tuple[float]]:
    xlim = (data.total_bounds[0], data.total_bounds[2])
    ylim = (data.total_bounds[1], data.total_bounds[3])
    return (xlim, ylim)

def get_data_limits(data:DataFrame, feature:str) -> tuple[tuple[float], tuple[float]]:
    xlim = (0, len(data)-1)   
    ylim = (0, math.ceil(max(data[feature].to_list())))
    return (xlim, ylim)

def setup_plots_and_limits(plot_types, geo_data, pop_data, settings):
    no_of_plots = len(plot_types)
    fig, axs = plt.subplots(1, no_of_plots, figsize=(no_of_plots * 4 + 2, 6),
                            layout='constrained', squeeze=False)
    _ = fig.suptitle(settings.plot_title, fontdict={'fontsize': '20', 'fontweight' : '2'})
    
    limits = []    
    for plot_type in plot_types:
        if plot_type == "geo":
            limits.append(get_geo_limits(geo_data))
        else:
            limits.append(get_data_limits(pop_data, "population_h_log10"))    
    colormap = generate_custom_colormap(settings.base_colormap, settings.color_slices, settings.alpha_slices)
    return(fig, axs, limits, colormap)

def generate_frame(
        frame:int,
        geo_data:GeoDataFrame,
        plot_borders:GeoDataFrame,
        pop_data:DataFrame,  
        plot_types:list[str],
        plot_axes:any,
        limits:tuple[tuple[float], tuple[float]],
        colormap:ListedColormap
    ) -> None:
    for [ax, bounds, plot_type] in zip(plot_axes.flat, limits, plot_types):
        match plot_type:
            case "geo":                
                generate_geo_frame(frame, ax, bounds, geo_data, plot_borders, colormap)
            case "bar":
                generate_bar_frame(frame, ax, bounds, pop_data)
            case "line":
                generate_line_frame(frame, ax, bounds, pop_data)

def generate_bar_frame(
        frame:int, 
        ax:any,
        limits:tuple[tuple[float, float], tuple[float, float]],
        pop_data:list[DataFrame]
    ) -> None:
    #Clear and redraw line plot axes
    ax.clear()
    ax.set_ylim(limits[1])  
    ax.yaxis.tick_right()
    ax.set_ylabel("Log10 Population")    
    ax.yaxis.set_label_position("right")
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)    

    #Plot population
    columns = pop_data.columns.to_list()
    values = pop_data.loc[pop_data.index[frame]].to_list()
    #Set up x-label
    x_label = [ f"Human population\n{int(pow(10, values[0])):,}", f"Zed population\n{int(pow(10, values[1])):,}"]    
    colors = ["green", "red"]
    ax.bar(columns, values, width=0.4, tick_label = x_label, color=colors)

def generate_geo_frame(
        frame:int, 
        ax:any, 
        limits:tuple[tuple[float, float], tuple[float, float]],
        data:list[GeoDataFrame],
        borders:GeoDataFrame,
        colormap:ListedColormap
        ) -> None:
    # Clear and redraw progress annotation
    progress =  f"Day: {frame}"
    #Configure axes
    ax.clear()
    ax.set_xlim(limits[0])
    ax.set_ylim(limits[1])
    ax.axis('off')        
    ax.annotate(progress, xy=(0.5, -0.05), xycoords='axes fraction', fontsize=12, ha='center')        

    # Plot boundaries
    _ = borders.boundary.plot(ax=ax, edgecolor='black', linewidth=0.3) 
    _ = data.boundary.plot(ax=ax, antialiased=False, edgecolor='face', linewidth=0.4)

    # Plot the data for the current year
    data.plot(
        ax=ax,
        column=frame,
        legend=False,
        cmap=colormap,
        rasterized=True,
        vmin=0,
        vmax=len(colormap.colors)-1
    )
    print(progress)

def generate_line_frame(
        frame:int, 
        ax:any,
        limits:tuple[tuple[float, float], tuple[float, float]],
        pop_data:list[DataFrame]
    ) -> None:
    #Clear and redraw line plot axes
    ax.clear()
    ax.set_xlim((0,frame+1))
    ax.set_ylim(limits[1])  
    ax.yaxis.tick_right()
    ax.set_ylabel("Log10 Population")
    ax.yaxis.set_label_position("right")
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #Plot population
    pop_h = pop_data["population_h_log10"].to_list()[:frame]
    pop_z = pop_data["population_z_log10"].to_list()[:frame]
    ax.plot(pop_h, c = "green")
    ax.plot(pop_z, c = "red")

def show_frame(geo_data:GeoDataFrame, plot_borders:GeoDataFrame, pop_data:DataFrame, settings:Settings) -> None:
    plot_types = settings.get_plot_types()
    (_, axs, limits, colormap) = setup_plots_and_limits(plot_types, geo_data, pop_data, settings)
    generate_frame(settings.image_frame, geo_data, plot_borders, pop_data, plot_types, axs, limits, colormap)
    plt.show()

def make_animation(geo_data:GeoDataFrame, plot_borders:GeoDataFrame, pop_data:DataFrame, settings:Settings) -> animation.FuncAnimation:
    plot_types = settings.get_plot_types()
    (fig, axs, limits, colormap) = setup_plots_and_limits(plot_types, geo_data, pop_data, settings) 
    total_frames = round(settings.fps * settings.animation_duration + 1)
    match settings.time_progression:
        case "lin":
            key_frames = utils.calculate_key_frames_linear(len(geo_data.keys())-1, total_frames)
        case "log":
            key_frames = utils.calculate_key_frames_logarithmic(len(geo_data.keys())-1, total_frames)
        case _:
            raise ValueError(TIME_PROGRESSION_ERROR_MESSAGE)

    # Create the animation
    mov = animation.FuncAnimation(
        fig=fig,
        func=generate_frame,        
        fargs=(geo_data, plot_borders, pop_data, plot_types, axs, limits, colormap),
        frames=key_frames,
        repeat=False,
        interval=1000
    )
    return mov

def show_animation() -> None:
    plt.show()

def save_animation(video:animation.FuncAnimation, settings:Settings) -> None:
    writer = animation.PillowWriter(fps=settings.fps)
    video.save(settings.video_filename, writer=writer)
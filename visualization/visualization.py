import config
from geopandas import GeoDataFrame
import math
import matplotlib.animation as animation
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.text import Text
from pandas import DataFrame
import utils
from visualization.custom_colormap import generate_custom_colormap


TIME_PROGRESSION_ERROR_MESSAGE = "TIME_PROGRESSION must be 'lin' or 'log'"

BASE_COLORMAP = [[0.6, 0.0, 0.2, 1.0],
                [0.8, 0.8, 0.2, 1.0],
                [0.0, 0.6, 0.2, 1.0]]

CUSTOM_COLORMAP = generate_custom_colormap(BASE_COLORMAP, config.COLOR_SLICES, config.ALPHA_SLICES)

# def generate_geo_plot_data(src_data_list:list[DataFrame], gdf:GeoDataFrame) -> GeoDataFrame:
#     data = []
#     for step in range(len(src_data_list)):
#         pop_h = src_data_list[step]["population_h"]
#         pop_z = src_data_list[step]["population_z"]
#         datum = pop_h / (pop_h + pop_z)
#         datum.name = step
#         data.append(datum)
#     data_df = DataFrame(data).T
#     ret_df = GeoDataFrame(        
#         data = data_df,
#         geometry = gdf.geometry,
#         crs = gdf.crs
#     )
#     return ret_df

def generate_geo_plot_data(src_data_list:list[DataFrame], gdf:GeoDataFrame) -> GeoDataFrame:
    data = []
    for step in range(len(src_data_list)):
        pop_h = src_data_list[step]["population_h"]
        pop_z = src_data_list[step]["population_z"]
        pop_d = src_data_list[step]["population_d"]
        value = (config.COLOR_SLICES * pop_h.apply(utils.safe_log10) / (pop_h + 10*pop_z + 1).apply(utils.safe_log10)).apply(math.floor)
        level = (config.ALPHA_SLICES * (0.1*pop_d).apply(utils.safe_log10) / (pop_h + pop_z + pop_d + 1).apply(utils.safe_log10)).apply(math.floor)
        datum = level*config.COLOR_SLICES + value
        datum.name = step
        data.append(datum)
    data_df = DataFrame(data).T
    ret_df = GeoDataFrame(        
        data = data_df,
        geometry = gdf.geometry,
        crs = gdf.crs
    )
    return ret_df

def calculate_key_frames_linear(data_length:int, number_of_frames:int) -> list[int]:
    '''
    Gets a linear distribution of the desired number_of_frames between [0, data_length]
    '''
    frame_step_size = float(data_length) / number_of_frames
    key_frames = []
    for i in range(number_of_frames):
        key_frames.append(round(i*frame_step_size))
    return key_frames

def calculate_key_frames_logarithmic(data_length:int, number_of_frames:int) -> list[int]:
    '''
    Gets a logarithmic distribution of the desired number_of_frames between [0, data_length]
    '''    
    key_frames = [0]
    frame_step_size = math.pow(data_length, 1/number_of_frames)
    for i in range(number_of_frames):
        key_frames.append(round(math.pow(frame_step_size, i)))
    key_frames.append(data_length-1)
    return key_frames

def setup_geo_plot(data:GeoDataFrame) -> tuple[Figure, any, tuple[float], tuple[float]]:
    fig, ax = plt.subplots(1, figsize=(8, 4))
    _ = fig.suptitle(config.PLOT_TITLE, fontdict={'fontsize': '20', 'fontweight' : '2'})
    xlim = (data.total_bounds[0], data.total_bounds[2])
    ylim = (data.total_bounds[1], data.total_bounds[3])
    return (fig, ax, xlim, ylim)

def setup_geo_bar_plot(data1:GeoDataFrame, data2:list[DataFrame]) -> tuple[Figure, any, any, tuple[float], tuple[float], tuple[float], Text]:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
    _ = fig.suptitle(config.PLOT_TITLE, fontdict={'fontsize': '20', 'fontweight' : '2'})
    xlim = (data1.total_bounds[0], data1.total_bounds[2])
    ylim1 = (data1.total_bounds[1], data1.total_bounds[3])
    ylim2 = (0, math.ceil(max(data2["population_h_log10"].to_list())))
    ax2.yaxis.tick_right()
    ax2.spines['top'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    prog_text = fig.text(0.30, 0.04, "Day: 0", ha="center", va="bottom")
    return (fig, ax1, ax2, xlim, ylim1, ylim2, prog_text)

def setup_geo_line_plot(data1:GeoDataFrame, data2:list[DataFrame]) -> tuple[Figure, any, any, tuple[float], tuple[float], tuple[float], Text]:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
    _ = fig.suptitle(config.PLOT_TITLE, fontdict={'fontsize': '20', 'fontweight' : '2'})    
    xlim1 = (data1.total_bounds[0], data1.total_bounds[2])
    ylim1 = (data1.total_bounds[1], data1.total_bounds[3])
    xlim2 = (0, len(data2)-1)   
    ylim2 = (0, math.ceil(max(data2["population_h_log10"].to_list())))
    ax2.yaxis.tick_right()
    ax2.spines['top'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    prog_text = fig.text(0.30, 0.04, "Day: 0", ha="center", va="bottom")
    return (fig, ax1, ax2, xlim1, ylim1, xlim2, ylim2, prog_text)

def make_geo_image(data:GeoDataFrame, frame:int) -> None:
     _, ax, xlim, ylim = setup_geo_plot(data) 
     generate_geo_frame(frame, ax, xlim, ylim, data)
     plt.show()

def make_bar_image(geo_data:GeoDataFrame, pop_data:DataFrame, frame:int) -> None:
    (_, ax1, ax2, xlim, ylim1, ylim2, progress_text) = setup_geo_bar_plot(geo_data, pop_data)
    generate_geo_bar_frame(frame, ax1, ax2, xlim, ylim1, ylim2, geo_data, pop_data, progress_text)
    plt.show()

def make_line_image(geo_data:GeoDataFrame, pop_data:DataFrame, frame:int) -> None:
    (_, ax1, ax2, xlim1, ylim1, xlim2, ylim2, progress_text) = setup_geo_bar_plot(geo_data, pop_data)
    generate_geo_bar_frame(frame, ax1, ax2, xlim1, ylim1, xlim2, ylim2, geo_data, pop_data, progress_text)
    plt.show()

def generate_geo_frame(frame:int, ax:any, xlim:tuple[float], ylim:tuple[float], data:list[GeoDataFrame]) -> None:
    # Clear and redraw progress annotation
    progress =  f"Day: {frame}"
    #Configure axes
    ax.clear()
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axis('off')        
    ax.annotate(progress, xy=(0.5, -0.05), xycoords='axes fraction', fontsize=12, ha='center')        

    # Plot boundaries
    _ = data.boundary.plot(ax=ax, edgecolor='black', linewidth=0.2)

    # Plot the data for the current year
    data.plot(
        ax=ax,
        column=frame,
        legend=False,
        cmap=CUSTOM_COLORMAP,
        rasterized=True,
        vmin=0,
        vmax=config.COLOR_SLICES*config.ALPHA_SLICES
    )
    print(progress)

def generate_geo_bar_frame(
        frame:int, 
        ax1:any,
        ax2:any,
        xlim:tuple[float], 
        ylim1:tuple[float],
        ylim2:tuple[float], 
        geo_data:GeoDataFrame, 
        pop_data:list[DataFrame],
        progress_text:Text
    ) -> None:

    # Clear and redraw progress annotation
    progress =  f"Day: {frame}"
    #Configure axes
    ax1.clear()
    ax1.set_xlim(xlim)
    ax1.set_ylim(ylim1)
    ax1.axis('off')        
    progress_text.set_text(progress)   

    ax2.clear()
    ax2.set_ylim(ylim2)  

    # Plot geo boundaries
    _ = geo_data.boundary.plot(ax=ax1, edgecolor='black', linewidth=0.2)

    # Plot the data for the current year
    geo_data.plot(
        ax=ax1,
        column=frame,
        legend=False,
        cmap=CUSTOM_COLORMAP,
        rasterized=True,
        vmin=0,
        vmax=config.COLOR_SLICES*config.ALPHA_SLICES
    )

    #Plot population
    columns = pop_data.columns.to_list()
    values = pop_data.loc[pop_data.index[frame]].apply(utils.safe_log10).to_list()
    colors = ["green", "red"]
    ax2.bar(columns, values, width=0.4, color=colors)
    print(progress)

def generate_geo_line_frame(
        frame:int, 
        ax1:any,
        ax2:any,
        xlim1:tuple[float, float],  
        ylim1:tuple[float, float],        
        xlim2:tuple[float, float],
        ylim2:tuple[float, float], 
        geo_data:GeoDataFrame, 
        pop_data:list[DataFrame],
        progress_text:Text
    ) -> None:

    # Clear and redraw progress annotation
    progress =  f"Day: {frame}"
    #Configure axes
    ax1.clear()
    ax1.set_xlim(xlim1)
    ax1.set_ylim(ylim1)
    ax1.axis('off')                   
    progress_text.set_text(progress)
    #Clear and redraw line plot axes
    ax2.clear()
    ax2.set_xlim(xlim2)
    ax2.set_ylim(ylim2)  

    # Plot geo boundaries
    _ = geo_data.boundary.plot(ax=ax1, edgecolor='black', linewidth=0.2)

    # Plot the geo data for the current day
    geo_data.plot(
        ax=ax1,
        column=frame,
        legend=False,
        cmap=CUSTOM_COLORMAP,
        rasterized=True,
        vmin=0,
        vmax=config.COLOR_SLICES*config.ALPHA_SLICES
    )

    #Plot population
    pop_h = pop_data["population_h_log10"].to_list()[:frame]
    pop_z = pop_data["population_z_log10"].to_list()[:frame]
    ax2.plot(pop_h, c = "green")
    ax2.plot(pop_z, c = "red")
    print(progress)

def make_geo_animation(geo_data:GeoDataFrame, fps:float, duration:float) -> animation.FuncAnimation:
    (fig, ax1, xlim, ylim) = setup_geo_plot(geo_data)    
    total_frames = fps * duration + 1
    match config.TIME_PROGRESSION:
        case "lin":
            key_frames = calculate_key_frames_linear(len(geo_data.keys())-1, total_frames)
        case "log":
            key_frames = calculate_key_frames_logarithmic(len(geo_data.keys())-1, total_frames)
        case _:
            raise ValueError(TIME_PROGRESSION_ERROR_MESSAGE)
       
    # Create the animation
    mov = animation.FuncAnimation(
        fig=fig,
        func=generate_geo_frame,        
        fargs=(ax1, xlim, ylim, geo_data),
        frames=key_frames,
        repeat=False,
        interval=1000
    )
    return mov

def make_geo_bar_animation(geo_data:GeoDataFrame, pop_data:list[DataFrame], fps:float, duration:float) -> animation.FuncAnimation:
    (fig, ax1, ax2, xlim, ylim1, ylim2, progress_text) = setup_geo_bar_plot(geo_data, pop_data)    
    total_frames = fps * duration + 1
    match config.TIME_PROGRESSION:
        case "lin":
            key_frames = calculate_key_frames_linear(len(geo_data.keys())-1, total_frames)
        case "log":
            key_frames = calculate_key_frames_logarithmic(len(geo_data.keys())-1, total_frames)
        case _:
            raise ValueError(TIME_PROGRESSION_ERROR_MESSAGE)
       
    # Create the animation
    mov = animation.FuncAnimation(
        fig=fig,
        func=generate_geo_bar_frame,        
        fargs=(ax1, ax2, xlim, ylim1, ylim2, geo_data, pop_data, progress_text),
        frames=key_frames,
        repeat=False,
        interval=1000
    )
    return mov

def make_geo_line_animation(geo_data:GeoDataFrame, pop_data:list[DataFrame], fps:float, duration:float) -> animation.FuncAnimation:
    (fig, ax1, ax2, xlim1, ylim1, xlim2, ylim2, progress_text) = setup_geo_line_plot(geo_data, pop_data)    
    total_frames = fps * duration + 1
    match config.TIME_PROGRESSION:
        case "lin":
            key_frames = calculate_key_frames_linear(len(geo_data.keys())-1, total_frames)
        case "log":
            key_frames = calculate_key_frames_logarithmic(len(geo_data.keys())-1, total_frames)
        case _:
            raise ValueError(TIME_PROGRESSION_ERROR_MESSAGE)
       
    # Create the animation
    mov = animation.FuncAnimation(
        fig=fig,
        func=generate_geo_line_frame,        
        fargs=(ax1, ax2, xlim1, ylim1, xlim2, ylim2, geo_data, pop_data, progress_text),
        frames=key_frames,
        repeat=False,
        interval=1000
    )
    return mov

def show_animation() -> None:
    plt.show()

def save_animation(video:animation.FuncAnimation, filename:str, fps:float) -> None:
    writer = animation.PillowWriter(fps=fps)
    video.save(filename, writer=writer)
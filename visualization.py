import config
from geopandas import GeoDataFrame
import math
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from pandas import DataFrame

TIME_PROGRESSION_ERROR_MESSAGE = "TIME_PROGRESSION must be 'lin' or 'log'"

def generate_plot_data(src_data_list:list[DataFrame], gdf:GeoDataFrame):
    data = []
    for step in range(len(src_data_list)):
        pop_h = src_data_list[step]["population_h"]
        pop_z = src_data_list[step]["population_z"]
        datum = pop_h / (pop_h + pop_z)
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

def setup_plot(data:list[GeoDataFrame]) -> tuple[plt.Figure, any, float, float]:
    fig, ax = plt.subplots(1, figsize=(8, 4))
    _ = fig.suptitle(config.PLOT_TITLE, fontdict={'fontsize': '20', 'fontweight' : '2'})
    xlim = (data.total_bounds[0], data.total_bounds[2])
    ylim = (data.total_bounds[1], data.total_bounds[3])
    return (fig, ax, xlim, ylim)

def generate_frame(frame:int, ax:any, xlim:float, ylim:float, data:list[GeoDataFrame]) -> None:
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

    # Normalize colormap    
    norm = plt.Normalize(vmin=config.VMIN, vmax=config.VMAX)

    # Plot the data for the current year
    data.plot(ax=ax, column=frame, legend=False, cmap=config.COLORMAP, norm=norm)
    print(progress)

def make_image(data:list[GeoDataFrame], frame:int) -> None:
    _, ax, xlim, ylim = setup_plot(data) 
    generate_frame(frame, ax, xlim, ylim, data)
    plt.show()

def make_animation(data:list[GeoDataFrame], fps:float, duration:float) -> animation.FuncAnimation:
    fig, ax, xlim, ylim = setup_plot(data)    
    total_frames = fps * duration + 1
    match config.TIME_PROGRESSION:
        case "lin":
            key_frames = calculate_key_frames_linear(len(data.keys())-1, total_frames)
        case "log":
            key_frames = calculate_key_frames_logarithmic(len(data.keys())-1, total_frames)
        case _:
            raise ValueError(TIME_PROGRESSION_ERROR_MESSAGE)
       
    # Create the animation
    mov = animation.FuncAnimation(
        fig=fig,
        func=generate_frame,        
        fargs=(ax, xlim, ylim, data),
        frames=key_frames,
        repeat=False,
        interval=1000
    )
    return mov

def save_animation(video:animation.FuncAnimation, filename:str, fps:float) -> None:
    writer = animation.PillowWriter(fps=fps)
    video.save(filename, writer=writer)
    plt.close()
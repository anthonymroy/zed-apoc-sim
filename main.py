import animation as ani
import config
from geopandas import GeoDataFrame
import simulate
from pandas import DataFrame
import setup

MODE = "state"

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

if __name__ == "__main__":
    shape_gdf, border_df, population_df = setup.main(MODE)  
    data_df = simulate.initialize(shape_gdf, border_df, population_df)    
    time_data = simulate.run(data_df)    
    plot_data = generate_plot_data(time_data, shape_gdf)
    ani.make_image(plot_data,2)
    mov = ani.make_animation(plot_data, config.FPS, config.ANIMATION_DURATION)
    ani.save_animation(mov, config.VIDEO_FILENAME, config.FPS)

 
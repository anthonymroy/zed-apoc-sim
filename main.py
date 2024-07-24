import argparse
from config import Filepaths, Settings
import errno
import os
import pickle
import setup
import simulate
import visualize as viz

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulate a zombie outbreak")    
    #parser.add_argument("region", help="The two-letter region to simulate.")
    parser.add_argument("--sim", dest="sim_only", action="store_true", default=False,
                           help="Flag to run only the simulation without visualization")
    parser.add_argument("--viz", dest="viz_only", action="store_true", default=False,
                           help="Flag to visualize the last simulation without rerunning it")
    return parser.parse_args()    

if __name__ == "__main__":
    my_settings = Settings()
    my_filepaths = Filepaths()
    my_args = parse_arguments()

    # my_settings.simulation_region = my_args.region.upper()

    shape_gdf, border_df, population_df = setup.main(my_settings, my_filepaths)
    
    if my_args.viz_only:
        if not os.path.exists(my_filepaths.last_simulation_filename):
            e = FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), my_filepaths.last_simulation_filename)
            e.strerror += ". Run the simulation locally to create it" #Add remedy to error message
            raise e
        time_data = pickle.load(open(my_filepaths.last_simulation_filename, "rb"))
    else: 
        data_df = simulate.initialize(shape_gdf, border_df, population_df, my_settings)    
        time_data = simulate.run(data_df, my_settings)        
        pickle.dump(time_data, open(my_filepaths.last_simulation_filename, 'wb'))

    time_totals = simulate.summarize(time_data)
    print("Zombie Apocalypse Simulation complete:")
    print(f"Initial population: {round(pow(10,time_totals.at[0,'population_h_log10'])):,d}")
    print(f"Final population: {round(pow(10,time_totals.at[my_settings.simulation_length,'population_h_log10'])):,d}")
    print(f"Maximum zed population: {round(max([sum(df['population_z']) for df in time_data])):,d}")

    if not my_args.sim_only:     
        plot_data = viz.generate_geo_plot_data(time_data, shape_gdf, my_settings)
        state_borders = setup.get_states_shapefile(my_filepaths)
        if my_settings.show_image:
            viz.show_frame(plot_data, state_borders, time_totals, my_settings)
        if my_settings.make_animation:
            mov = viz.make_animation(plot_data, state_borders, time_totals, my_settings)
            viz.save_animation(mov, my_settings)        
    

    
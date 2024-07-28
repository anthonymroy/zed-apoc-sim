import argparse
from cli import MainCLI
from config import Filepaths, Settings
import errno
import os
import pickle
import setup
import simulate
import visualize as viz

NO_SIM_MESSAGE = "Error: Unable to visualize without simulating first. Please run 'sim' or 'load' before calling 'viz'"
NO_LAST_SIM_MESSAGE = ". Unable to load last simulation. Please run 'sim' before calling 'load'"

# def parse_arguments2() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(description="Simulate a zombie outbreak")    
#     parser.add_argument("resolution", help="Select a resolution of ['state'] or 'county'",
#                         action="store", default="state")
#     parser.add_argument("--sim", dest="sim_only", action="store_true", default=False,
#                            help="Flag to run only the simulation without visualization")
#     parser.add_argument("--viz", dest="viz_only", action="store_true", default=False,
#                            help="Flag to visualize the last simulation without rerunning it")
#     return parser.parse_args()    

_settings = Settings()
_filepaths = Filepaths()
_cli = MainCLI
_shape_gdf = None
_border_df = None
_population_df = None
_simulation_data = None
_simulation_summary = None
_plot_data = None

def print_report(data, totals) -> None:
    print(f"Initial population: {round(pow(10,totals.at[0,'population_h_log10'])):,d}")
    print(f"Final population: {round(pow(10,totals.at[_settings.simulation_length,'population_h_log10'])):,d}")
    print(f"Maximum zed population: {round(max([sum(df['population_z']) for df in data])):,d}")

def main():
    while True:
        text = input(">> ")
        if len(text) == 0:
            text = "-help"
        if text[0] != "-":
            text = "-"+text
        try:
            args = _cli.parse_args(text.split())
            if args.quit:
                print("Quiting...")
                break
            if args.run or args.setup:
                pass
            if args.run or args.sim:
                _shape_gdf, _border_df, _population_df = setup.main(_settings, _filepaths)
                initial_df = simulate.initialize(_shape_gdf, _border_df, _population_df, _settings)    
                _simulation_data = simulate.run(initial_df, _settings)
                _simulation_summary = simulate.summarize(_simulation_data)
                pickle.dump(_simulation_data, open(_filepaths.last_simulation_filename, 'wb'))
            if args.load:
                if not os.path.exists(_filepaths.last_simulation_filename):
                    e = FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), _filepaths.last_simulation_filename)
                    e.strerror += NO_LAST_SIM_MESSAGE
                    raise e
                _simulation_data = pickle.load(open(_filepaths.last_simulation_filename, "rb"))
                _simulation_summary = simulate.summarize(_simulation_data)
            if args.run or args.viz:
                if _simulation_data == None:
                    print(NO_SIM_MESSAGE)
                    continue
                _plot_data = viz.generate_geo_plot_data(_simulation_data, _shape_gdf, _settings)
                state_borders = setup.get_states_shapefile(_filepaths)
                if _settings.show_image:
                    viz.show_frame(_plot_data, state_borders, _simulation_summary, _settings)
                if _settings.make_animation:
                    mov = viz.make_animation(_plot_data, state_borders, _simulation_summary, _settings)
                    viz.save_animation(mov, _settings)
        except SystemExit as e:
            #Don't exit the program on an error
            pass

if __name__ == "__main__":
    main()
    # my_settings = Settings
    # my_filepaths = Filepaths()
    # print(f"Starting {my_settings.plot_title}")
    # my_args = parse_arguments2()
    # resolution = my_args.resolution.lower()
    # match resolution:
    #     case "state" | "county":
    #         my_settings.simulation_resolution = resolution
    #     case _:
    #         error_msg = f"Resolution value of {resolution} is not understood. "
    #         error_msg += "The value must be ['state'] or 'county'"
    #         raise ValueError(error_msg)
        
    # shape_gdf, border_df, population_df = setup.main(my_settings, my_filepaths)
    
    # if my_args.viz_only:
    #     if not os.path.exists(my_filepaths.last_simulation_filename):
    #         e = FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), my_filepaths.last_simulation_filename)
    #         e.strerror += ". Run the simulation locally to create it" #Add remedy to error message
    #         raise e
    #     time_data = pickle.load(open(my_filepaths.last_simulation_filename, "rb"))
    # else: 
    #     data_df = simulate.initialize(shape_gdf, border_df, population_df, my_settings)    
    #     time_data = simulate.run(data_df, my_settings)        
    #     pickle.dump(time_data, open(my_filepaths.last_simulation_filename, 'wb'))

    # time_totals = simulate.summarize(time_data)
    # print("Zombie Apocalypse Simulation complete:")
    # print_report(time_data, time_totals)

    # if not my_args.sim_only:     
    #     plot_data = viz.generate_geo_plot_data(time_data, shape_gdf, my_settings)
    #     state_borders = setup.get_states_shapefile(my_filepaths)
    #     if my_settings.show_image:
    #         viz.show_frame(plot_data, state_borders, time_totals, my_settings)
    #     if my_settings.make_animation:
    #         mov = viz.make_animation(plot_data, state_borders, time_totals, my_settings)
    #         viz.save_animation(mov, my_settings)        
    # print_report(time_data, time_totals)

    
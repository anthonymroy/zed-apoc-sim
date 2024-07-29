import argparse
from cli import CLI
from config import Filepaths, Settings
import errno
import os
import pickle
import setup
import simulate
import visualize as viz

NO_LAST_SIM_MESSAGE = ". Unable to load last simulation. Please run 'sim' before calling 'load'"
NO_SIM_MESSAGE_REPORT = "Error: Unable to report without simulating first."
NO_SIM_MESSAGE_VIZ = "Error: Unable to visualize without simulating first. Please run 'sim' or 'load' before calling 'viz'"
SUPPRESS = '==SUPPRESS=='

global _shape_gdf
_border_df = None
_population_df = None
global _simulation_data
global _simulation_summary
_plot_data = None

# def parse_arguments2() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(description="Simulate a zombie outbreak")    
#     parser.add_argument("resolution", help="Select a resolution of ['state'] or 'county'",
#                         action="store", default="state")
#     parser.add_argument("--sim", dest="sim_only", action="store_true", default=False,
#                            help="Flag to run only the simulation without visualization")
#     parser.add_argument("--viz", dest="viz_only", action="store_true", default=False,
#                            help="Flag to visualize the last simulation without rerunning it")
#     return parser.parse_args()    

class MainCLI:
    def __init__(self):
        self._parser = argparse.ArgumentParser(prog='Simulator Settings', description='Commands', add_help=False, allow_abbrev=True)
        self._parser.add_argument("-echo", dest="echo", action="store_true", help="Echo settings to screen")
        self._parser.add_argument("-help", action='help', default=SUPPRESS, help= "Show this help message")        
        self._parser.add_argument("-run", dest="run", action="store_true", help="Run simulation and visualization")
        self._parser.add_argument("-sim", dest="sim", action="store_true", help="Simulation Settings")
        self._parser.add_argument("-viz", dest="viz", action="store_true", help="Visualization settings")
        self._parser.add_argument("-quit", dest="quit", action="store_true", help="Quit the program")

    def run(self, settings:Settings):
        while True:
            text = input(">> ")
            if len(text) == 0:
                text = "--help"
            if text[0] != "-":
                text = "-"+text
            try:
                args = self._parser.parse_args(text.lower().split())
                if args.quit:
                    print("Quiting...")
                    break
                if args.echo:
                    settings.echo()
                if args.run:
                    print("Run simulation and vizualization")
                    run_simulation()
                    run_visualization()
                    print_report()
                if args.sim:
                    simCLI = SimCLI()
                    simCLI.run(settings)
                    print("Main Menu:")
                if args.viz:
                    print("Run vizualization")
            except SystemExit:
                #Don't exit the program on an error
                pass

class SimCLI:
    def __init__(self):
        self._parser = argparse.ArgumentParser(prog='Simulator Settings', description='Commands', add_help=False, allow_abbrev=True)
        self._parser.add_argument("-echo", dest="echo", action="store_true", help="Echo settings to screen")
        self._parser.add_argument("-help", action='help', default=SUPPRESS, help= "Show this help message")
        self._parser.add_argument("-res", dest="resolution", action="store", help="Resolution of 'state'(default) or 'county'",
                            default=None, choices={"county", "state"})
        self._parser.add_argument("-run", dest="run", action="store_true", help="Run the simulation without visualization")
        self._parser.add_argument("-back", dest="back", action="store_true", help="Go back to main menu")

    def run(self, settings:Settings):
        print("Simulation Menu:")
        while True:
            text = input(">> ")
            if len(text) == 0:
                text = "--help"
            if text[0] != "-":
                text = "-"+text
            try:
                args = self._parser.parse_args(text.lower().split())
                if args.back:
                    print("Back to main menu...")
                    break
                if args.echo:
                    settings.echo()
                if args.run:
                    print("Run simulation only")
                    run_simulation()
                    print_report()
                if args.resolution:
                    settings.simulation_resolution = args.resolution
            except SystemExit:
                #Don't exit the program on an error
                pass


def run_simulation():
    _shape_gdf, _border_df, _population_df = setup.main(_settings, _filepaths)
    initial_df = simulate.initialize(_shape_gdf, _border_df, _population_df, _settings)    
    _simulation_data = simulate.run(initial_df, _settings)
    _simulation_summary = simulate.summarize(_simulation_data)
    pickle.dump(_simulation_data, open(_filepaths.last_simulation_filename, 'wb'))

def load_simulation():
    if not os.path.exists(_filepaths.last_simulation_filename):
        e = FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), _filepaths.last_simulation_filename)
        e.strerror += NO_LAST_SIM_MESSAGE
        raise e
    _simulation_data = pickle.load(open(_filepaths.last_simulation_filename, "rb"))
    _simulation_summary = simulate.summarize(_simulation_data)
    return

def run_visualization():
    if not _simulation_data:
        print(NO_SIM_MESSAGE_VIZ)
        return
    _plot_data = viz.generate_geo_plot_data(_simulation_data, _shape_gdf, _settings)
    state_borders = setup.get_states_shapefile(_filepaths)
    if _settings.show_image:
        viz.show_frame(_plot_data, state_borders, _simulation_summary, _settings)
    if _settings.make_animation:
        mov = viz.make_animation(_plot_data, state_borders, _simulation_summary, _settings)
        viz.save_animation(mov, _settings)

def print_report() -> None:
    if not _simulation_data or not _simulation_summary:
        print(NO_SIM_MESSAGE_REPORT)
        return
    print(f"Initial population: {round(pow(10,_simulation_summary.at[0,'population_h_log10'])):,d}")
    print(f"Final population: {round(pow(10,_simulation_summary.at[_settings.simulation_length,'population_h_log10'])):,d}")
    print(f"Maximum zed population: {round(max([sum(df['population_z']) for df in _simulation_data])):,d}")

_settings = Settings()
_filepaths = Filepaths()
_cli = MainCLI()

def main():
    print("Enter commands:")
    _cli.run(_settings)
    print("Program exited")

    # while True:
    #     text = input(">> ")
    #     if len(text) == 0:
    #         text = "-help"
    #     if text[0] != "-":
    #         text = "-"+text
    #     try:
    #         args = _cli.parse_args(text.split())
    #         if args.quit:
    #             print("Quiting...")
    #             break
    #         if args.run or args.setup:
    #             pass
    #         if args.run or args.sim:
    #             _shape_gdf, _border_df, _population_df = setup.main(_settings, _filepaths)
    #             initial_df = simulate.initialize(_shape_gdf, _border_df, _population_df, _settings)    
    #             _simulation_data = simulate.run(initial_df, _settings)
    #             _simulation_summary = simulate.summarize(_simulation_data)
    #             pickle.dump(_simulation_data, open(_filepaths.last_simulation_filename, 'wb'))
    #         if args.load:
    #             if not os.path.exists(_filepaths.last_simulation_filename):
    #                 e = FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), _filepaths.last_simulation_filename)
    #                 e.strerror += NO_LAST_SIM_MESSAGE
    #                 raise e
    #             _simulation_data = pickle.load(open(_filepaths.last_simulation_filename, "rb"))
    #             _simulation_summary = simulate.summarize(_simulation_data)
    #         if args.run or args.viz:
    #             if _simulation_data == None:
    #                 print(NO_SIM_MESSAGE)
    #                 continue
    #             _plot_data = viz.generate_geo_plot_data(_simulation_data, _shape_gdf, _settings)
    #             state_borders = setup.get_states_shapefile(_filepaths)
    #             if _settings.show_image:
    #                 viz.show_frame(_plot_data, state_borders, _simulation_summary, _settings)
    #             if _settings.make_animation:
    #                 mov = viz.make_animation(_plot_data, state_borders, _simulation_summary, _settings)
    #                 viz.save_animation(mov, _settings)
    #     except SystemExit as e:
    #         #Don't exit the program on an error
    #         pass

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

    
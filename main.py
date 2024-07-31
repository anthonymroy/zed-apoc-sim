import argparse
from config import Filepaths, Settings
import errno
from geopandas import GeoDataFrame
import os
from pandas import DataFrame
import pickle
import setup
import simulate
import visualize as viz

NO_LAST_SIM_MESSAGE = ". Unable to load last simulation. Please run 'sim' before calling 'load'"
NO_SIM_MESSAGE_REPORT = "Error: Unable to report without simulating first."
NO_SIM_MESSAGE_VIZ = "Error: Unable to visualize without simulating first. Please run 'sim' or 'load' before calling 'viz'"
SUPPRESS = '==SUPPRESS=='

class MainCLI:
    def __init__(self, settings:Settings, filepaths:Filepaths):
        self._settings = settings
        self._filepaths = filepaths
        self._shape_gdf = None
        self._simulation_data = None
        self._simulation_summary = None
        self._parser = argparse.ArgumentParser(prog='Simulator Settings', description='Commands', add_help=False, allow_abbrev=True)
        self._parser.add_argument("-echo", dest="echo", action="store_true", help="Echo settings to screen")
        self._parser.add_argument("-help", action='help', default=SUPPRESS, help= "Show this help message")
        self._parser.add_argument("-load", dest="load", action="store_true", help="Load the last simulation run")
        self._parser.add_argument("-run", dest="run", action="store_true", help="Run simulation and visualization")
        self._parser.add_argument("-sim", dest="sim", action="store_true", help="Simulation Settings")
        self._parser.add_argument("-viz", dest="viz", action="store_true", help="Visualization settings")
        self._parser.add_argument("-quit", dest="quit", action="store_true", help="Quit the program")

    def run(self):
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
                    self._settings.echo()
                if args.load:
                    self._simulation_data, self._simulation_summary = load_simulation(self._filepaths)
                    match self._settings.simulation_resolution:
                        case "state":
                            self._shape_gdf = setup.get_states_shapefile(self._filepaths)
                        case "county":
                            self._shape_gdf = setup.get_county_shapefile(self._filepaths)
                        case _:
                            raise ValueError
                if args.run:
                    print("Run simulation and vizualization")
                    self._shape_gdf, self._simulation_data, self._simulation_summary = run_simulation(self._settings, self._filepaths)
                    run_visualization(
                        self._settings,
                        self._filepaths,
                        self._shape_gdf,
                        self._simulation_data,
                        self._simulation_summary
                    )
                    print_report(self._settings, self._simulation_data, self._simulation_summary)
                if args.sim:
                    simCLI = SimCLI(
                        self._settings,
                        self._filepaths,
                        self._shape_gdf,
                        self._simulation_data,
                        self._simulation_summary
                    )
                    simCLI.run()                    
                    print("Main Menu:")
                if args.viz:
                    vizCLI = VizCLI(
                        self._settings,
                        self._filepaths,
                        self._shape_gdf,
                        self._simulation_data,
                        self._simulation_summary
                    )
                    vizCLI.run()                    
                    print("Main Menu:")
            except SystemExit:
                #Don't exit the program on an error
                pass

class SimCLI:
    def __init__(self, settings:Settings, filepaths:Filepaths, shape_gdf, simulation_data, simulation_summary):
        self._settings = settings
        self._filepaths = filepaths
        self._shape_gdf = shape_gdf
        self._simulation_data = simulation_data
        self._simulation_summary = simulation_summary
        self._parser = argparse.ArgumentParser(prog='Simulator Settings', description='Commands', add_help=False, allow_abbrev=True)
        self._parser.add_argument("-echo", dest="echo", action="store_true", help="Echo settings to screen")
        self._parser.add_argument("-help", action='help', default=SUPPRESS, help= "Show this help message")
        self._parser.add_argument("-load", dest="load", action="store_true", help="Load the last simulation run")
        self._parser.add_argument("-resolution", dest="resolution", action="store", help="Resolution of 'state'(default) or 'county'",
                            default=None, choices={"county", "state"})
        self._parser.add_argument("-run", dest="run", action="store_true", help="Run the simulation without visualization")
        self._parser.add_argument("-back", dest="back", action="store_true", help="Go back to main menu")

    def run(self):
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
                    self._settings.echo()
                if args.load:
                    self._simulation_data, self._simulation_summary = load_simulation(self._filepaths)
                    match self._settings.simulation_resolution:
                        case "state":
                            self._shape_gdf = setup.get_states_shapefile(self._filepaths)
                        case "county":
                            self._shape_gdf = setup.get_county_shapefile(self._filepaths)
                        case _:
                            raise ValueError
                if args.run:
                    print("Run simulation only")
                    self._shape_gdf, self._simulation_data, self._simulation_summary = run_simulation(self._settings, self._filepaths)
                if args.resolution:
                    self._settings.simulation_resolution = args.resolution
            except SystemExit:
                #Don't exit the program on an error
                pass

class VizCLI:
    def __init__(self, settings:Settings, filepaths:Filepaths, shape_gdf, simulation_data, simulation_summary):
        self._settings = settings
        self._filepaths = filepaths
        self._shape_gdf = shape_gdf
        self._simulation_data = simulation_data
        self._simulation_summary = simulation_summary
        self._parser = argparse.ArgumentParser(prog='Visualization Settings', description='Commands', add_help=False, allow_abbrev=True)
        self._parser.add_argument("-echo", dest="echo", action="store_true", help="Echo settings to screen")
        self._parser.add_argument("-help", action='help', default=SUPPRESS, help= "Show this help message")
        self._parser.add_argument("-duration", dest="duration", action="store", help="Duration of the video",
                            default=None, type=float)
        self._parser.add_argument("-run", dest="run", action="store_true", help="Run the visualization without rerunning the simulation")
        self._parser.add_argument("-back", dest="back", action="store_true", help="Go back to main menu")

    def run(self):
        print("Visualization Menu:")
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
                    self._settings.echo()
                if args.run:
                    print("Run vizualization")
                    run_visualization(
                        self._settings,
                        self._filepaths,
                        self._shape_gdf,
                        self._simulation_data,
                        self._simulation_summary
                    )
                    print_report(self._settings, self._simulation_data, self._simulation_summary)
                if args.duration:
                    self._settings.animation_duration = args.duration
            except SystemExit:
                #Don't exit the program on an error
                pass

def run_simulation(settings:Settings, filepaths:Filepaths) -> tuple[GeoDataFrame, list[DataFrame], DataFrame]:
    shape_gdf, border_df, population_df = setup.main(settings, filepaths)
    initial_df = simulate.initialize(shape_gdf, border_df, population_df, settings)    
    simulation_data = simulate.run(initial_df, settings)
    simulation_summary = simulate.summarize(simulation_data)
    pickle.dump(simulation_data, open(filepaths.last_simulation_filename, 'wb'))
    print_report(settings, simulation_data, simulation_summary)
    return shape_gdf, simulation_data, simulation_summary

def load_simulation(filepaths:Filepaths) -> tuple[list[DataFrame], DataFrame]:
    if not os.path.exists(filepaths.last_simulation_filename):
        e = FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filepaths.last_simulation_filename)
        e.strerror += NO_LAST_SIM_MESSAGE
        raise e
    simulation_data = pickle.load(open(filepaths.last_simulation_filename, "rb"))
    simulation_summary = simulate.summarize(simulation_data)
    return simulation_data, simulation_summary

def run_visualization(
        settings:Settings,
        filepaths:Filepaths,
        shape_gdf:GeoDataFrame,
        simulation_data:list[DataFrame],
        simulation_summary:DataFrame) -> None:
    if not simulation_data:
        print(NO_SIM_MESSAGE_VIZ)
        return
    plot_data = viz.generate_geo_plot_data(simulation_data, shape_gdf, settings)
    state_borders = setup.get_states_shapefile(filepaths)
    if settings.show_image:
        viz.show_frame(plot_data, state_borders, simulation_summary, settings)
    if settings.make_animation:
        mov = viz.make_animation(plot_data, state_borders, simulation_summary, settings)
        viz.save_animation(mov, settings)

def print_report(settings, simulation_data, simulation_summary) -> None:
    if not simulation_data or type(simulation_summary) is not DataFrame:
        print(NO_SIM_MESSAGE_REPORT)
        return
    print(f"Initial population: {round(pow(10,simulation_summary.at[0,'population_h_log10'])):,d}")
    print(f"Final population: {round(pow(10,simulation_summary.at[settings.simulation_length,'population_h_log10'])):,d}")
    print(f"Maximum zed population: {round(max([sum(df['population_z']) for df in simulation_data])):,d}")

def main():
    settings = Settings()
    filepaths = Filepaths()
    cli = MainCLI(settings, filepaths)
    print("Enter commands:")
    cli.run()
    print("Program exited")

if __name__ == "__main__":
    main()    
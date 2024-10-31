from config import Filepaths, Settings
from geopandas import GeoDataFrame
from pandas import DataFrame
import pickle
import setup
import simulate
import visualize as viz

NO_SIM_MESSAGE_REPORT = "Error: Unable to report without simulating first."
NO_SIM_MESSAGE_VIZ = "Error: Unable to visualize without simulating first. Please run 'sim' or 'load' before calling 'viz'"

def display_menu():
  print("Available Options:")
  print("0. Test Run")
  print("1. Night of the Living Dead (1968)")
  print("2. Dawn of the Dead (2004)")
  print("3. The Walking Dead (2010)")
  print("Q. Quit")

def run_simulation(settings:Settings, filepaths:Filepaths) -> tuple[GeoDataFrame, list[DataFrame], DataFrame]:
    shape_gdf, border_df, population_df = setup.main(settings, filepaths)
    initial_df = simulate.initialize(shape_gdf, border_df, population_df, settings)    
    simulation_data = simulate.run(initial_df, settings)
    simulation_summary = simulate.summarize(simulation_data)
    pickle.dump(simulation_data, open(filepaths.last_simulation_filename, 'wb'))
    print_report(settings, simulation_data, simulation_summary)
    return shape_gdf, simulation_data, simulation_summary

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

def main(settings:Settings, filepaths:Filepaths):
    while True:
        display_menu()
        choice = input("Choose scenario: ")
        if choice == '0':
            settings.set_test_scenario()
        elif choice == '1':
            settings.set_scenario1()
        elif choice == '2':
            settings.set_scenario2()
        elif choice == '3':
            settings.set_scenario3()
        elif choice.lower() == 'q':
            break
        else:
            print("Invalid choice. Please try again.")
        try:
            shape_gdf, simulation_data, simulation_summary = run_simulation(settings, filepaths)
            run_visualization(settings, filepaths, shape_gdf, simulation_data, simulation_summary)
            print_report(settings, simulation_data, simulation_summary)
        except Exception as ex:
            print(ex)

if __name__ == "__main__":    
    my_settings = Settings()
    my_filepaths = Filepaths()
    main(my_settings, my_filepaths)    
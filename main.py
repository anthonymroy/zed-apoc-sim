import argparse
import config
import errno
import os
import pickle
import setup
import simulate
import visualization as viz

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulate a zombie outbreak")    
    parser.add_argument("region", default=config.DEFAULT_REGION,
                           help="The two-letter region to simulate. 'US' is the default value")
    parser.add_argument("--sim", dest="sim_only", action="store_true", default=False,
                           help="Flag to run only the simulation without visualization")
    parser.add_argument("--viz", dest="viz_only", action="store_true", default=False,
                           help="Flag to visualize the last simulation without rerunning it")
    return parser.parse_args()    

if __name__ == "__main__":
    my_args = parse_arguments()
    
    shape_gdf, border_df, population_df = setup.main(my_args.region.upper()) 
    
    if my_args.viz_only:
        if not os.path.exists(config.LAST_SIMULATION_FILENAME):
            e = FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config.LAST_SIMULATION_FILENAME)
            e.strerror += ". Run the simulation locally to create it" #Add remedy to error message
            raise e
        time_data = pickle.load(open(config.LAST_SIMULATION_FILENAME, "rb"))
    else: 
        data_df = simulate.initialize(shape_gdf, border_df, population_df)    
        time_data = simulate.run(data_df)        
        pickle.dump(time_data, open(config.LAST_SIMULATION_FILENAME, 'wb'))

    time_totals = simulate.summarize(time_data)

    if not my_args.sim_only:            
        plot_data = viz.generate_plot_data(time_data, shape_gdf)
        
        #viz.make_geo_image(plot_data,10)
        #mov = viz.make_animation(plot_data, config.FPS, config.ANIMATION_DURATION)        
        #viz.save_animation(mov, config.VIDEO_FILENAME, config.FPS)

        # viz.make_image(plot_data, time_totals, 100)
        mov = viz.make_animation2(plot_data, time_totals, config.FPS, config.ANIMATION_DURATION)     
        viz.save_animation(mov, config.VIDEO_FILENAME, config.FPS)

    print("Zombie Apocalypse Simulation complete:")
    print(f"Initial population: {time_totals.at[0,'population_h']}")
    print(f"Final population: {time_totals.at[config.DAYS_TO_SIMULATE,'population_h']}")
    print(f"Maximum zed population: {max([sum(df['population_z']) for df in time_data])}")
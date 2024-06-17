import argparse
import config
import pickle
import setup
import simulate
import visualization as viz

MODE = "state"

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()    
    parser.add_argument("--sim", dest="sim_only", action="store_true", default=False,
                           help="Simulation only")
    parser.add_argument("--viz", dest="viz_only", action="store_true", default=False,
                           help="process the full dataset")
    return parser.parse_args()    

if __name__ == "__main__":
    my_args = parse_arguments()
    
    shape_gdf, border_df, population_df = setup.main(MODE) 
    
    if my_args.viz_only:
        time_data = pickle.load(open(config.LAST_SIMULATION_FILENAME, "rb"))
    else: 
        data_df = simulate.initialize(shape_gdf, border_df, population_df)    
        time_data = simulate.run(data_df)        
        pickle.dump(time_data, open(config.LAST_SIMULATION_FILENAME, 'wb'))

    if not my_args.sim_only:    
        plot_data = viz.generate_plot_data(time_data, shape_gdf)
        # ani.make_image(plot_data,500)
        mov = viz.make_animation(plot_data, config.FPS, config.ANIMATION_DURATION)
        viz.save_animation(mov, config.VIDEO_FILENAME, config.FPS)

    print("Zombie Apocalypse Simulation complete")
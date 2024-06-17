import argparse
import config
import errno
import os
import pickle
import setup
import simulate
import visualization as viz

MODE = "state"

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()    
    parser.add_argument("--sim", dest="sim_only", action="store_true", default=False,
                           help="Flag to run only the simulation without visualization")
    parser.add_argument("--viz", dest="viz_only", action="store_true", default=False,
                           help="Flag to visualize the last simulation without rerunning it")
    return parser.parse_args()    

if __name__ == "__main__":
    my_args = parse_arguments()
    
    shape_gdf, border_df, population_df = setup.main(MODE) 
    my_args.viz_only = True
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

    if not my_args.sim_only:    
        plot_data = viz.generate_plot_data(time_data, shape_gdf)
        # ani.make_image(plot_data,500)
        mov = viz.make_animation(plot_data, config.FPS, config.ANIMATION_DURATION)
        viz.save_animation(mov, config.VIDEO_FILENAME, config.FPS)

    print("Zombie Apocalypse Simulation complete")
import os

class Settings:
    def __init__(self):
        self.simulation_resolution = "state"
        self.outbreak_region = ["42007", "42019", "42"]
        self.outbreak_size = 20 #Number of zeds to start with. Enter a number bewteen 0-1 to make the start a fraction of the existing population
        self.initial_escape_chance_h = 0.5
        self.final_escape_chance_h = 0.99
        self.initial_escape_chance_z = 0.99
        self.final_escape_chance_z = 0.2
        self.escape_learning_rate_h = 1
        self.escape_learning_threshold_h = 1
        self.combat_learning_rate_h = 0.5
        self.combat_learning_threshold_h = 10
        self.zed_speed = 1 #mph
        self.encounter_distance = 30 #ft
        self.simulation_length = 35     
        self.video_filename = "Zombie Apocalypse Simulation.gif"
        self.plot_title = "Zombie Apocalypse Simulator"
        self.visuzalize_geo_data = True
        self.visuzalize_bar_data = False
        self.visuzalize_line_data = False
        self.show_image = False
        self.image_frame = 200
        self.make_animation = True
        self.fps = 10 
        self.animation_duration = 30 #seconds
        self.time_progression = "lin" #Must be "lin" or "log"
        self.base_colormap = [[1.0, 0.0, 0.1, 1.0],
                              [0.8, 0.8, 0.2, 1.0],
                              [0.0, 1.0, 0.1, 1.0]]
        self.color_slices = 64
        self.alpha_slices = 32

    def get_plot_types(self) -> list[str]:
        plot_types = []
        if self.visuzalize_geo_data:
            plot_types.append("geo")
        if self.visuzalize_bar_data:
            plot_types.append("bar")
        if self.visuzalize_line_data:
            plot_types.append("line")
        return plot_types

class Filepaths:
    def __init__(self):
        self.data_directory = "./data"
        self.shape_directory = os.path.join(self.data_directory,"shapefiles")
        self.neighbor_directory = os.path.join(self.data_directory,"neighbors")
        self.population_directory = os.path.join(self.data_directory,"populations")  
        self.county_shapefile_filename = "counties_shapefile.shp"
        self.state_shapefile_filename = "states_shapefile.shp"
        self.county_neighbors_filename = "counties_neighbors.json"
        self.state_neighbors_filename = "states_neighbors.json"
        self.county_populations_filename = os.path.join(self.population_directory,"county_populations.csv")
        self.last_simulation_filename = os.path.join(self.data_directory,"last_simulation.sim")
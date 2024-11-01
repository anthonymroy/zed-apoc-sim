import os

class Settings:
    def __init__(self):
        self.set_test_scenario()

    def set_test_scenario(self):
        self.simulation_resolution = "state"
        self.outbreak_region = ["US"]
        self.outbreak_size = 1000 #Number of zeds to start with. Enter a number bewteen 0-1 to make the start a fraction of the existing population
        self.initial_escape_chance_h = 0.25
        self.final_escape_chance_h = 0.5
        self.initial_escape_chance_z = 0.99
        self.final_escape_chance_z = 0.25
        self.escape_learning_threshold_h = 50
        self.combat_learning_threshold_h = 500
        self.zed_speed = 1 #mph
        self.encounter_distance = 6 #ft
        self.simulation_length = 365     
        self.video_filename = "Zombie Apocalypse Simulation.gif"
        self.plot_title = "Zombie Apocalypse Simulator"
        self.visuzalize_geo_data = True
        self.visuzalize_bar_data = False
        self.visuzalize_line_data = True
        self.show_image = False
        self.image_frame = 10
        self.make_animation = True
        self.fps = 4
        self.animation_duration = 10 #seconds
        self.time_progression = "lin" #Must be "lin" or "log"        
        self.color_slices = 64
        self.alpha_slices = 32

    def set_scenario1(self):
        self.simulation_resolution = "county"
        self.outbreak_region = ["42007", "42019", "42059", "42073", "42125", "39029"]
        self.outbreak_size = 0.000131 #Number of zeds to start with. Enter a number bewteen 0-1 to make the start a fraction of the existing population
        self.initial_escape_chance_h = 0.25
        self.final_escape_chance_h = 0.95
        self.initial_escape_chance_z = 0.95
        self.final_escape_chance_z = 0.1
        self.escape_learning_threshold_h = 5
        self.combat_learning_threshold_h = 10
        self.zed_speed = 1.5 #mph
        self.encounter_distance = 6 #ft
        self.simulation_length = 730    
        self.video_filename = "Zombie Apocalypse Simulation.gif"
        self.plot_title = "Zombie Apocalypse Simulator"
        self.visuzalize_geo_data = True
        self.visuzalize_bar_data = False
        self.visuzalize_line_data = True
        self.show_image = False
        self.image_frame = 10
        self.make_animation = True
        self.fps = 5
        self.animation_duration = 15 #seconds
        self.time_progression = "lin" #Must be "lin" or "log"            

    def set_scenario2(self):
        self.simulation_resolution = "county"
        self.outbreak_region = ["55079"]
        self.outbreak_size = 1 #Number of zeds to start with. Enter a number bewteen 0-1 to make the start a fraction of the existing population
        self.initial_escape_chance_h = 0.1
        self.final_escape_chance_h = 0.75
        self.initial_escape_chance_z = 0.6
        self.final_escape_chance_z = 0.2
        self.escape_learning_threshold_h = 2
        self.combat_learning_threshold_h = 10
        self.zed_speed = 15 #mph
        self.encounter_distance = 6 #ft
        self.simulation_length = 730     
        self.video_filename = "Zombie Apocalypse Simulation.gif"
        self.plot_title = "Zombie Apocalypse Simulator"
        self.visuzalize_geo_data = True
        self.visuzalize_bar_data = False
        self.visuzalize_line_data = True
        self.show_image = False
        self.image_frame = 10
        self.make_animation = True
        self.fps = 5
        self.animation_duration = 15 #seconds
        self.time_progression = "lin" #Must be "lin" or "log"     
        
    def set_scenario3(self):
        self.simulation_resolution = "county"
        self.outbreak_region = ["US"]
        self.outbreak_size = 0.000102 #Number of zeds to start with. Enter a number bewteen 0-1 to make the start a fraction of the existing population
        self.initial_escape_chance_h = 0.25
        self.final_escape_chance_h = 0.95
        self.initial_escape_chance_z = 0.95
        self.final_escape_chance_z = 0.1
        self.escape_learning_threshold_h = 5
        self.combat_learning_threshold_h = 10
        self.zed_speed = 1.5 #mph
        self.encounter_distance = 6 #ft
        self.simulation_length = 730     
        self.video_filename = "Zombie Apocalypse Simulation.gif"
        self.plot_title = "Zombie Apocalypse Simulator"
        self.visuzalize_geo_data = True
        self.visuzalize_bar_data = False
        self.visuzalize_line_data = True
        self.show_image = False
        self.image_frame = 10
        self.make_animation = True
        self.fps = 5
        self.animation_duration = 15 #seconds
        self.time_progression = "lin" #Must be "lin" or "log"     
        
    def get_plot_types(self) -> list[str]:
        plot_types = []
        if self.visuzalize_geo_data:
            plot_types.append("geo")
        if self.visuzalize_bar_data:
            plot_types.append("bar")
        if self.visuzalize_line_data:
            plot_types.append("line")
        return plot_types
    
    def echo(self):
        print(f"days = {self.simulation_length}")
        print(f"duration = {self.animation_duration}")
        print(f"frame = {self.image_frame}")
        print(f"fps = {self.fps}")        
        print(f"image = {self.show_image}")
        print(f"video = {self.make_animation}")
        print(f"region = {self.outbreak_region}")
        print(f"resolution = {self.simulation_resolution}")
        print(f"size = {self.outbreak_size}")

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

import os

class Settings:
    def __init__(self):
        self.simulation_resolution = "state"
        self.outbreak_region = ["42"]
        self.outbreak_size = 0.0001 #Number of zeds to start with. Enter a number bewteen 0-1 to make the start a fraction of the existing population
        self.initial_escape_chance_h = 0.35
        self.final_escape_chance_h = 0.95
        self.initial_escape_chance_z = 0.95
        self.final_escape_chance_z = 0.1
        self.escape_learning_rate_h = 1
        self.escape_learning_threshold_h = 3
        self.combat_learning_rate_h = .5
        self.combat_learning_threshold_h = 20
        self.zed_speed = 1 #mph
        self.encounter_distance = 30 #ft
        self.simulation_length = 50     
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

# default_simulation_parameters = {        
#     'days to simulate':50,    
#     'resolution':'state',
#     'outbreak region':['42'],
#     'outbreak_size':0.0001, #Number of zeds to start with. Enter a number bewteen 0-1 to make the start a fraction of the existing population
#     'initial human escape chance': 0.35,
#     'final human escape_chance': 0.95,
#     'human escape learning 50 percent threshold':3,
#     'initial zed escape chance': 0.35,
#     'final zed escape_chance': 0.95,
#     'human combat learning 50 percent threshold':20,
#     'zed_speed':1, #mph
#     'encounter_distance':30, #ft 
# }

default_visualization_parameters = {        
    'plot title':'Zombie Apocalypse Simulator',
    'visuzalize geodata':True,
    'visuzalize bar graph':False,
    'visuzalize line graph':True,
    'show graph':False,
    'show animation':True,
    'animation duration':15, #seconds
    'fps':5,
    'time step type':'lin', #Must be "lin" or "log"
    'base_colormap':[[1.0, 0.0, 0.1, 1.0],
                    [0.8, 0.8, 0.2, 1.0],
                    [0.0, 1.0, 0.1, 1.0]],
    'color slices':64,
    'alpha slices':32
}

default_filename_parameters = {
    'data directory':"./data",
    'shape subdirectory':"shapefiles",
    'neighbor subdirectory':"neighbors",
    'population subdirectory':"populations", 
    'county shapefile filename':"counties_shapefile.shp",
    'state shapefile filename': "states_shapefile.shp",
    'county neighbors filename': "counties_neighbors.json",
    'state neighbors filename':"states_neighbors.json",
    'county populations filename' :"county_populations.csv",
    'last simulation filename': "last_simulation.sim",
    'animation filename':"Zombie Apocalypse Simulation.gif"
}

class SimulationParameter:
    def __init__(self, display_name:str, default_value:any = None, description:str = None, units:str = None):
        self.display_name = display_name
        self.default_value = default_value
        self.description = description
        self.units = units

default_simulation_parameters = {        
    'simulation_length':SimulationParameter('Days to simulate', 50, None, 'day'),
    'simulation_resolution':SimulationParameter('Simulation resolution', 'state', 'Must be "state" or "county"', None),   
    'outbreak_region':SimulationParameter('Outbreak region', 42, 'FIPS of the outbreak location(s)', None),   
    'outbreak_size':SimulationParameter('Outbreak size', 0.0001, 'Number of zeds to start with. Enter a number bewteen 0-1 to make the start a fraction of the existing population', 'Individuals or fraction'),   
    'zed_speed':SimulationParameter('Zed speed', 1.5, 'Average speed of a zed', 'mph'),   
    'encounter_distance':SimulationParameter('Encounter distance', 30, 'Distance between a zed and human for an encounter to have occured', 'feet'),   
    'initial_escape_chance_h':SimulationParameter('Initial human escape chance', 0.35, None, 'probability'), 
    'final_escape_chance_h':SimulationParameter('Final human escape chance', 0.35, None, 'probability'),   
    'escape_learning_threshold_h':SimulationParameter('Human escape learning 50 percent threshold', 3, None, 'encounter(s)'), 
    'initial_escape_chance_z':SimulationParameter('Initial zed escape chance', 0.95, None, 'probability'), 
    'final_escape_chance_z':SimulationParameter('Final zed escape chance', 0.05, None, 'probability'),   
    'combat_learning_threshold_h':SimulationParameter('Human combat learning 50 percent threshold', 10, None, 'encounter(s)')   
}

class SimulationConfig:
    def __init__(self):
        self.parameters = {}
        self.parameters['simulation'] = default_simulation_parameters
        self.parameters['visualization'] = default_visualization_parameters
        self.parameters['filepaths'] = default_filename_parameters
        # ---- Simulation parameters ----
        self.parameters['simulation']['resolution'] = 'state'
        self.simulation_resolution = "state"
        self.outbreak_region = ["42"]
        self.outbreak_size = 0.0001 #Number of zeds to start with. Enter a number bewteen 0-1 to make the start a fraction of the existing population
        self.initial_escape_chance_h = 0.35
        self.final_escape_chance_h = 0.95
        self.initial_escape_chance_z = 0.95
        self.final_escape_chance_z = 0.1
        self.escape_learning_rate_h = 1
        self.escape_learning_threshold_h = 3
        self.combat_learning_rate_h = .5
        self.combat_learning_threshold_h = 20
        self.zed_speed = 1 #mph
        self.encounter_distance = 30 #ft
        self.simulation_length = 50     
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
        self.base_colormap = [[1.0, 0.0, 0.1, 1.0],
                              [0.8, 0.8, 0.2, 1.0],
                              [0.0, 1.0, 0.1, 1.0]]
        self.color_slices = 64
        self.alpha_slices = 32

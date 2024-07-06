import os

DATA_DIRECTORY = "./data"
SHAPE_DIRECTORY = os.path.join(DATA_DIRECTORY,"shapefiles")
NEIGHBOR_DIRECTORY = os.path.join(DATA_DIRECTORY,"neighbors")
POPULATION_DIRECTORY = os.path.join(DATA_DIRECTORY,"populations")

SHAPEFILE_FILENAME_SUFFIX = "_shapefile.shp"
NEIGHBORS_FILENAME_SUFFIX = "_neighbors.json"
STATE_POPULATIONS_FILENAME = os.path.join(POPULATION_DIRECTORY,"state_populations.csv")
COUNTY_POPULATIONS_FILENAME = os.path.join(POPULATION_DIRECTORY,"county_populations.csv")

LAST_SIMULATION_FILENAME = "last_simulation.sim"
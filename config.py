import os

INITIAL_ESCAPE_CHANCE_H = 0.7
INITIAL_ESCAPE_CHANGE_Z = 0.75
BORDER_POROSITY = 0.1
DAYS_TO_SIMULATE = 400
VIDEO_FILENAME = "Zombie Apocalypse Simulation.gif"
PLOT_TITLE = "Zombie Apocalypse Simulator"
FPS = 10
ANIMATION_DURATION = 10
TIME_PROGRESSION = "lin" #Must be "lin" or "log"
COLORMAP = "RdYlGn"
VMIN = 0
VMAX = 1

DATA_DIRECTORY = "./data"
SHAPE_DIRECTORY = os.path.join(DATA_DIRECTORY,"shapes")
STATE_SHAPE_FILENAME = os.path.join(SHAPE_DIRECTORY,"states.shp")
STATE_BORDERS_FILENAME = os.path.join(DATA_DIRECTORY,"state_borders.json")
STATE_POPULATIONS_FILENAME = os.path.join(DATA_DIRECTORY,"state_populations.csv")
COUNTY_SHAPE_FILENAME = os.path.join(SHAPE_DIRECTORY,"counties.shp")

BASE_BORDERS_FILENAME = "_borders.shp"
BASE_NEIGHBORS_FILENAME = "_neighbors.json"

COUNTY_POPULATIONS_FILENAME = os.path.join(DATA_DIRECTORY,"county_populations.csv")

LAST_SIMULATION_FILENAME = "last_simulation.sim"
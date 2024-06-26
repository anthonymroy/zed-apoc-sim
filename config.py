import os

DEFAULT_REGION = "US"
OUTBREAK_START = "Wayne"

INITIAL_ESCAPE_CHANCE_H = 0.7
INITIAL_ESCAPE_CHANGE_Z = 0.75
BORDER_POROSITY = 0.1
DAYS_TO_SIMULATE = 300
VIDEO_FILENAME = "Zombie Apocalypse Simulation.gif"
PLOT_TITLE = "Zombie Apocalypse Simulator"
FPS = 10
ANIMATION_DURATION = 20
TIME_PROGRESSION = "lin" #Must be "lin" or "log"
COLORMAP = "RdYlGn"
VMIN = 0
VMAX = 1

DATA_DIRECTORY = "./data"
SHAPE_DIRECTORY = os.path.join(DATA_DIRECTORY,"shapes")

BASE_BORDERS_FILENAME = "_borders.shp"
BASE_NEIGHBORS_FILENAME = "_neighbors.json"
STATE_POPULATIONS_FILENAME = os.path.join(DATA_DIRECTORY,"state_populations.csv")
COUNTY_POPULATIONS_FILENAME = os.path.join(DATA_DIRECTORY,"county_populations.csv")

LAST_SIMULATION_FILENAME = "last_simulation.sim"
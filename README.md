# zed-apoc-sim
Hobby project of simulating a zombie apocalypse in the United States

![](demo.gif)

## Quick Start
`python -m virtualenv venv`

`source venv/bin/activate (on Linux) OR venv\Scripts\activate (on Windows)`

`pip install -r requirements.txt`

`python .\main.py`

### Runtime instructions
<pre>
usage: Zombie Apocalypse Simulato [-help] [-load] [-run] [-setup] [-sim] [-viz] [-quit]

Commands

options:
  -help, --help    Show this help message
  -load, --load    Load the last simulation run
  -run, --run      Run the entire simulation pipeline
  -setup, --setup  Setup the simulation by downloading necessary files
  -sim, --sim      Simulation the zombie apocalypse
  -viz, --viz      Visualize the results of the simulation
  -quit, --quit    Quit the program
  </pre>
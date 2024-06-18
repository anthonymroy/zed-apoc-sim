# zed-apoc-sim
Hobby project of simulating a zombie apocalypse in the United States

## Quick Start
`python -m virtualenv venv`

`source venv/bin/activate (on Linux) OR venv\Scripts\activate (on Windows)`

`pip install -r requirements.txt`

`python .\main.py`

### Runtime instructions
<pre>
usage: main.py [-h] [--sim] [--viz] region

Simulate a zombie outbreak

positional arguments:
  region      The two-letter region to simulate. 'US' is the default value

options:
  -h, --help  show this help message and exit
  --sim       Flag to run only the simulation without visualization
  --viz       Flag to visualize the last simulation without rerunning it
  </pre>
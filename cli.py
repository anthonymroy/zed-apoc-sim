import argparse
from config import Settings

SUPPRESS = '==SUPPRESS=='

CLI = argparse.ArgumentParser(prog='Zombie Apocalypse Simulator', description='Commands', add_help=False, allow_abbrev=True)
CLI.add_argument("-help", action='help', default=SUPPRESS, help= "Show this help message")
CLI.add_argument("-load", dest="load", action="store_true", help="Load the last simulation run")
CLI.add_argument("-run", dest="run", action="store_true", help="Run the entire simulation pipeline")
CLI.add_argument("-setup", dest="setup", action="store_true", help="Setup the simulation by downloading necessary files")
CLI.add_argument("-sim", dest="sim", action="store_true", help="Simulation the zombie apocalypse")
CLI.add_argument("-viz", dest="viz", action="store_true", help="Visualize the results of the simulation")
CLI.add_argument("-quit", dest="quit", action="store_true", help="Quit the program")



class MainCLI:
    def __init__(self):
        self._parser = argparse.ArgumentParser(prog='Simulator Settings', description='Commands', add_help=False, allow_abbrev=True)
        self._parser.add_argument("-echo", dest="echo", action="store_true", help="Echo settings to screen")
        self._parser.add_argument("-help", action='help', default=SUPPRESS, help= "Show this help message")        
        self._parser.add_argument("-run", dest="run", action="store_true", help="Run simulation and visualization")
        self._parser.add_argument("-sim", dest="sim", action="store_true", help="Simulation Settings")
        self._parser.add_argument("-viz", dest="viz", action="store_true", help="Visualization settings")
        self._parser.add_argument("-quit", dest="quit", action="store_true", help="Quit the program")

    def run(self, settings:Settings):
        while True:
            text = input(">> ")
            if len(text) == 0:
                text = "--help"
            if text[0] != "-":
                text = "-"+text
            try:
                args = self._parser.parse_args(text.lower().split())
                if args.quit:
                    print("Quiting...")
                    break
                if args.echo:
                    settings.echo()
                if args.run:
                    print("Run simulation and vizualization")
                if args.sim:
                    simCLI = SimCLI()
                    simCLI.run(settings)
                    print("Main Menu:")
                if args.viz:
                    print("Run vizualization")
            except SystemExit:
                #Don't exit the program on an error
                pass

class SimCLI:
    def __init__(self):
        self._parser = argparse.ArgumentParser(prog='Simulator Settings', description='Commands', add_help=False, allow_abbrev=True)
        self._parser.add_argument("-echo", dest="echo", action="store_true", help="Echo settings to screen")
        self._parser.add_argument("-help", action='help', default=SUPPRESS, help= "Show this help message")
        self._parser.add_argument("-res", dest="resolution", action="store", help="Resolution of 'state'(default) or 'county'",
                            default=None, choices={"county", "state"})
        self._parser.add_argument("-run", dest="run", action="store_true", help="Run the simulation without visualization")
        self._parser.add_argument("-back", dest="back", action="store_true", help="Go back to main menu")

    def run(self, settings:Settings):
        print("Simulation Menu:")
        while True:
            text = input(">> ")
            if len(text) == 0:
                text = "--help"
            if text[0] != "-":
                text = "-"+text
            try:
                args = self._parser.parse_args(text.lower().split())
                if args.back:
                    print("Back to main menu...")
                    break
                if args.echo:
                    settings.echo()
                if args.run:
                    print("Run simulation only")
                if args.resolution:
                    settings.simulation_resolution = args.resolution
            except SystemExit:
                #Don't exit the program on an error
                pass
           
if __name__ == "__main__":
    my_settings = Settings()
    cli = MainCLI()
    cli.run(my_settings)
    input("Press [ENTER] to quit:")
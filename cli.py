import argparse

SUPPRESS = '==SUPPRESS=='

MainCLI = argparse.ArgumentParser(prog='Zombie Apocalypse Simulator', description='Commands', add_help=False, allow_abbrev=True)
MainCLI.add_argument("-help", action='help', default=SUPPRESS, help= "Show this help message")
MainCLI.add_argument("-load", dest="load", action="store_true", help="Load the last simulation run")
MainCLI.add_argument("-run", dest="run", action="store_true", help="Run the entire simulation pipeline")
MainCLI.add_argument("-setup", dest="setup", action="store_true", help="Setup the simulation by downloading necessary files")
MainCLI.add_argument("-sim", dest="sim", action="store_true", help="Simulation the zombie apocalypse")
MainCLI.add_argument("-viz", dest="viz", action="store_true", help="Visualize the results of the simulation")
MainCLI.add_argument("-quit", dest="quit", action="store_true", help="Quit the program")

class SimCLI:
    def __init__(self):
        self._parser = argparse.ArgumentParser(prog='Simulator Settings', description='Commands', add_help=False, allow_abbrev=True)
        self._parser.add_argument("-echo", dest="echo", action="store_true", help="Print settings to screen")
        self._parser.add_argument("-help", action='help', default=SUPPRESS, help= "Show this help message")
        self._parser.add_argument("-res", dest="resolution", action="store", help="Select a resolution of 'state'(default) or 'county'",
                            default="state", choices={"county", "state"})
        self._parser.add_argument("-run", dest="run", action="store_true", help="Run the simulation without visualization")
        self._parser.add_argument("-back", dest="back", action="store_true", help="Go back to main menu")

    def main(self):
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
                    print("echo")
                if args.run:
                    print("run")
                print(f"resolution = {args.resolution}")
            except SystemExit:
                #Don't exit the program on an error
                pass
           
if __name__ == "__main__":
    cli = SimCLI()
    cli.main()
    input("Press [ENTER] to quit:")
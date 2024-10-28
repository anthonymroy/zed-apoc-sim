

class MainCLI:
    def __init__(self, settings:Settings, filepaths:Filepaths):
        self.config = {}
        self.config['simulation'] = {}
        self.config['visualization'] = {}
        self.config['filepaths'] = {}
        
        self._settings = settings
        self._filepaths = filepaths
        self._shape_gdf = None
        self._simulation_data = None
        self._simulation_summary = None
        self._parser = argparse.ArgumentParser(prog='Simulator Settings', description='Commands', add_help=False, allow_abbrev=True)
        self._parser.add_argument("-days", dest="days", action="store", type=int ,
                            help="Number of days to simulate", default=None)
        self._parser.add_argument("-duration", dest="duration", action="store", help="Duration of the video",
                    default=None, type=float)        
        self._parser.add_argument("-echo", dest="echo", action="store_true", help="Echo settings to screen")
        self._parser.add_argument("-frame", dest="frame", action="store", help="Frames to show",
                            default=None, type=int)
        self._parser.add_argument("-fps", dest="fps", action="store", help="Frames per second",
                            default=None, type=float)        
        self._parser.add_argument("-help", action='help', default=SUPPRESS, help= "Show this help message")
        self._parser.add_argument("-image", dest="image", action="store_true", help="Make and show image")
        self._parser.add_argument("-load", dest="load", action="store_true", help="Load the last simulation run")
        self._parser.add_argument("-region", dest="region", action="store", nargs='+', 
                            help="Region(s) where outbreak starts", default=None)
        self._parser.add_argument("-resolution", dest="resolution", action="store", help="Resolution of 'state'(default) or 'county'",
                            default=None, choices={"county", "state"})
        self._parser.add_argument("-run", dest="run", action="store_true", help="Run simulation and visualization")
        self._parser.add_argument("-size", dest="size", action="store", default=None, type = float,
                                help="Number of zeds to start with. Enter a number bewteen 0-1 to make the start a fraction of the existing population")
        self._parser.add_argument("-video", dest="video", action="store_true", help="Make and save video")
        self._parser.add_argument("-viz", dest="viz", action="store_true", help="Run visualization using previous simulation")
        self._parser.add_argument("-quit", dest="quit", action="store_true", help="Quit the program")

    def run(self):
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
                if args.days:
                    self._settings.simulation_length = args.days
                if args.duration:
                    self._settings.animation_duration = args.duration               
                if args.frame:
                    self._settings.image_frame = args.frame
                if args.fps:
                    self._settings.fps = args.fps
                if args.image:
                    self._settings.show_image = True
                    self._settings.make_animation = False
                if args.load:
                    self._simulation_data, self._simulation_summary = load_simulation(self._filepaths)
                    match self._settings.simulation_resolution:
                        case "state":
                            self._shape_gdf = setup.get_states_shapefile(self._filepaths)
                        case "county":
                            self._shape_gdf = setup.get_county_shapefile(self._filepaths)
                        case _:
                            raise ValueError
                if args.region:
                    self._settings.outbreak_region = args.region
                if args.resolution:
                    self._settings.simulation_resolution = args.resolution
                if args.run:
                    self._shape_gdf, self._simulation_data, self._simulation_summary = run_simulation(self._settings, self._filepaths)
                    run_visualization(
                        self._settings,
                        self._filepaths,
                        self._shape_gdf,
                        self._simulation_data,
                        self._simulation_summary
                    )
                    print_report(self._settings, self._simulation_data, self._simulation_summary)
                if args.size:
                    self._settings.outbreak_size = args.size
                if args.video:
                    self._settings.show_image = False
                    self._settings.make_animation = True
                if args.viz:
                    run_visualization(
                        self._settings,
                        self._filepaths,
                        self._shape_gdf,
                        self._simulation_data,
                        self._simulation_summary
                    )
                    print_report(self._settings, self._simulation_data, self._simulation_summary)
                if args.echo:
                    self._settings.echo()
            except SystemExit:
                #Don't exit the program on an error
                pass

if __name__ == "__main__":
    import setup
    from config import Filepaths
    my_settings = Settings()
    my_filepaths = Filepaths()
    my_settings.outbreak_region = ["53003"]
    my_settings.simulation_resolution = "county"
    shape_gdf, nieghbors_df, population_df = setup.main(my_settings, my_filepaths)
    initial_df = initialize(shape_gdf, nieghbors_df, population_df, my_settings)
    print(initial_df.loc["53003"])
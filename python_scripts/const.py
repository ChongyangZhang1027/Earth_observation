import datetime


class constNum:
    def __init__(self):
        self.today = datetime.date.today()
        self.EARTH_RADIUS = 6378e3            # [m]
        self.AREA_LIMIT = 5e4                 # [m^2]
        self.MAX_LAT = 62.75                  # [deg], the cover area of Copernicus North Atlantic product
        self.MIN_LAT = 46
        self.MAX_LON = 13
        self.MIN_LON = -16
        self.PRODUCT_START_YEAR = 2019        # the product started from June 2019
        self.PRODUCT_END_YEAR = self.today.year
        self.PRODUCT_START_MONTH = 6
        self.GRAVITY = 9.8                    # [m/s^2]
        self.CROSS_AREA_TURBINE_SMALL = 1     # [m^2]
        self.CROSS_AREA_TURBINE_LARGE = 25    # [m^2]
        self.SEA_WATER_DENSITY = 1027         # [kg/m^3]
        self.TURBINE_EFFICIENT = 0.4
        self.DAM_EFFICIENT = 0.9
        self.LAT_RESOLUTION = 0.014           # [deg] spatial resolution of input data
        self.LON_RESOLUTION = 0.03
        self.TURBINE_COVER_AREA = 100         # [m^2]
        self.KWH_TO_J = 3600000               # unit transfer, J to kwh
        self.TIME_RESOLUTION = 3600           # [s]
        self.WIDTH_OF_GENERATOR = 1           # [m]
        self.DISTANCE_LIMIT = 5000            # [m] distance limit of the power plant away from shore

    def readFile(self, path):
        fp = open(path, 'r')
        lines = fp.readlines()
        print("enter function")
        for line in lines:
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            items = line.split()
            if items[0] == "CROSS_AREA_TURBINE_SMALL":
                self.CROSS_AREA_TURBINE_SMALL = float(items[2])
            elif items[0] == "CROSS_AREA_TURBINE_LARGE":
                self.CROSS_AREA_TURBINE_LARGE = float(items[2])
            elif items[0] == "TURBINE_EFFICIENT":
                self.TURBINE_EFFICIENT = float(items[2])
            elif items[0] == "DAM_EFFICIENT":
                self.DAM_EFFICIENT = float(items[2])
            elif items[0] == "TURBINE_COVER_AREA":
                self.TURBINE_COVER_AREA = float(items[2])
            elif items[0] == "WIDTH_OF_GENERATOR":
                self.WIDTH_OF_GENERATOR = float(items[2])
            elif items[0] == "DISTANCE_LIMIT":
                self.DISTANCE_LIMIT = float(items[2])

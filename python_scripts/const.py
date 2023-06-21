import datetime
today = datetime.date.today()

EARTH_RADIUS = 6378e3            # [m]
AREA_LIMIT = 5e4                 # [m^2]
MAX_LAT = 62.75                  # [deg], the cover area of Copernicus North Atlantic product
MIN_LAT = 46
MAX_LON = 13
MIN_LON = -16
PRODUCT_START_YEAR = 2019        # the product started from June 2019
PRODUCT_END_YEAR = today.year
PRODUCT_START_MONTH = 6
GRAVITY = 9.8                    # [m/s^2]
CROSS_AREA_TURBINE_SMALL = 0.25  # [m^2]
CROSS_AREA_TURBINE_LARGE = 4     # [m^2]
SEA_WATER_DENSITY = 1027         # [kg/m^3]
TURBINE_EFFICIENT = 0.4
LAT_RESOLUTION = 0.014           # [deg] spatial resolution of input data
LON_RESOLUTION = 0.03
TURBINE_COVER_AREA = 100         # [m^2]
KWH_TO_J = 3600000               # unit transfer, J to kwh
TIME_RESOLUTION = 3600           # [s]
WIDTH_OF_GENERATOR = 3           # [m]

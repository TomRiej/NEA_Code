

DEBUG = False

# User Interface
WINDOW_SIZE = (650,500)
BG_COLOUR = "#FFFFFF"
RED = "#FF0000"
GREEN = "#20CC20"  
BLUE = "#0e6cc9"
FONT = "Verdana"
PATH = "/Users/Tom/Desktop/Education/CS-A-level/NEA/Media/"
LOGO_NAME = "FormulAI_Logo.png"
REFRESH_AFTER = 1 # constantly refresh
SMALL_TIME_DELAY = 2000 # 2 seconds
EMPTY = ""
INVALID = -1


# Camera
GREEN_RANGE =   [[60, 170, 150], [110, 220, 200]]
ORANGE_RANGE =  [[35, 140, 190], [ 70, 180, 235]]
BLUE_RANGE =    [[254, 81,  20], [254,  81,  20]]
LOADING_DOTS_X_COORDS = [932, 959, 985]
TRACK_STRAIGHT = 0
TRACK_TURN = 1
SAMPLE_ITERATIONS = 50
NUM_TRACK_LOCATIONS = 6
NUM_CAR_PIXELS_RANGE = [3500, 5500] # optimum car pixels ~= 4200
MILLIMETERS_PER_PIXEL = 2000 / 1442 # track is 2000mm wide. track is 1432 pixels wide on the camera


# Hardware
SERIAL_PORT_NAME = "/dev/tty.usbmodem14101"
SERIAL_BAUD_RATE = 9600
SERIAL_READ_TIMEOUT = 0.5

  # Input
DISTANCE_BETWEEN_MAGNETS = 88 # mm
NUM_HALL_SENSORS = 2
START_FINISH_SENSOR_NUMBER = "2" # must be a str
VALIDATION_TIMEOUT = 10 # seconds
HALL_VS_CAMERA_SPEED_TOLERANCE = 200 # +- 200 mm/s = 20cm/s
MAX_TIME_BETWEEN_MEASUREMENTS = 0.05 # s

  # Output
SERVO_RANGE = [30, 90]
SLOW_ANGLE = 62


# Q Learning
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9 
MAX_EXPLORING_ITERATIONS = 1000000
STATE_SHAPE = [[0, 0, 0], [1, 99, 999], [1, 30, 100]]
ACTION_SHAPE = [30, 90, 2]
WAITING_TIME_FOR_ACTION = 0.3 # second
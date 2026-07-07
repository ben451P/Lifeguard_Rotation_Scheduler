import os
from dotenv import load_dotenv

load_dotenv()

EXAMPLE_USERNAME = os.getenv("EXAMPLE_USERNAME")
EXAMPLE_PASSWORD = os.getenv("EXAMPLE_PASSWORD")

LOG_PATH = "debug/log.txt"

ROTATION_CYCLE = {"data":[
    "Kiddie", "Dive", "Main", "Break", "First Aid", "Slide",
    "Main2", "Rover", "Lap", "See Manager", "Bathroom Break"
]}

STATION_IMPORTANCE_DESCENDING = {"data":[
    "Bathroom Break", "Rover", "Main2", "See Manager", "Slide",
    "Kiddie", "First Aid", "Dive", "Lap", "Main", "Break"
]}

SHIFTS = {"data":[
    #[name, start, end, attendance, lunch break]
    ["Guard A", "09:45", "15:30", True, False],
    ["Guard B", "09:45", "15:30", True, False],
    ["Guard C", "10:30", "16:00", True, False],
    ["Guard D", "10:30", "16:00", True, False],
    ["Guard E", "11:00", "20:00", True, False],
    ["Guard F", "11:00", "20:00", True, False],
    ["Guard G", "11:00", "20:00", True, False],
    ["Guard H", "11:00", "20:00", True, False],
    ["Guard I", "13:00", "19:00", True, False],
    ["Guard J", "14:00", "20:00", True, False],
    ["Guard K", "14:00", "20:00", True, False],
    ["Guard L", "14:00", "20:00", True, False],
    ["Guard M", "15:30", "20:00", True, False],
]}
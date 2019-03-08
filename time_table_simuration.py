"""
Timetable simulation.

-- CSV FORMAT --
A 10:00 10:10
B 10:05 10:15
C 10:07 10:17

column1    : Station name
column2... : time table
"""
import sys
import csv
import datetime
import time

DIRECTION_FORWARD  = 1
DIRECTION_BACKWORD = 2

stations    = []
time_tables = []
sections    = []

class SectionInfo:
    """ Section info"""

    def __init__(self, index, before_station, before_time, next_station, next_time, direction):
        self.index = index
        self.before_station = before_station
        self.before_time = datetime.datetime.strptime(before_time, '%H:%M')
        self.next_station = next_station
        self.next_time   = datetime.datetime.strptime(next_time, '%H:%M')
        self.direction = direction
        
    def contain_time(self, time):
        if self.before_time <= time and time <= self.next_time:
            return True
        return False

    def propotion(self, time):
        time_span = self.next_time - self.before_time
        past_time = self.next_time - time
        rate = 1.0 - (past_time / time_span)
        if self.direction == DIRECTION_BACKWORD:
            rate = 1.0 - rate
        return rate

    def write_position(self, time, interval):
        position = self.propotion(time)
        total_len = interval + 1
        write_position = total_len * position
        return int(write_position)

    def train_icon(self):
        if self.direction == DIRECTION_FORWARD:
            return ">"
        else:
            return "<"

    def __str__(self):
        return str(self.index) + " " + self.before_station + "[" + self.before_time.strftime('%Y/%m/%d %H:%M:%S') + "]" + ":" + self.next_station + "[" + self.next_time.strftime('%Y/%m/%d %H:%M:%S') + "]"

""" Write Station and Train position """
def write_train_position(stations, sections, time):
    station_interval = 4
    total_stations = len(stations)
    rail_length = (total_stations + total_stations * station_interval) - station_interval
    station_rail  = ["-"] * rail_length
    forward_rail  = [" "] * rail_length
    backward_rail = [" "] * rail_length

    # Insert station position to the station_rail
    for i in range(0, len(stations)):
        station_pos = i * station_interval + i
        station_rail[station_pos] = stations[i]

    # Insert train position to the forward/backward rail
    for section in sections:
        section_position = section.index
        train_position = station_interval * section_position + section_position + section.write_position(time, station_interval)
        if section.direction == DIRECTION_FORWARD:
            forward_rail[train_position] = section.train_icon()
        else:
            backward_rail[train_position] = section.train_icon()

    # Write station and train
    for i in range(len(station_rail)):
        sys.stdout.write(station_rail[i])
    sys.stdout.write("\n")
    for i in range(len(forward_rail)):
        sys.stdout.write(forward_rail[i])
    sys.stdout.write("\n")
    for i in range(len(backward_rail)):
        sys.stdout.write(backward_rail[i])
    sys.stdout.write("\n")

def load_forward_direction():
    # read data form csv file
    with open('./timetable/forward.csv') as f:
        reader = csv.reader(f, delimiter=' ')
        index = 0
        for row in reader:
            time_tables.append(row)
            stations.append(row[0])

    # create section info
    for j in range(1, len(time_tables[0])):
        for index in range(0, len(time_tables) - 1):
            before_station = time_tables[index][0]
            before_time    = time_tables[index][j]
            next_station   = time_tables[index + 1][0]
            next_time      = time_tables[index + 1][j]
            section_info = SectionInfo(index, before_station, before_time, next_station, next_time, DIRECTION_FORWARD)
            sections.append(section_info)

def load_backword_direction():
    # read data form csv file
    stations = []
    time_tables = []
    with open('./timetable/backward.csv') as f:
        reader = csv.reader(f, delimiter=' ')
        index = 0
        for row in reader:
            time_tables.append(row)
            stations.append(row[0])

    total_stations = len(stations) - 1

    # create section info
    for j in range(1, len(time_tables[0])):
        for index in range(0, len(time_tables) - 1):
            before_station = time_tables[index][0]
            before_time    = time_tables[index][j]
            next_station   = time_tables[index + 1][0]
            next_time      = time_tables[index + 1][j]
            section_info = SectionInfo(total_stations - (index+1), before_station, before_time, next_station, next_time, DIRECTION_BACKWORD)
            sections.append(section_info)

def load_and_show_station_name():
    with open('./timetable/statiosn_name.txt') as f:
        sys.stdout.write(f.read())

"""
Simulate train position
"""
def simulation_mode(start_time):
    check_date = datetime.datetime.strptime(start_time, '%H:%M:%S')
    end_time   = datetime.datetime.strptime('23:59:00', '%H:%M:%S')

    while(check_date < end_time):
        time_str = check_date.strftime('%H:%M:%S')
        points = []
        for info in sections:
            if info.contain_time(check_date):
                points.append(info)
        print(time_str)
        write_train_position(stations, points, check_date);
        sys.stdout.flush()
        check_date += datetime.timedelta(seconds=30)
        time.sleep(1);
        # clear console 4 line, time(one line) + station and rail (3 line)
        sys.stdout.write("\033[4F")

"""
Show Current time position
Update 10 second.
"""
def real_time_mode():
    while(True):
        current_time = datetime.datetime.now()
        time_str = current_time.strftime('%H:%M:%S')
        print(time_str)
        check_date = datetime.datetime.strptime(time_str, '%H:%M:%S')
        points = []
        for info in sections:
            if info.contain_time(check_date):
                points.append(info)
        write_train_position(stations, points, check_date);
        time.sleep(10);
        # clear console 4 line, time(one line) + station and rail (3 line)
        sys.stdout.write("\033[4F")

# __main__

load_forward_direction()
load_backword_direction()
load_and_show_station_name()

#real_time_mode()
simulation_mode('10:08:00')


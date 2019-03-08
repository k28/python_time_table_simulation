
import sys
import csv
import datetime
import time

DIRECTION_FORWARD  = 1
DIRECTION_BACKWORD = 2

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



def writeTrainPosition(stations, sections, time):
    station_interval = 4
    # Write Station Point
    for i in stations:
        sys.stdout.write(i)
        for j in range(0,station_interval):
            sys.stdout.write("-")
    #for j in range(0,station_interval + 1):
    #    sys.stdout.write("\033[1D\033[K")
    #    sys.stdout.flush()
    sys.stdout.write("\n")

    total_stations = len(stations)
    rail_length = total_stations + total_stations * station_interval
    forward_rail  = ["-"] * rail_length
    backward_rail = ["-"] * rail_length

    for section in sections:
        #print(section)
        section_position = section.index
        # test --
        # print(str(station_interval) + ":" + str(section_position) + ":" + str(section.write_position(time, station_interval)))
        train_position = station_interval * section_position + section_position + section.write_position(time, station_interval)
        if section.direction == DIRECTION_FORWARD:
            forward_rail[train_position] = section.train_icon()
        else:
            backward_rail[train_position] = section.train_icon()
        # test --
        # for i in range(0, total_stations):
        #     if section.index != i:
        #         for j in range(0,station_interval + 1):
        #             sys.stdout.write(" ")
        #     else:
        #         write_position = section.write_position(time, station_interval)
        #         #print(str(write_position))
        #         for j in range(0,station_interval + 1):
        #             if j != write_position:
        #                 sys.stdout.write(" ")
        #             else:
        #                 sys.stdout.write(section.train_icon())
        # sys.stdout.write("\n")
        
    for i in range(len(forward_rail)):
        sys.stdout.write(forward_rail[i])
    sys.stdout.write("\n")
    for i in range(len(backward_rail)):
        sys.stdout.write(backward_rail[i])
    sys.stdout.write("\n")

stations = []
time_tables = []
sections = []

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
           #print(before_station + ":" + before_time + ":" + next_station + ";" + next_time)
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

def simulation_mode():
    check_date = datetime.datetime.strptime('08:15:00', '%H:%M:%S')
    end_time   = datetime.datetime.strptime('23:59:00', '%H:%M:%S')

    while(check_date < end_time):
        time_str = check_date.strftime('%H:%M:%S')
        print(time_str)
        points = []
        for info in sections:
            if info.contain_time(check_date):
                points.append(info)
        writeTrainPosition(stations, points, check_date);
        check_date += datetime.timedelta(seconds=30)
        time.sleep(1);

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
        writeTrainPosition(stations, points, check_date);
        time.sleep(10);
        print(chr(27) + "[2J")


# __main__

load_forward_direction()
load_backword_direction()

#real_time_mode()
simulation_mode()


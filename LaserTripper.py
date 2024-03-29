from collections import deque, namedtuple
from pprint import pprint
import time

from data_transfer import NUM_LASERS
from utils import say


MAX_DEQUE_LENGTH = 4000
LASER_SAMPLE_SECS = 0.5
VALID_LASERS = [10]

LaserSample = namedtuple('LaserSample', ('timestamp', 'reading'))
LaserTriggerTuple = namedtuple('LaserTriggerTuple', ('instant_value', 'instant', 'debounced'))


class LaserTripper():
    def __init__(self, num_lasers):
        self.laser = [None] * num_lasers
        self.calibrations = []
        for d in range(NUM_LASERS):
            self.calibrations.append({
            'low_value': None,
            'high_value': None,
            'threshold': None,
            'in_use': False,
            'deque': deque(maxlen=MAX_DEQUE_LENGTH)
        })

    def calibrate(self, data_transferer, num_cycles, off_seconds=0.1, on_seconds=0.1):
        def get_avg_readings(data_transferer, num_lasers, seconds):
            readings = [[] for d in range(num_lasers)]
            end_time = time.time() + seconds
            while time.time() < end_time:
                __, laser_infos, __ = data_transferer.get_all_data()
                for idx, laser_reading in enumerate(laser_infos):
                    if laser_reading is None:
                        continue
                    readings[idx].append(laser_reading)
            # print(readings)
            avg_readings = [sum(reading) // len(reading) for reading in readings]
            return avg_readings, readings

        say('Calibrating...')
        print('Resetting the calibrations...')
        for calibration in self.calibrations:
            calibration['low_value'] = None
            calibration['high_value'] = None

        print('doing the calibrations...')
        for d in range(num_cycles):
            which_value = ['low_value', 'high_value'][d % 2]
            input(f'Block the laser and hit enter to calibrate {which_value}- ')
            avg_readings, all_readings = get_avg_readings(data_transferer, len(self.laser), off_seconds)
            for idx, avg_reading in enumerate(avg_readings):
                if self.calibrations[idx][which_value] is None:
                    self.calibrations[idx][which_value] = avg_reading
                else:
                    self.calibrations[idx][which_value] = (self.calibrations[idx][which_value] + avg_reading) // 2
            print(f'average {which_value} =', self.calibrations)
        for idx, cal in enumerate(self.calibrations):
            if VALID_LASERS and idx in VALID_LASERS:
                cal['in_use'] = False

            low = cal['low_value']
            high = cal['high_value']
            diff = high - low
            
            in_use = True

            ratio = None
            if low == 0 and diff < 100:
                in_use = False
            elif low > high:
                in_use = False
            elif high == 0:
                in_use = False
            elif high < 200:
                in_use = False
            else:
                ratio = low / high
                if ratio > 0.8:
                    in_use = False

            p66 = int(low + (diff) * 0.66)
            p75 = int(low + (diff) * 0.75)
            cal['in_use'] = in_use
            if in_use:
                cal['threshold'] = p75
            print(f'{idx} low / high / diff / ratio / 66% / 75% / in_use = {low} / {high} / {diff} / {ratio} / {p66} / {p75} / {cal["in_use"]}')

        for idx, c in enumerate(self.calibrations):
            print(f'Laser {idx} is in-use - {c["in_use"]}')


    def _procees_queues(self, laser_readings):
        now = time.time()
        cutoff = now - LASER_SAMPLE_SECS
        debounced_data = []
        for idx, c in enumerate(self.calibrations):
            laser_reading = laser_readings[idx]
            if not c['in_use']:
                debounced_data.append(LaserTriggerTuple(None, None, None))
                continue

            if laser_reading is None:
                debounced_data.append(LaserTriggerTuple(None, None, None))
                continue

            q = c['deque']

            # Get rid of values that are too old
            while q and q[0].timestamp < cutoff:
                q.popleft()

            instant_info = laser_reading > c['threshold']

            # Add the latest value
            c['deque'].append(LaserSample(time.time(), instant_info))

            # Currently more that 50% means it is on
            readings = [x.reading for x in q]
            debounced_info = readings.count(True) > (len(q) / 2)
            # print(readings.count(True), readings.count(False), readings.count(None), len(q)) #, q)
            debounced_data.append(LaserTriggerTuple(laser_reading, instant_info, debounced_info))
        return debounced_data

    def get_readings(self, laser_infos):
        return self._procees_queues(laser_infos)

    def get_readings_self_contained_loop_for_testing(self, data_transferer):
        from data_transfer import clear_screen, clear_screen2
        while True:
            __, laser_infos, __ = data_transferer.get_all_data()
            clear_screen2()
            infos = self._procees_queues(laser_infos)
            for idx, (instant_info, debounced_info) in enumerate(infos):
                print(f'{idx:02} - {str(instant_info):5} - {str(debounced_info):5}')
                continue

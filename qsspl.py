import numpy as np
import pandas as pd
import csv
from time import sleep

#import from computer
from PLQY.sr830 import SR830
from PLQY.ldc502 import LDC502
plus_minus = u"\u00B1"

class QSSPL:
    def __init__(self):
        self.ldc = LDC502("COM24")
        print('\nConnected to Laser Diode Driver')
        self.lia = SR830('GPIB0::8::INSTR') # connect to the lock-in amplifier
        print('\nConnected to Lock-in Amplifier')
        self.laser_wl = 532
        self.LASERSTABILIZETIME = 10.0
        self.laser_current = self.ldc.get_laser_current()
        self.laser_temp = self.ldc.get_laser_temp()

    def take_qsspl(self, sample_name = "sample", min_current = 300, max_current = 800, step = 20, num_measurements = 5)
        print('\nSetting Laser Current and waiting to stabilize...')
        data = {}

        for current_setting in np.arange(min_current, max_current, step):
            voc_list = []
            if np.abs(self.ldc.get_laser_current() - current_setting) > 2:
                self.ldc.set_laserCurrent(current_setting)
                sleep(self.LASERSTABILIZETIME)
            else:
                self.ldc.set_laserCurrent(current_setting)

            print('\nLaser Current Set and Stable at {current_setting}.')
            sleep(1)
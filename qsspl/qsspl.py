import numpy as np
import pandas as pd
import csv
from time import sleep

#import from computer
from PLQY.sr830 import SR830
from PLQY.ldc502 import LDC502
# Import locally from computer

try:
    from PLQY.ldc502 import LDC502
except ImportError:
    raise ImportError("Failed to import LDC502 from PLQY.ldc502. Ensure the module is installed and accessible.")

try:
    from PLQY.sr830 import SR830
except ImportError:
    raise ImportError("Failed to import control3 from PLQY.sr830. Ensure the module is installed and accessible.")
    

plus_minus = u"\u00B1"

# Version 1.0

class QSSPL:
    ''' A class to take Quasi-steady-state photoluminescence measurements '''

    class CustomError(Exception):
        pass

    def __init__(self):
        # Initialize the hardware
        # Connect to the laser
        try: 
            self.ldc = LDC502("COM24")
            self.laser_current = self.ldc.get_laser_current()
            self.laser_temp = self.ldc.get_laser_temp()
            self.laser_wl = 532
            self.ldc.set_laserOn()
            self.ldc.set_tecOn()
            self.ldc.set_modulationOff()
            self.ldc.set_laserCurrent(400)
            print("Laser connected and set to safe level to set up device testing.")
        except Exception as e:  
            print("Error while trying to connect to the Laser: ", e)
            print("Please ensure the Laser is connected to COM24 and try again.")
            raise self.CustomError("Laser Connection Error")


       # Connect to the Lock-in
        try:
            self.lia = SR830('GPIB0::8::INSTR')
            print("Lock-in SR850 connected.")
        except Exception as e:
            print("Error while trying to connect to the SR850: ", e)
            print("Please ensure the Keithley is connected to 'GPIB1::22::INSTR' and try again.")
            raise self.CustomError("Lock-in Connection Error")

    # Method to configure the hardware
    def _configure(self, n_wires = 2):
        self.ldc.set_laserOn()
        self.ldc.set_tecOn()
        self.ldc.set_modulationON()
        print("Laser, TEC, and modulation turned on.")


    def take_qsspl(self, sample_name = "sample", min_current = 300, max_current = 800, step = 20, num_measurements = 5)
        print('\nSetting Laser Current and waiting to stabilize...')
        print('\This is a test function')
        data = {}


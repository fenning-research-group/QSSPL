import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from time import sleep

# Version 1.3 - function dev

# Import local modules for hardware control

try:
    from PLQY.ldc502 import LDC502
except ImportError:
    raise ImportError("Failed to import LDC502 from PLQY.ldc502. Ensure the module is installed and accessible.")

try:
    from PLQY.sr830 import SR830
except ImportError:
    raise ImportError("Failed to import control3 from PLQY.sr830. Ensure the module is installed and accessible.")

try:
    from PLQY.ell6_slider import FilterSlider
except ImportError:
    raise ImportError("Failed to import FilterSlider from PLQY.ell6_slider. Ensure the module is installed and accessible.")

plus_minus = u"\u00B1"

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
            self.laser_wl = 532 #nm
            self.ldc.set_laserOn()
            self.ldc.set_tecOn()
            self.ldc.set_modulationOn()
            self.ldc.set_laserCurrent(380)
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
        
        # Connect to the Filter Slider
            self.filter = FilterSlider()
            print("Filter slider connected.")
        except Exception as e:
            print("Error while trying to connect to the Filter Slider: ", e)
            print("Please ensure the Filter Slider is connected and try again.")
            raise self.CustomError("Filter Slider Connection Error")    
        
    # Method to set the laser current modulation
    def _current_mod(self, max_current):
        ''' Method to modulate the current of the laser '''
        turn_on = 295.5
        diff = max_current-turn_on
        setpoint = 0.5*(turn_on+max_current)
        voltage = (2**-0.5)*(diff*0.5)/100
        return voltage, setpoint

    # Method to configure the hardware
    def _configure(self):
        self.ldc.set_laserOn()
        self.ldc.set_tecOn()
        self.ldc.set_modulationOn()
        print("Laser, TEC, and modulation turned on.")


    # Method to take QSSPL measurements- function dev in progress
    def take_qsspl(self, sample_name = "sample"):
        print('This is a test function')

        # Configure the hardware
        self._configure()

        # Set up the data frame
        currents = 294.3+np.logspace(np.log10(300-294.3), np.log10(700-294.3), 41)
        # change currents to arguments

        for curr in currents:
            data = pd.DataFrame()
            v_set, I_set = self._current_mod(curr)
            self.lia.sine_voltage = v_set
            self.ldc.set_laserCurrent(I_set)

            # Adjust delays based on current
            if curr < 350:
                sleep_factor = 1
                self.lia.time_constant = 1
            else:
                sleep_factor = 0.1
                self.lia.time_constant = 0.1

            # Sweep frequency and take measurements
            for freq in np.linspace(1e4, 8e4, 15):
                self.lia.frequency = freq

                # Measure PL signal
                self.filter.right() # Longpass in
                sleep(10*sleep_factor)
                self.lia.quick_range()
                temp = []
                sleep(2*sleep_factor)
                for i in tqdm(range(10)):
                    temp.append(self.lia.get_theta()) # Get phase shift
                    sleep(sleep_factor)

                # Measure laser signal
                self.filter.left() # Longpass out
                sleep(10*sleep_factor)
                self.lia.quick_range()
                temp2 = []
                sleep(2*sleep_factor)
                for i in tqdm(range(10)):
                    temp2.append(self.lia.get_theta())
                    sleep(sleep_factor)
                
                #Store the data
                data[f'Laser_{freq}'] = temp
                data[f'Diff_{freq}'] = np.abs(data[f'Laser_{freq}'] -  data[f'PL_{freq}'])
                print(f'Difference: {np.mean(data[f"Diff_{freq}"])}+-{np.std(data[f"Diff_{freq}"])}')

            # Save the data
            self.lia.frequency = 1e4
            data.to_csv(f'TR_{freq}_{curr:0.2f}.csv', index = False)
            plt.plot(np.linspace(1e4, 8e4, 15), data[[c for c in data.columns if 'Diff' in c]].mean())
            plt.show()







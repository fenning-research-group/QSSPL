import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from time import sleep

# Version 1.9 - fygen updates

# Import local modules for hardware control

try:
    from PLQY.ldc502 import LDC502
except ImportError:
    raise ImportError("Failed to import LDC502 from PLQY.ldc502. Ensure the module is installed and accessible.")

try:
    from PLQY.ell6_slider import FilterSlider
except ImportError:
    raise ImportError("Failed to import FilterSlider from PLQY.ell6_slider. Ensure the module is installed and accessible.")

try:
    from PLQY.stepper_control import Stepper
except ImportError:
    raise ImportError("Failed to import Stepper from PLQY.stepper_control. Ensure the module is installed and accessible.")

try:
    from QSSPL.sr850 import SR830
except ImportError:
    raise ImportError("Failed to import sr850 from QSSPL.sr850. Ensure the module is installed and accessible.")

try:
    from QSSPL.fy2300 import fy2300
except ImportError:
    raise ImportError("Failed to import fy2300 from QSSPL.fy2300. Ensure the module is installed and accessible.")

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
            self.turn_on = 295.5
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
            self.lia = SR830('GPIB1::8::INSTR')
            print("Lock-in SR850 connected.")
        except Exception as e:
            print("Error while trying to connect to the SR850: ", e)
            print("Please ensure the Lock-in is connected to 'GPIBX::XX::INSTR' and try again.")
            raise self.CustomError("Lock-in Connection Error")
        
        # Connect to the Filter Slider
        try:
            self.filter = FilterSlider()
            print("Filter slider connected.")
        except Exception as e:
            print("Error while trying to connect to the Filter Slider: ", e)
            print("Please ensure the Filter Slider is connected and try again.")
            raise self.CustomError("Filter Slider Connection Error")    

        # Connect to the FY2300
        try: 
            self.fy = fy2300("COM5")
            print("FY2300 connected.")
        except Exception as e:
            print("Error while trying to connect to the FY2300: ", e)
            print("Please ensure the FY2300 is connected and try again.")
            raise self.CustomError("FY2300 Connection Error")

        # Connect to the stepper motor
        try:
            self.stepper = Stepper('COM23')
            print("Stepper connected.")
        except Exception as e:
            print("Error while trying to connect to the Stepper: ", e)
            print("Please ensure the Stepper is connected and try again.")
            raise self.CustomError("Stepper Connection Error")           
        
    # Method to set the laser current modulation
    def _current_mod(self, max_current):
        ''' Method to modulate the current of the laser '''
        turn_on = self.turn_on
        diff = max_current  - turn_on
        voltage = (2**-0.5)*(diff*0.05)/100
        return voltage, max_current

    # Method to configure the hardware
    def _configure_ldc(self):
        ''' Method to configure the laser settings'''
        self.ldc.set_laserOn()
        self.ldc.set_tecOn()
        self.ldc.set_modulationOn()
        self.stepper.moveto(0)
        print("Laser, TEC, and modulation turned on, sample moved to laser beam.")
        sleep(1)

    def _configure_fy(self):
        self.fy.set_output_on(1)
        self.fy.set_output_on(2)
        self.fy.set_amplitude(2, 1)

        print("FY2300 channel 1 and 2 turned on, channel 2 amplitude set to 1 V")

    # Method to turn off the laser
    def _turn_off(self):
        ''' Method to turn off laser '''
        self.ldc.set_laserOff()
        self.ldc.set_tecOff()
        self.ldc.set_modulationOff()
        print("Laser, TEC, and modulation turned off.")

    def _generate_currents(self, start, stop):
        turn_on = self.turn_on
        currents = np.logspace(np.log10(start-turn_on), np.log10(stop-turn_on), 21)
        currents = currents + turn_on
        return currents


    # Method to take QSSPL measurements
    def take_qsspl(self, sample_name = "sample", min_current = 300, max_current = 780, waveform = "square", rest = 0.1):
        """ Method to take QSSPL measurements

        Args:
            sample_name (str, optional): Name of sample. Defaults to "sample".
            min_current (int, optional): Minimum laser current (mA). Defaults to 300.
            max_current (int, optional): Maximum laser current (mA). Defaults to 780.
            step (int, optional): Step between current settings (mA). Defaults to 20.
            waveform (str, optional): Shape of waveform.  Defaults to "square".
            rest(float, optional): Time delay between measurements (s).  Defaults to 0.1 s. 
        """        
        # Configure the hardware
        self._configure_ldc()
        self._configure_fy()

        print('Begin scan')
        
        currents = self._generate_currents(min_current, max_current) # log space

        for curr in currents:
            data = pd.DataFrame()
            v_set, I_set = self._current_mod(curr)
            #self.lia.sine_voltage = v_set  # when using lock in
            self.fy.set_amplitude(1, v_set) # when using fy2300
            self.ldc.set_laserCurrent(I_set)
            print(f'Current set to {I_set}')
            
            # Sweep frequency and take measurements
            for freq in np.linspace(1e4, 8e4, 15):
                #self.lia.frequency = freq # when using lock in
                self.fy.set_waveform(1, waveform, freq) # when using fy2300
                self.fy.set_waveform(2, "sine", freq) # when using fy2300

                # Measure PL signal
                self.filter.right() # Longpass in - PL
                sleep(10*rest)
                #self.lia.quick_range()
                self.lia.auto_gain()
                temp = []
                sleep(2*rest)
                for i in tqdm(range(10)):
                    temp.append(self.lia.get_theta()) # Get phase shift
                    sleep(rest)
                data[f'PL_{freq}'] = temp    
                print(f"Longpass in (PL) phase shift collected at {freq} Hz")    

                # Measure laser signal
                self.filter.left() # Longpass out - Laser
                sleep(10*rest)
                #self.lia.quick_range()
                self.lia.auto_gain()
                temp = []
                sleep(2*rest)
                for i in tqdm(range(10)):
                    temp.append(self.lia.get_theta()) # Get phase shift
                    sleep(rest)
                data[f'Laser_{freq}'] = temp    
                print(f"Longpass out (laser) phase shift collected at {freq} Hz")    
                
                # Store the data
                data[f'Diff_{freq}'] = np.abs(data[f'Laser_{freq}'] -  data[f'PL_{freq}'])
                print(f'Difference: {np.mean(data[f"Diff_{freq}"])}+-{np.std(data[f"Diff_{freq}"])}')

            # Save the data
            data.to_csv(f'{sample_name}_TR_{curr:0.2f}.csv', index = False)
            print("Data saved")

        # Power down
        self._turn_off()



    # Method to test QSSPL measurements- for quick hardware testing
    def test_qsspl(self, sample_name = "test_1", min_current = 550, max_current = 650, waveform = "square", rest = 0.1):
        """ Method to take QSSPL measurements

        Args:
            sample_name (str, optional): Name of sample. Defaults to "sample".
            min_current (int, optional): Minimum laser current (mA). Defaults to 320.
            max_current (int, optional): Maximum laser current (mA). Defaults to 780.
            step (int, optional): Step between current settings (mA). Defaults to 20.
            waveform (str, optional): Shape of waveform.  Defaults to "sine".
            rest(float, optional): Time delay between measurements (s).  Defaults to 0.1 s. 
        """        

        # Configure the hardware
        self._configure_ldc()
        self._configure_fy()

        print('Begin test scan, testing quickrange')
        

        currents = [min_current, max_current] 

        for curr in currents:
            data = pd.DataFrame()
            v_set, I_set = self._current_mod(curr)
            #self.lia.sine_voltage = v_set  # when using lock in
            self.fy.set_amplitude(1, v_set) # when using fy2300
            self.ldc.set_laserCurrent(I_set)
            print(f'Current set to {I_set}')
            
            # Sweep frequency and take measurements
            for freq in np.linspace(1e4, 8e4, 5):
                #self.lia.frequency = freq # when using lock in
                self.fy.set_waveform(1, waveform, freq) # when using fy2300
                self.fy.set_waveform(2, "sine", freq) # when using fy2300

                # Measure PL signal
                self.filter.right() # Longpass in - PL
                sleep(10*rest)
                #self.lia.quick_range()
                self.lia.auto_gain()
                temp = []
                sleep(2*rest)
                for i in tqdm(range(10)):
                    temp.append(self.lia.get_theta()) # Get phase shift
                    sleep(rest)
                data[f'PL_{freq}'] = temp    
                print(f"Longpass in (PL) phase shift collected at {freq} Hz")    

                # Measure laser signal
                self.filter.left() # Longpass out - Laser
                sleep(10*rest)
                #self.lia.quick_range()
                self.lia.auto_gain()
                temp = []
                sleep(2*rest)
                for i in tqdm(range(10)):
                    temp.append(self.lia.get_theta()) # Get phase shift
                    sleep(rest)
                data[f'Laser_{freq}'] = temp    
                print(f"Longpass out (laser) phase shift collected at {freq} Hz")    
                
                # Store the data
                data[f'Diff_{freq}'] = np.abs(data[f'Laser_{freq}'] -  data[f'PL_{freq}'])
                print(f'Difference: {np.mean(data[f"Diff_{freq}"])}+-{np.std(data[f"Diff_{freq}"])}')

            # Save the data
            data.to_csv(f'{sample_name}_TR_{curr:0.2f}.csv', index = False)
            print("Data saved")

        # Power down
        self._turn_off()






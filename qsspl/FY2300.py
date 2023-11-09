
import fygen
fy = fygen.FYGen('/dev/ttyUSB0', debug_level=1)
fy = fygen.FYGen(debug_level=1)  # Same thing

# In case you get UnsupportedDeviceError, you can manually specify
# one of the supported devices that may be compatible.
# The id's of waveforms are different between models,
# so you might not get the waveform you ask for
fy = fygen.FyGen(device_name='fy2300')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from time import sleep
import os
from tqdm import tqdm
%matplotlib

currents = np.linspace(300, 700, 41)[::-1]
for curr in tqdm(currents):
    fig, ax = plt.subplots(1,1)
    voltage_setpt, current_setpt = current_mod(curr)
    plqy.lia.sine_voltage = voltage_setpt
    plqy.ldc.set_laserCurrent(current_setpt)
    sleep(2)
    plqy.lia.quick_range()
    x_data = []
    y_data = []
    t0 = time()
    x_data.append(1)
    y_data.append(plqy.lia.get_magnitude())
    line1, = plt.plot(x_data, y_data)
    while time()-t0 < 600:
        x_data.append(time()-t0)
        y_data.append(plqy.lia.get_magnitude())
        line1.set_xdata(x_data)
        line1.set_ydata(y_data)
        ax.set_xlim(0, x_data[-1]+1)
        ax.set_ylim(min(y_data), max(y_data))
        fig.canvas.draw()
        fig.canvas.flush_events()
        sleep(0.5)

    df = pd.DataFrame({'time (s)' : x_data, 'laser_signal' : y_data})
    df.to_csv(f'Power_{curr}.csv', index = False)
    plt.savefig(f'Power_{curr}.png')
    plt.close()

plqy.ldc.set_laserOff()
plqy.ldc.set_tecOff()

from time import time
fig, ax = plt.subplots(1,1)
x_data = []
y_data = []
t0 = time()
x_data.append(1)
y_data.append(plqy.lia.get_magnitude())
line1, = plt.plot(x_data, y_data)
while True:
    x_data.append(time()-t0)
    y_data.append(plqy.lia.get_magnitude())
    line1.set_xdata(x_data)
    line1.set_ydata(y_data)
    ax.set_xlim(0, x_data[-1]+1)
    ax.set_ylim(min(y_data), max(y_data))
    fig.canvas.draw()
    fig.canvas.flush_events()
    sleep(0.5)

^M
    ...:         temperature.append(float(ldc.ask('TTRD ?')[:-2]))^M
    ...:         laser_power.append(lia.get_magnitude())^M
    ...:         counter.append(j)^M
    ...: ^M
    ...:         line1.set_xdata(counter)^M
    ...:         line1.set_ydata(temperature)^M
    ...:         line2.set_xdata(counter)^M
    ...:         line2.set_ydata(laser_power)^M
    ...: ^M
    ...:         fig.canvas.draw()^M
    ...: ^M
    ...:         fig.canvas.flush_events()^M
    ...:         j+=1^M
    ...:         sleep(0.1)^M
    ...: ^M
    ...:     v_sine, i_ld = current_mod(current_setpoint)^M
    ...:     lia.sine_voltage = v_sine^M7893
    ...:     ldc.clear()^M
    ...:     sleep(0.1)^M
    ...:     ldc.write(f'SILD {i_ld:0.1f}')^M
    ...:     sleep(0.1)^M
    ...:     ldc.write(f'SILD {i_ld:0.1f}')^M
    ...:     sleep(0.1)^M
    ...:     lia.quick_range()^M
    ...:     ax1.set_title(f'Setpoint: {i_ld:0.1f}, Voltage: {v_sine:0.4f}, Peak Current: {current_setp
    ...: oint}')^M
    ...: ^M
    ...:     for i in tqdm(range(duration*8)):^M
    ...: ^M
    ...:         temperature.append(float(ldc.ask('TTRD ?')[:-2]))^M
    ...:         laser_power.append(lia.get_magnitude())^M
    ...:         counter.append(j)^M
    ...: ^M
    ...:         line1.set_xdata(counter)^M
    ...:         line1.set_ydata(temperature)^M
    ...:         line2.set_xdata(counter)^M
    ...:         line2.set_ydata(laser_power)^M
    ...: ^M
    ...:         fig.canvas.draw()^M
    ...: ^M
    ...:         fig.canvas.flush_events()^M
    ...:         j+=1^M
    ...:         sleep(0.1)^M
    ...: ^M
    ...:     plt.savefig(f'Power_{current_setpoint}.png')^M
    ...:     plt.close()^M
    ...: ^M
    ...:     return temperature, laser_power
    ...:




t0 = time()
plqy.stepper.moveto(30)
print(time()-t0)


# currents = np.linspace(300, 700, 21)[::-1]

# currents = 294.3+np.logspace(np.log10(300-294.3), np.log10(700-294.3), 41)
currents = np.arange(300, 800, 20)
for curr in currents:
    plqy.take_PLQY(f'iPACl_test_{curr}_1', max_current = curr, n_avg = 5, time_constant = 0.1, frequency_setpt = 993.0)

plqy.ldc.set_laserOff()
plqy.ldc.set_tecOff()



currents = 294.3+np.logspace(np.log10(400-294.3), np.log10(700-294.3), 31)
currents = currents[::-1]
for curr in currents:
    data = pd.DataFrame()
    v_set, I_set = current_mod(curr)
    plqy.lia.sine_voltage = v_set
    plqy.ldc.set_laserCurrent(I_set)
    sleep(1)
    for freq in np.linspace(1e4, 8e4, 15):
        plqy.lia.frequency = freq
        plqy.filterslider.right() #PL signal
        sleep(0.3)
        plqy.lia.quick_range()
        temp = []
        sleep(0.5)
        for i in tqdm(range(10)):
            temp.append(plqy.lia.get_theta())
            sleep(0.1)
        data[f'PL_{freq}'] = temp
        print(f'Average: {np.mean(temp):0.2f} +- {np.std(temp):0.2f}')

        plqy.filterslider.left() #PL signal
        sleep(0.3)
        plqy.lia.quick_range()
        temp = []
        sleep(0.5)
        for i in tqdm(range(10)):
            temp.append(plqy.lia.get_theta())
            sleep(0.1)
        data[f'Laser_{freq}'] = temp
        print(f'Average: {np.mean(temp):0.2f} +- {np.std(temp):0.2f}')
        data[f'Diff_{freq}'] = np.abs(data[f'Laser_{freq}'] -  data[f'PL_{freq}'])

    # print(data.mean())
    plqy.lia.frequency = 1e4
    data.to_csv(f'TR_{freq}_{curr:0.2f}.csv', index = False)
    # plt.plot(np.linspace(1e4, 8e4, 15), data[[c for c in data.columns if 'Diff' in c]].mean())
    # plt.show()

plqy.ldc.set_laserOff()
plqy.ldc.set_tecOff()



temp = []
vs = np.linspace(0,1.434, 1435)
for v in vs:
    plqy.lia.sine_voltage = v
    temp.append(plqy.lia.get_theta())



currents = 294.3+np.logspace(np.log10(300-294.3), np.log10(700-294.3), 41)
for curr in currents:
    data = pd.DataFrame()
    v_set, I_set = current_mod(curr)
    plqy.lia.sine_voltage = v_set
    plqy.ldc.set_laserCurrent(I_set)
    if curr < 350:
        sleep_factor = 1
        plqy.lia.time_constant = 1
    else:
        sleep_factor = 0.1
        plqy.lia.time_constant = 0.1
    for freq in np.linspace(1e4, 8e4, 15):
        plqy.lia.frequency = freq
        plqy.filterslider.right() #PL signal
        sleep(sleep_factor*10)
        plqy.lia.quick_range()
        temp = []
        sleep(sleep_factor*2)
        for i in tqdm(range(10)):
            temp.append(plqy.lia.get_theta())
            sleep(sleep_factor)
        data[f'PL_{freq}'] = temp

        plqy.filterslider.left() #PL signal
        sleep(sleep_factor*10)
        plqy.lia.quick_range()
        temp = []
        sleep(sleep_factor*2)
        for i in tqdm(range(10)):
            temp.append(plqy.lia.get_theta())
            sleep(sleep_factor)
        data[f'Laser_{freq}'] = temp
        data[f'Diff_{freq}'] = np.abs(data[f'Laser_{freq}'] -  data[f'PL_{freq}'])
        print(f'Difference: {np.mean(data[f"Diff_{freq}"])}+-{np.std(data[f"Diff_{freq}"])}')

    plqy.lia.frequency = 1e4
    data.to_csv(f'TR_{freq}_{curr:0.2f}.csv', index = False)
    plt.plot(np.linspace(1e4, 8e4, 15), data[[c for c in data.columns if 'Diff' in c]].mean())
    plt.show()




# currents = np.append(np.arange(282, 320, 0.1), np.arange(320, 801, 2.0))
currents = np.arange(300, 800, 20)
for i in range(5):
    pm_power = []
    pm_stds = []
    for curr in tqdm(currents):
        plqy.ldc.set_laserCurrent(curr)
        sleep(10)
        temp = []
        for _ in range(5):
            temp.append(pm.read)
            sleep(0.1)

        temp = np.array(temp)
        pm_power.append(temp.mean())
        pm_stds.append(temp.std())

        print(f'\n{pm_power[-1]:0.3e} W of power at {curr} mA of current')

    df = pd.DataFrame(
        {
            'currents': currents,
            'pm_power': pm_power,
            'pm_stds' : pm_stds
        }
    )

    df.to_csv(f'Current_vs_Power_{i+1}.csv', index = False)

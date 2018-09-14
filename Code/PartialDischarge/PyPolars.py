import math as m
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
import copy
import os

minCont = 10

class Sensor:
    def __init__(self, canal, amp, t0):
        self.canal = canal
        self.t0 = t0
        self.angs = np.linspace(0, 2 * m.pi, 360)
        self.conts = np.zeros(360)
        self.conts[0] = 1
        self.amps = [amp]
        self.AcuAmps = np.zeros(360)
        self.AcuAmps[0] += amp

    def addHit(self, amp, time):
        ang = ((time - self.t0) / (1 / 60)) % 1
        ang *= 360
        self.conts[int(ang)] += 1
        self.amps.append(amp)
        self.AcuAmps[int(ang)] += amp


def linetoArray(line):
    i = 0
    array = []
    temp = ""
    flag = True
    for char in line:
        if char == " ":
            if flag:
                pass
            else:
                i += 1
                array.append(temp)
                temp = ""
                flag = True
        else:
            temp += char
            flag = False

    if temp != "":
        temp = temp.split("\n")[0]
        array.append(temp)

    return array

def main(dir, dir_figs):
    files_paths = []
    for root, dirs, files in os.walk(dir):  
        for filename in files:
            files_paths.append(filename)

    print(files_paths)

    for file_name in files_paths:
        file = open(os.path.join(dir, file_name), "r")
        plot_name = copy.copy(file_name)
        plot_name = plot_name.lower()
        plot_name = plot_name.strip(".txt")
        print(plot_name)
        AllData = file.readlines()

        Tags = []
        Sensors = []

        for line in AllData:
            data = linetoArray(line)
            if len(data) == 4 and data[0] != "ID":
                i = 0
                for element in data:
                    data[i] = float(element)
                    i += 1

                canal = data[2]
                try:
                    id = Tags.index(canal)
                    sensor = Sensors[id]
                    sensor.addHit(data[3], data[1])

                except ValueError:
                    Tags.append(canal)
                    sensor = Sensor(canal, data[3], data[1])
                    Sensors.append(sensor)

        for sensor in Sensors:
            if np.max(sensor.conts) >= minCont:
                plt.polar(sensor.angs, sensor.conts)
                AcuAmpsNorm = sensor.AcuAmps / \
                    np.max(sensor.AcuAmps) * np.max(sensor.conts)
                plt.polar(sensor.angs, 0.5 * AcuAmpsNorm)
                plt.title(plot_name + " - CH " + str(int(sensor.canal)))
                plt.legend(["Nº de Hits", "Amplitude acumulada"], loc = (0.8, 0.95))
                fig_name = plot_name + " - CH " + str(int(sensor.canal)) + ".png"
                plt.savefig(os.path.join(dir_figs, fig_name))
                plt.clf()

        for sensor in Sensors:
            if np.max(sensor.conts) >= minCont:
                plt.polar(sensor.angs, sensor.conts)

        plt.title(plot_name + " - todos")
        fig_name = plot_name + " - todos" + ".png"
        plt.savefig(os.path.join(dir_figs, fig_name))

main("L:\\Documentos\\Python\\Projects\\PyPolars\\Data", "C:\\Users\\l01481\\Desktop\\teste")
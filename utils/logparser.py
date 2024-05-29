#!/usr/bin/env python

import os
import numpy

class LogFile:

    def __init__(self, path) -> None:
        self.path = os.path.abspath(path)
        self.name = os.path.basename(self.path)
        self.freqlist, self.ir_inten, self.raman_act = self.read_data()
    
    def read_data(self):
        FREQ_INDICATOR = "Frequencies"
        RAMAN_INDICATOR = "Raman Activ"
        IR_INDICATOR = "IR Inten"
        INDICATORS = [FREQ_INDICATOR, IR_INDICATOR, RAMAN_INDICATOR]
        DATA_LISTS = {"Frequencies" : [],
                      "Raman": [],
                      "IR": []}
        with open(self.path, "r") as file:
            lines = file.readlines()
            for line in lines:
                if any(ind in line for ind in INDICATORS):
                    data = line.split()
                    for i in range(-3, 0, 1):
                        DATA_LISTS[data[0]].append(float(data[i]))
        return numpy.array(DATA_LISTS["Frequencies"]), numpy.array(DATA_LISTS["IR"]), numpy.array(DATA_LISTS["Raman"])
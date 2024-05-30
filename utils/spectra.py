#!/usr/bin/env python

import os
import csv
import numpy
import scipy

class Spectrum:

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.read_data()
    
    def read_data(self, d=","):
        frequencies = []
        intensities = []
        with open(self.path, "r") as file:
            csv_file = csv.reader(file, delimiter=d)
            for line in csv_file:
                if line[0][0].isdigit() and line[1][0].isdigit():
                    frequencies.append(float(line[0]))
                    intensities.append(float(line[1]))

        # Sort the data in ascending order       
        if frequencies[0] > frequencies[1]:
            frequencies = frequencies[::-1]
            intensities = intensities[::-1]

        self.frequencies = numpy.array(frequencies)
        self.intensities = numpy.array(intensities)

    def normalize(self):
        max_intensity = self.intensities.max()
        self.intensities /= max_intensity

    def export_csv(self, path):
        with open(path, "w") as output:
            output.write("Frequency (cm^-1), Intensity\n")
            for i, j in zip(self.frequencies, self.intensities):
                output.write(f"{i},{j}\n")
    
class Experimental_Spectrum(Spectrum):
    def __init__(self, path):
        Spectrum.__init__(self, path)
        self.read_data()
    
    def interpolate(self, th_spectrum):
        interpolated_intensities = numpy.interp(th_spectrum.frequencies, self.frequencies, self.intensities)
        return interpolated_intensities
    
    def correlation(self, interpolated_intensities, th_spectrum, mode = "pearson"):
        if mode == "pearson":
            r = scipy.stats.pearsonr(interpolated_intensities, th_spectrum.intensities)[0]
        elif mode == "spearman":
            r = scipy.stats.spearmanr(interpolated_intensities, th_spectrum.intensities)[0]
        else:
            raise Exception("The correlation mode that was specified does not exist...")
        return r
    
class Theoretical_Spectrum(Spectrum):
    def __init__(self, freqlist, intlist, fmin, fmax, step, sigma, scale, mode="lorentz"):
        self.check_input([fmin, fmax, step, sigma, scale])
        self.fmin = fmin
        self.fmax = fmax
        self.step = step
        self.nstep = int(round((self.fmax - self.fmin)/self.step) + 1)
        self.sigma = sigma
        self.scale = scale
        self.mode = mode
        self.freqlist = freqlist
        self.intlist = intlist
        self.scaled_freqlist = freqlist * scale
        self.frequencies, self.intensities = self.generate_spectrum()

    def check_input(self, params):
        for param in params:
            if isinstance(param, str):
                raise TypeError("fmax, fmin, step, sigma and scale must be of type int or float")
            
        if params[0] > params[1]:
            raise Exception("The maximum frequency is below the minimum frequency (cm^-1)")

    def generate_spectrum(self):
        # Generate frequencies
        self.frequencies = []
        for i in range(0, self.nstep):
             freq = self.fmin + i * self.step
             self.frequencies.append(freq)

        # Set spectrum function
        if self.mode == "gauss":
            spectrum_function = lambda freq, x: (1.0/(self.sigma*numpy.sqrt(2*numpy.pi)) * numpy.exp(-0.5*((x-freq)/self.sigma)**2))
        elif self.mode == "lorentz":
            spectrum_function  = lambda freq, x: (1.0/numpy.pi*self.sigma)/((x-freq)**2+self.sigma**2)
        else:
            raise Exception("Mode must be 'gauss' or 'lorentz'.")
        
        # Generate the spectrum
        temp = numpy.empty((self.nstep, len(self.scaled_freqlist)))
        for i in range(len(self.scaled_freqlist)):
            temp[:,i] = spectrum_function(self.scaled_freqlist[i], self.frequencies) * self.intlist[i]
        self.intensities = numpy.sum(temp, axis=1, dtype=float)
        return self.frequencies, self.intensities
    
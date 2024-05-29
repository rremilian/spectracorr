#!/usr/bin/env python

import os
import argparse
from datetime import datetime
from utils import logparser
from utils import spectra


def write_output(message, output_file):

    with open(output_file, "a") as output:
        output.write(message)

def write_spectral_data(data, output_file):
    for index, i in enumerate(data):
        if index %  5 == 0:
            write_output("\n", output_file)
        write_output(f"{i} ", output_file)
    write_output("\n\n", output_file)

def main():
    parser = argparse.ArgumentParser(
        prog = "SpectraCorr",
        description = "A Python program used for the calculation of the correlation coefficients between experimental spectra and theoretical spectra."
)
    parser.add_argument("-e", "--experimental-spectrum", type=str, required=True)
    parser.add_argument("-t", "--theoretical-log", type=str, required=True)
    parser.add_argument("-s", "--sigma", type=float, required=False, default = 20)
    parser.add_argument("-fmin", "--min-frequency", type=float, required=False, default=500)
    parser.add_argument("-fmax", "--max-frequency", type=float, required=False, default=3800)
    parser.add_argument("-fs", "--frequency-step", type=float, required=False, default=1)
    parser.add_argument('-sc', "--scale-factor", type=float, required=False)
    parser.add_argument("-smin", "--min-scale-factor", type=float, required=False)
    parser.add_argument("-smax", "--max-scale-factor", type=float, required=False)
    parser.add_argument("-ss", "--scale-factor-step", type=float, required=False, default=0.01)
    parser.add_argument("-m", "--mode", type=str, required=False, default="lorentz")
    parser.add_argument("-o", "--output", type=str, required=False, default="output.txt")

    args = parser.parse_args()

    if os.path.isfile(args.output):
        os.remove(args.output)

    dt = datetime.now().strftime('%d-%m-%Y %H:%M:%S ')
    write_output("Starting analysis using SpectraCorr...\n", args.output)
    write_output(f"Date: {dt}\n", args.output)

    if not os.path.isfile(args.experimental_spectrum):
        message = "The experimental spectrum file could not be found..."
        write_output(message)
        raise FileNotFoundError(message)
    
    if not os.path.isfile(args.theoretical_log):
        raise FileNotFoundError("The theoretical log file could not be found...")
    
    exp_spectrum = spectra.Experimental_Spectrum(args.experimental_spectrum)
    th_log = logparser.LogFile(args.theoretical_log)

    write_output(f"Experimental Spectrum: {exp_spectrum.path}\n", args.output)
    write_output(f"Theoretical Spectrum Log File: {th_log.path}\n\n", args.output)
    write_output(f"====================THEORETICAL SPECTRUM OPTIONS====================\n", args.output)
    write_output(f"Minimum frequency: {args.min_frequency} cm^-1 \n", args.output)
    write_output(f"Maximum frequency: {args.max_frequency} cm^-1 \n", args.output)
    write_output(f"Frequency Step: {args.frequency_step} cm^-1\n", args.output)
    write_output(f"Sigma: {args.sigma} cm^-1\n", args.output)

    if args.scale_factor and (args.min_scale_factor or args.max_scale_factor or args.scale_factor_step):
        raise Exception("The option '--scale-factor' cannot be used together with '--min-scale-factor', '--max-scale-factor' or '--scale-factor-step'...")

    if args.min_scale_factor and args.max_scale_factor and args.scale_factor_step:
        if args.min_scale_factor > args.max_scale_factor:
            raise Exception("The minimum scale factor cannot be greater than the maximum scale factor...")
  
    
        write_output(f"Minimum Scale Factor: {args.min_scale_factor} cm^-1\n", args.output)
        write_output(f"Maximum Scale Factor: {args.max_scale_factor} cm^-1\n", args.output)
        write_output(f"Scale Factor Step: {args.scale_factor_step} cm^-1\n", args.output)
    write_output("====================================================================\n\n", args.output)

    write_output("============================INITIAL DATA============================\n", args.output)

    write_output(f"Experimental Spectrum Frequencies:", args.output)
    write_spectral_data(exp_spectrum.frequencies, args.output)
    write_output(f"Experimental Spectrum Intensities:", args.output)
    write_spectral_data(exp_spectrum.intensities, args.output)

    write_output(f"Theoretical Log Frequencies List:", args.output)
    write_spectral_data(th_log.freqlist, args.output)

    write_output(f"Theoretical Log IR Intensities List:", args.output)
    write_spectral_data(th_log.ir_inten, args.output)

    if th_log.raman_act.any():
        write_output(f"Theoretical Log Raman Activities List:", args.output)
        write_spectral_data(th_log.raman_act, args.output)
    
    write_output("====================================================================\n\n", args.output)

    write_output("===================GENERATING THEORETICAL SPECTRUM==================\n", args.output)



if __name__ == '__main__':
    main()
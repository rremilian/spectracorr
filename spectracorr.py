#!/usr/bin/env python

import os
import argparse
import numpy
import shutil
from datetime import datetime
from utils import logparser
from utils import spectra


def write_output(message, output_file):

    with open(output_file, "a") as output:
        output.write(message)

def write_spectral_data(frequencies, intensities, output_file):
    write_output("\n", output_file)
    write_output("Frequency (cm^-1) - Intensity\n", output_file)
    write_output("=============================\n", output_file)
    for i, j in zip(frequencies, intensities):
        write_output(f"{i:.3f} - {j:.3f}", output_file)
        write_output("\n", output_file)
    write_output("=============================\n", output_file)
    write_output("\n", output_file)

def main():
    parser = argparse.ArgumentParser(
        prog = "SpectraCorr",
        description = "A Python program used for the calculation of the correlation coefficients between experimental spectra and theoretical spectra."
)
    parser.add_argument("-e", "--experimental-spectrum", type=str, required=False)
    parser.add_argument("-t", "--theoretical-log", type=str, required=True)
    parser.add_argument("-s", "--sigma", type=float, required=False, default = 20)
    parser.add_argument("-fmin", "--min-frequency", type=float, required=False, default=500)
    parser.add_argument("-fmax", "--max-frequency", type=float, required=False, default=3800)
    parser.add_argument("-fs", "--frequency-step", type=float, required=False, default=1)
    parser.add_argument('-sc', "--scale-factor", type=float, required=False, default=1.00)
    parser.add_argument("-smin", "--min-scale-factor", type=float, required=False)
    parser.add_argument("-smax", "--max-scale-factor", type=float, required=False)
    parser.add_argument("-ss", "--scale-factor-step", type=float, required=False, default=0.01)
    parser.add_argument("-m", "--mode", type=str, required=False, default="lorentz")
    parser.add_argument("--only-raman", action="store_true")
    parser.add_argument("--only-ir", action="store_true")
    parser.add_argument("-c", "--correlation-mode", type=str, required=False, default="pearson")
    parser.add_argument("-o", "--output", type=str, required=False, default="output.txt")

    args = parser.parse_args()

    if os.path.isfile(args.output):
        os.remove(args.output)

    dt = datetime.now().strftime('%d-%m-%Y %H:%M:%S ')
    write_output("Starting analysis using SpectraCorr...\n", args.output)
    write_output(f"Date: {dt}\n", args.output)

    if args.experimental_spectrum:
        if not os.path.isfile(args.experimental_spectrum):
            raise FileNotFoundError("The experimental spectrum file could not be found...")
        exp_spectrum = spectra.Experimental_Spectrum(args.experimental_spectrum)
        write_output(f"Experimental Spectrum: {exp_spectrum.path}\n", args.output)
    
    if not os.path.isfile(args.theoretical_log):
        raise FileNotFoundError("The theoretical log file could not be found...")
    
    
    th_log = logparser.LogFile(args.theoretical_log)

    
    write_output(f"Theoretical Spectrum Log File: {th_log.path}\n\n", args.output)
    write_output(f"====================THEORETICAL SPECTRUM OPTIONS====================\n", args.output)
    write_output(f"Minimum frequency: {args.min_frequency} cm^-1 \n", args.output)
    write_output(f"Maximum frequency: {args.max_frequency} cm^-1 \n", args.output)
    write_output(f"Frequency Step: {args.frequency_step} cm^-1\n", args.output)
    write_output(f"Sigma: {args.sigma} cm^-1\n", args.output)

    if args.min_scale_factor and args.max_scale_factor is None:
        raise Exception("The options '--min-scale-factor' and '--max-scale-factor' must be used together...")

    if args.min_scale_factor and args.max_scale_factor and args.scale_factor_step:
        if args.min_scale_factor > args.max_scale_factor:
            raise Exception("The minimum scale factor cannot be greater than the maximum scale factor...")
  
    
        write_output(f"Minimum Scale Factor: {args.min_scale_factor} cm^-1\n", args.output)
        write_output(f"Maximum Scale Factor: {args.max_scale_factor} cm^-1\n", args.output)
        write_output(f"Scale Factor Step: {args.scale_factor_step} cm^-1\n", args.output)
    write_output("====================================================================\n\n", args.output)

    write_output("============================INITIAL DATA============================\n\n", args.output)

    if args.experimental_spectrum:
        write_output(f"Experimental Spectrum :\n", args.output)
        write_spectral_data(exp_spectrum.frequencies, exp_spectrum.intensities, args.output)

    write_output(f"Theoretical Log IR Data List:\n", args.output)
    write_spectral_data(th_log.freqlist, th_log.ir_inten, args.output)

    if th_log.raman_act.any():
        write_output(f"Theoretical Log Raman Data List:\n", args.output)
        write_spectral_data(th_log.freqlist, th_log.raman_act, args.output)
    
    write_output("====================================================================\n\n", args.output)

    write_output("===================GENERATING THEORETICAL SPECTRA===================\n\n", args.output)

    scale_factors = []
    th_ir_spectrum = None
    th_raman_spectrum = None

    if args.min_scale_factor and args.max_scale_factor:
        output_name = args.output.split(".")[0]
        if os.path.isdir(output_name):
            shutil.rmtree(output_name)
        os.mkdir(output_name)
        scale_factor_nstep = int(round((args.max_scale_factor - args.min_scale_factor)/args.scale_factor_step) + 1)
        for i in range(0, scale_factor_nstep):
             s = args.min_scale_factor + i * args.scale_factor_step
             scale_factors.append(round(s,3))
    else:
        scale_factors.append(args.scale_factor)

    for s in scale_factors:
        if args.only_ir:
            th_ir_spectrum = spectra.Theoretical_Spectrum(th_log.freqlist, th_log.ir_inten, args.min_frequency, args.max_frequency, args.frequency_step,
                                                          args.sigma, s, args.mode)
        elif args.only_raman:
            th_raman_spectrum = spectra.Theoretical_Spectrum(th_log.freqlist, th_log.raman_act, args.min_frequency, args.max_frequency, args.frequency_step,
                                                             args.sigma, s, args.mode)
        else:
            th_ir_spectrum = spectra.Theoretical_Spectrum(th_log.freqlist, th_log.ir_inten, args.min_frequency, args.max_frequency, args.frequency_step,
                                                          args.sigma, s, args.mode)
            th_raman_spectrum = spectra.Theoretical_Spectrum(th_log.freqlist, th_log.raman_act, args.min_frequency, args.max_frequency, args.frequency_step,
                                                             args.sigma, s, args.mode)
            
        if th_ir_spectrum:
            th_ir_spectrum.export_csv(os.path.join(output_name,f"{output_name}-IR-{s}.csv"))
            write_output(f"IR Spectrum with Scale Factor = {s} - DONE\n", args.output)
        if th_raman_spectrum:
            th_raman_spectrum.export_csv(os.path.join(output_name,f"{output_name}-Raman-{s}.csv"))
            write_output(f"Raman Spectrum with Scale Factor = {s} - DONE\n", args.output)

    write_output("====================================================================\n\n", args.output)

    write_output("=======================CORRELATION CALCULATION======================\n\n", args.output)

    write_output("Normalizing experimental spectrum...\n", args.output)

    exp_spectrum.normalize()

    write_output("Interpolating experimental spectrum based on the theoretical frequencies...\n", args.output)

    if args.only_ir:
        to_do = ["IR"]
        interpolated_exp_intensities = exp_spectrum.interpolate(th_ir_spectrum)
    elif args.only_raman:
        to_do = ["Raman"]
        interpolated_exp_intensities = exp_spectrum.interpolate(th_raman_spectrum)
    else:
        to_do = ["IR", "Raman"]
        interpolated_exp_intensities = exp_spectrum.interpolate(th_ir_spectrum)

    for type in to_do:
        write_output(f"Correlation Factors - {type}\n", args.output)
        write_output("===============================\n", args.output)
        with open(os.path.join(output_name, f"correlation-{type.lower()}.out"), "w") as file:
            file.write(f"Scale Factor, Correlation Factor --- {type}\n")
            for s in scale_factors:
                sp = spectra.Spectrum(os.path.join(output_name,f"{output_name}-{type}-{s}.csv"))
                r = exp_spectrum.correlation(interpolated_exp_intensities, sp, mode=args.correlation_mode)
                write_output(f"[{type}] Correlation calculation for scale factor {s} - DONE...\n", args.output)
                file.write(f"{s},{r}\n")
            file.write("\n\n")

if __name__ == '__main__':
    main()
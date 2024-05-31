#!/usr/bin/env python

import os
import argparse
import numpy
import shutil
from datetime import datetime

from utils import logparser
from utils import spectra

def print_spectral_data(frequencies, intensities):
    print("Frequency (cm^-1) - Intensity")
    print("=============================")
    for i, j in zip(frequencies, intensities):
        print(f"{i:.3f} - {j:.3f}")
    print("=============================\n")

def main():
    parser = argparse.ArgumentParser(
        prog = "SpectraCorr",
        description = "A Python program used for the calculation of the correlation coefficients between experimental spectra and theoretical spectra."
)
    parser.add_argument("-e", "--experimental-spectrum", type=str, required=False)
    parser.add_argument("-t", "--theoretical-log", type=str, required=True)
    parser.add_argument("-d", "--description", type=str, required=False)
    parser.add_argument("-s", "--sigma", type=float, required=False, default = 20)
    parser.add_argument("-fmin", "--min-frequency", type=float, required=False, default=500)
    parser.add_argument("-fmax", "--max-frequency", type=float, required=False, default=3800)
    parser.add_argument("-fs", "--frequency-step", type=float, required=False, default=1)
    parser.add_argument('-sc', "--scale-factor", type=float, required=False, default=1.00)
    parser.add_argument("-smin", "--min-scale-factor", type=float, required=False)
    parser.add_argument("-smax", "--max-scale-factor", type=float, required=False)
    parser.add_argument("-ss", "--scale-factor-step", type=float, required=False, default=0.001)
    parser.add_argument("-m", "--mode", type=str, required=False, default="lorentz")
    parser.add_argument("--only-raman", action="store_true")
    parser.add_argument("--only-ir", action="store_true")
    parser.add_argument("--do-not-save-spectra", action="store_true")
    parser.add_argument("--skip-correlation", action="store_true")
    parser.add_argument("-c", "--correlation-mode", type=str, required=False, default="pearson")
    parser.add_argument("-o", "--output-dir", type=str, required=False, default="output")

    args = parser.parse_args()

    dt_start = datetime.now()
    print("Starting analysis using SpectraCorr...")
    print(f"Date: {dt_start.strftime('%d-%m-%Y %H:%M:%S ')}")

    if args.description:
        print(f"Description: {args.description}")

    if args.experimental_spectrum:
        if not os.path.isfile(args.experimental_spectrum):
            raise FileNotFoundError("The experimental spectrum file could not be found...")
        exp_spectrum = spectra.Experimental_Spectrum(args.experimental_spectrum)
        print(f"Experimental Spectrum: {exp_spectrum.path}")
    
    if not os.path.isfile(args.theoretical_log):
        raise FileNotFoundError("The theoretical log file could not be found...")
    
    
    th_log = logparser.LogFile(args.theoretical_log)

    
    print(f"Theoretical Spectrum Log File: {th_log.path}")
    print(f"===========================PROGRAM OPTIONS===========================")
    print(f"Minimum frequency: {args.min_frequency} cm^-1")
    print(f"Maximum frequency: {args.max_frequency} cm^-1")
    print(f"Frequency Step: {args.frequency_step} cm^-1")
    print(f"Sigma: {args.sigma} cm^-1")
    print(f"Spectrum mode: {args.mode}")

    if args.correlation_mode:
        print(f"Correlation mode: {args.correlation_mode}")

    if args.min_scale_factor and args.max_scale_factor is None:
        raise Exception("The options '--min-scale-factor' and '--max-scale-factor' must be used together...")

    if args.min_scale_factor and args.max_scale_factor and args.scale_factor_step:
        if args.min_scale_factor > args.max_scale_factor:
            raise Exception("The minimum scale factor cannot be greater than the maximum scale factor...")
  
    
        print(f"Minimum Scale Factor: {args.min_scale_factor} cm^-1")
        print(f"Maximum Scale Factor: {args.max_scale_factor} cm^-1")
        print(f"Scale Factor Step: {args.scale_factor_step} cm^-1")

    print("====================================================================\n")

    print("============================INITIAL DATA============================")

    if args.experimental_spectrum:
        print("Experimental Spectrum :")
        print_spectral_data(exp_spectrum.frequencies, exp_spectrum.intensities)

    print("Theoretical Log IR Data List:")
    print_spectral_data(th_log.freqlist, th_log.ir_inten)

    if th_log.raman_act.any():
        print("Theoretical Log Raman Data List:")
        print_spectral_data(th_log.freqlist, th_log.raman_act)
    
    print("====================================================================\n")

    print("===================GENERATING THEORETICAL SPECTRA===================")

    scale_factors = []
    th_ir_spectrum = None
    th_raman_spectrum = None
    if os.path.isdir(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.mkdir(args.output_dir)

    if args.min_scale_factor and args.max_scale_factor:
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
            th_ir_spectrum.export_csv(os.path.join(args.output_dir,f"{args.output_dir}-IR-{s}.csv"))
            print(f"IR Spectrum with Scale Factor = {s} - DONE")
        if th_raman_spectrum:
            th_raman_spectrum.export_csv(os.path.join(args.output_dir,f"{args.output_dir}-Raman-{s}.csv"))
            print(f"Raman Spectrum with Scale Factor = {s} - DONE")

    print("====================================================================\n")

    if args.experimental_spectrum is None:
        print("Skip correlation calculation because experimental spectrum is not defined...")
        return 0
    elif args.skip_correlation:
        print("Skip correlation calculation since the skip_correlation option was used...")
        return 0

    print("========================CORRELATION CALCULATION=======================")

    print("Normalizing experimental spectrum...")

    exp_spectrum.normalize()

    print("Interpolating experimental spectrum based on the theoretical frequencies...\n")

    if args.only_ir:
        to_do = ["IR"]
        interpolated_exp_intensities = exp_spectrum.interpolate(th_ir_spectrum)
    elif args.only_raman:
        to_do = ["Raman"]
        interpolated_exp_intensities = exp_spectrum.interpolate(th_raman_spectrum)
    else:
        to_do = ["IR", "Raman"]
        interpolated_exp_intensities = exp_spectrum.interpolate(th_ir_spectrum)

    summary = []
    for type in to_do:
        r_max = -1
        print(f"Correlation Factors - {type}")
        print("===============================")
        with open(os.path.join(args.output_dir, f"correlation-{type.lower()}.out"), "w") as file:
            file.write(f"Scale Factor, Correlation Factor --- {type}\n")
            for s in scale_factors:
                sp = spectra.Spectrum(os.path.join(args.output_dir,f"{args.output_dir}-{type}-{s}.csv"))
                if args.do_not_save_spectra:
                    os.remove(os.path.join(args.output_dir,f"{args.output_dir}-{type}-{s}.csv"))
                r = exp_spectrum.correlation(interpolated_exp_intensities, sp, mode=args.correlation_mode)
                if r > r_max:
                    r_max = r
                    s_max = s
                print(f"[{type}] Correlation calculation for scale factor {s} - DONE... = {r:.3f}")
                file.write(f"{s},{r}\n")
            file.write("\n\n")
        print("")
        print("==================MAXIMUM CORRELATION COEFFICIENT==================")
        message = f"Maximum correlation coefficient for {type} is {r_max:.3f} at scale factor {s_max}..."
        summary.append(message)
        print(f"{message}\n")

        print("==============================SUMMARY==============================")
        dt_finish = datetime.now()
        duration = dt_finish - dt_start
        total_seconds = round(duration.total_seconds(), 0)
        e_hours = round(total_seconds / 3600, 0)
        e_minutes = round(total_seconds / 60, 0) - e_hours * 60
        e_seconds = total_seconds - e_hours * 3600 - e_minutes * 60 
        print(f"Description: {args.description}")
        for m in summary:
            print(m)
        print(f"Elasped time: {duration.days} days {e_hours} hours {e_minutes} minutes {e_seconds} seconds...\n")
        print(f"Normal termination of SpectraCorr at {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")



if __name__ == '__main__':
    main()
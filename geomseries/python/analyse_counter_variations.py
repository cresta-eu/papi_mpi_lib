#!/usr/bin/env python
# Copyright EPCC,
# Michael Bareford, Copyright 2018
# v1.0

import sys
import re
import os
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plusminus = u'\u00b1'

def have_package_pylab():
    try:
        import pylab
        return True
    except ImportError:
        return False


def help():
    print """usage: python analyse_counter_variations.py -data <data_file_name> [-cntr <cntr_name>] -flops <cntr_name> [-single-flops <cntr_name> -double-flops <cntr_name>]

    If the -cntr argument is absent then the variation of all counters present in the data file will be plotted.
    On some platforms there may be separate counters for single/double floating point operations; in which case
    the -single-flops and -double-flops counters should be used.

    Arguments:

        -data            Name of file containing counter recordings
        -cntr            Name of counter whose value is some proxy for data movement
        -cntr-line-size  The unit counter value in number of bytes

        -flops           Name of FLOPS counter
        -single-flops    Name of FLOPS counter for single precision operations
        -double-flops    Name of FLOPS counter for double precision operations

        -round           The number of decimal places to round logged results
        -ymax            Maximum limit on y-axis
        -nprocs          The number of parallel processes calculating geometric series

        -plot-flops      Plot the flops measured when calculating each geometric series set;
                         note, the flops measurements are those recorded when reading counter cntr
    
        -plot-intensity  Plot the arithmetic intensity for each geometric series set using
                         counter cntr as the proxy for data movement

        -plot-error      Plot the ratio of the recorded value over the expected value
        -plot-error-func Plot the ratio (see above) as a function of counter value
        -no-log          Do not log plot data
"""


def init_args():
    global data_file_name
    global cntr_name
    global cntr_line_size
    global flops_cntr_names
    global log_name
    global fig_name
    global rnd
    global ymax
    global nprocs
    global plot_flops
    global plot_intensity
    global plot_error
    global plot_error_func
    global no_log

    data_file_name = ""
    log_data = False
    cntr_name = ""
    cntr_line_size = 64
    flops_cntr_names = []
    log_name = ""
    fig_name = ""
    rnd = 3
    ymax = 0.0
    nprocs = 1
    plot_flops = False
    plot_intensity = False
    plot_error = False
    plot_error_func = False
    no_log = False

    

def print_args():
    global data_file_name
    global cntr_name
    global cntr_line_size
    global flops_cntr_names
    global log_name
    global fig_name
    global rnd
    global ymax
    global nprocs
    global plot_flops
    global plot_intensity
    global plot_error
    global plot_error_func
    global no_log

    print "data_file_name =", data_file_name
    print "cntr_name =", cntr_name
    print "cntr_line_size =", str(cntr_line_size)
    print "flops_cntr_name(s) =", str(flops_cntr_names)
    print "log_name =", log_name
    print "fig_name =", fig_name
    print "rnd =", str(rnd)
    print "ymax =", str(ymax)
    print "nprocs =", str(nprocs)
    print "plot_flops =", str(plot_flops)
    print "plot_intensity =", str(plot_intensity)
    print "plot_error =", str(plot_error)
    print "plot_error_func =", str(plot_error_func)
    print "no_log =", str(no_log)


    
def parse_args():
    global data_file_name
    global cntr_name
    global cntr_line_size
    global flops_cntr_names
    global log_name
    global fig_name
    global rnd
    global ymax
    global nprocs
    global plot_flops
    global plot_intensity
    global plot_error
    global plot_error_func
    global no_log

    init_args()

    i = 1
    while i < len(sys.argv):
        arg=sys.argv[i]

        if arg == "-h" or arg == "-help":
            help()
            sys.exit()

        elif arg == "-data":
            data_file_name = sys.argv[i+1]
            i += 2
        elif arg == "-cntr":
            cntr_name = sys.argv[i+1]
            i += 2
        elif arg == "-cntr-line-size":
            cntr_line_size = int(sys.argv[i+1])
            i += 2
            
        elif arg == "-flops":
            flops_cntr_names.append(sys.argv[i+1])
            i += 2
        elif arg == "-single-flops":
            flops_cntr_names.append(sys.argv[i+1])
            i += 2
        elif arg == "-double-flops":
            flops_cntr_names.append(sys.argv[i+1])
            i += 2
            
        elif arg == "-round":
            rnd = int(sys.argv[i+1])
            i += 2

        elif arg == "-ymax":
            ymax = float(sys.argv[i+1])
            i += 2

        elif arg == "-nprocs":
            nprocs = int(sys.argv[i+1])
            i += 2

        elif arg == "-plot-flops":
            plot_flops = True
            i += 1

        elif arg == "-plot-intensity":
            plot_intensity = True
            i += 1

        elif arg == "-plot-error":
            plot_error = True
            i += 1
        elif arg == "-plot-error-func":
            plot_error_func = True
            i += 1

        elif arg == "-no-log":
            no_log = True
            i += 1

        else:
            print "Error, argument", arg, "not recognised."
            help()
            sys.exit()
        

    if 0 == len(cntr_name):
        log_name = "variations.txt"
        fig_name = "variations.eps"
    else:
        if ":" in cntr_name:
            fname = cntr_name.replace(":","-")
        else:
            fname = cntr_name

        if plot_flops:
            fname += "-flops"
        elif plot_intensity:
            fname += "-intensity"

        if plot_error:
            fname += "-error"
        elif plot_error_func:
            fname += "-error-func"

        log_name = fname + ".txt"
        fig_name = fname + ".eps"



def parse_counter_data(data_file_name, cntr_name, flops_names, cntr_line_size, nprocs):
    global ARRAY_SIZES
    global MIN_SERIES_ORDER
    global MAX_SERIES_ORDER
    global SERIES_ORDERS
    global LOOP_TYPE_LABELS
    global PRECISION_LABELS
    global TEST_COUNT
    global PRECISION_TEST_COUNT

    cntr_dict = {}
    label_key = 1
    for i in range(len(PRECISION_LABELS)):
        p_label = str(PRECISION_LABELS[i][0]) 
        for j in range(len(LOOP_TYPE_LABELS)):
            lt_label = str(LOOP_TYPE_LABELS[j][0])
            for k in range(len(ARRAY_SIZES)):
                m = ARRAY_SIZES[k]
                for l in range(len(SERIES_ORDERS)):
                    n = SERIES_ORDERS[l]
                    label = p_label + "-" + lt_label + "-" + str(m) + "-" + str(n)
                    cntr_dict[label_key] = { "label": label }
                    label_key += 1
                    
    INDEX_TIME    = 0
    INDEX_STEP    = 1
    INDEX_SUBSTEP = 2
    double_precision = False
    index_cntr = -1
    index_flops = -1
    name = ""

    with open(data_file_name) as fin:
        for line in fin:
            
            cols = line.split()
            
            if "_mpi_lib" in cols[0]:
                # parse header to get counter name
                cols = line.split(',')
                cols[-1] = cols[-1][0:len(cols[-1])-1]
                
                for i, col_name in enumerate(reversed(cols)):
                    col_name = col_name[1:]
                    if col_name == "substep":
                        # we have now iterated past the hardware counters
                        break
                    if 0 < len(flops_cntr_names) and col_name in flops_cntr_names:
                        double_precision = True if "DP" in col_name else False
                        index_flops = len(cols)-1-i
                        if len(cols)-1 == index_flops:
                            index_cntr = index_flops-1
                            name = cols[-2][1:]
                        else:
                            index_cntr = index_flops+1
                            name = cols[-1][1:]

                        if "perf::" in name:
                            name = name[6:]

                if -1 == index_flops:
                    print "Error, none of counter(s) in " + str(flops_cntr_names) + " found in data file."
                    sys.exit()
                    
            elif len(line) > 0:
                step = int(cols[INDEX_STEP])
                if -1 < step:
                    # skip step recorded by pat/papi_mpi_initialise
                    if double_precision:
                        step += PRECISION_TEST_COUNT
                    if step <= TEST_COUNT:
                        # and skip record added by pat/papi_mpi_finalise
                        cntr_dict[step][name] = \
                            { "value": long(cols[index_cntr]), \
                              "flops": long(cols[index_flops]), \
                               "time": float(cols[INDEX_TIME]) }
    
    return cntr_dict



def round2precision(x, p):
    """
    returns a string representation of x formatted with a precision of p

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
    """

    x = float(x)

    if x == 0.:
        return "0." + "0"*(p-1)

    out = []

    if x < 0:
        out.append("-")
        x = -x

    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x/tens)

    if n < math.pow(10, p - 1):
        e = e -1
        tens = math.pow(10, e - p+1)
        n = math.floor(x / tens)

    if abs((n + 1.) * tens - x) <= abs(n * tens -x):
        n = n + 1

    if n >= math.pow(10,p):
        n = n / 10.
        e = e + 1

    m = "%.*g" % (p, n)

    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p -1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e+1])
        if e+1 < len(m):
            out.append(".")
            out.extend(m[e+1:])
    else:
        out.append("0.")
        out.extend(["0"]*-(e+1))
        out.append(m)

    return "".join(out)


script_title = "analyse_counter_variations"
script_version = "v2.0.0"

plt_markers = ['o', '^', 's', 'd']
cbs_palette = ["#d7191c", "#fdae61", "#abd9e9", "#2c7bb6"]
cbs_brush = 0

lt_markers = {'f': 'o', 'i': '^', 'r': 's'}
lt_labels = {'f': "flat", 'i': "inline", 'r': "recursive"}
as_colours = {64: "#d7191c", 256: "#fdae61", 1024: "#abd9e9", 4096: "#2c7bb6"}
as_labels = {64: "64", 256: "256", 1024: "1k", 4096: "4k"}
as_weights = {64: 1.0, 256: 4.0, 1024: 16.0, 4096: 64.0}

ARRAY_SIZES      = [64, 256, 1024, 4096]
MIN_SERIES_ORDER = 1
MAX_SERIES_ORDER = 29
SERIES_ORDERS    = range(MIN_SERIES_ORDER,MAX_SERIES_ORDER+1)
LOOP_TYPE_LABELS = ["flat","inline","recursive"]
PRECISION_LABELS = ["single","double"]
PRECISION_SIZES  = [4,8]
TEST_COUNT = len(PRECISION_LABELS)*len(LOOP_TYPE_LABELS)*len(ARRAY_SIZES)*len(SERIES_ORDERS)
PRECISION_TEST_COUNT = TEST_COUNT/len(PRECISION_LABELS)
    
parse_args()

if 0 == len(flops_cntr_names):
    print "Error, no flops counter name specified."
    sys.exit()
   
cntr_dict = parse_counter_data(data_file_name, cntr_name, cntr_line_size, flops_cntr_names, nprocs)

# setup the list of data movement counters
counters = cntr_dict[1].keys()
counters.remove("label")
counters.sort()
print counters
if cntr_name in counters:
    counters = [cntr_name]
  
cntr_exists = (0 < len(cntr_name) and cntr_name in counters)
if not cntr_exists and 0 < len(cntr_name):
    print "Error, counter \"" + cntr_name + "\" does not exist in data file."
    sys.exit()


# calculate expected values and format the x-axis labels
exp_values = []
plot_labels = []
ef_markers = []
ef_colours = []
ef_labels = []
mn_weights = []
test = 1
while test <= TEST_COUNT:
    label = cntr_dict[test]["label"]
    
    # capture the precision
    p_label = str(label[0])
    p_size  = 8 if "d" == p_label else 4

    # capture loop type and array size
    as_label = label[label.find('-')+1:label.rfind('-')]
    lt_label = as_label[:label.find('-')]
    as_label = as_label[label.find('-')+1:]
    a_size = int(as_label)
    
    # abbreviate array size
    if 64 == a_size:
        as_label = "064"
    elif 1024 == a_size:
        as_label = "01k"
    elif 4096 == a_size:
        as_label = "04k"

    # construct plot label
    plot_label = lt_label + as_label + p_label
    plot_labels.append(plot_label)

    # calculate expected value
    exp_cntr_val = ((2.0*p_size*(a_size**2)*nprocs)/cntr_line_size)*MAX_SERIES_ORDER
    exp_flops_val = 0.0
    for i in range(MIN_SERIES_ORDER,MAX_SERIES_ORDER+1):
        exp_flops_val += (2.0*i-1.0)*(a_size**2)*nprocs
            
    if plot_flops:
        exp_val = exp_flops_val
    elif plot_intensity:
        exp_val = exp_flops_val / (exp_cntr_val*cntr_line_size)
    else:
        exp_val = exp_cntr_val
            
    exp_val = float(round2precision(exp_val, rnd))
    exp_values.append(exp_val)

    ef_markers.append(lt_markers[lt_label])
    ef_colours.append(as_colours[a_size])
    ef_labels.append(lt_labels[lt_label]+"-"+as_labels[a_size])

    mn_weights.append(as_weights[a_size])

    # skip to next set of tests
    test += len(SERIES_ORDERS)


ax = plt.gca()
fig = plt.gcf()

if plot_error_func:
    if plot_flops:
        plt.xlabel("FLOPs")
    elif plot_intensity:
        plt.xlabel("Arithmetic Intensity")
    else:
        plt.xlabel("Counter Value")
else:
    plt.xticks(range(1,len(plot_labels)+1), plot_labels, rotation="70", fontsize=10)
    plt.xlim(0,len(plot_labels)+1)

if cntr_exists:
    if plot_flops:
        plt.ylabel("FLOPs")
        title = flops_cntr_names[0]
        for flops_cntr in flops_cntr_names[1:]:
            title += "," + flops_cntr
        plt.title(title + "  ("+ counters[0] + ")")
        print "Analysing flops data associated with " + cntr_name + " in " + data_file_name + "..."
    elif plot_intensity:
        plt.ylabel("Arithmetic Intensity")
        title = flops_cntr_names[0]
        if 1 < len(flops_cntr_names):
            title += "("
        for flops_cntr in flops_cntr_names[1:]:
            title += "," + flops_cntr
        if 1 < len(flops_cntr_names):
            title += ")"
        plt.title(title + "  /  "+ counters[0])
        print "Analysing arithmetic intensity data associated with " + cntr_name + " in " + data_file_name + "..."
    else:
        plt.ylabel("Counter Value")
        plt.title(counters[0])
        print "Analysing counter data associated with " + cntr_name + " in " + data_file_name + "..."
    if plot_error or plot_error_func:
        plt.ylabel("Error Ratio (recorded / expected)")
else:
    plt.ylabel("Coefficients of Variation")
    plt.title(data_file_name)
    print "Analysing counter data recorded in " + data_file_name + "..."
    
    
with open(log_name, 'w') as log:
    
    for cntr in counters:
        test = 1
        ceoffs_var = []
        totals = []
        flops = []
                
        while test <= TEST_COUNT:
            cntr_vals = []
            flops_vals = []
            for subtest in SERIES_ORDERS:
                cntr_vals.append(cntr_dict[test][cntr]["value"])
                flops_vals.append(cntr_dict[test][cntr]["flops"])
                test += 1
            cntr_vals_np = np.array(cntr_vals)
            flops_vals_np = np.array(flops_vals)

            flops_tot = np.sum(flops_vals_np)
            cntr_tot = np.sum(cntr_vals_np)
            cntr_mu = np.mean(cntr_vals_np)
            cntr_sigma = np.std(cntr_vals_np)
            cntr_coeff = cntr_sigma / cntr_mu

            log.write(str(test) + ": " + round2precision(cntr_mu,rnd) + " +/- " + round2precision(cntr_sigma,rnd) + \
                ", " + round2precision(cntr_coeff,rnd) + "\n")
            log.write(str(test) + ": " + round2precision(cntr_tot,rnd) + "\n")
            log.write(str(test) + ": " + round2precision(flops_tot,rnd) + " FLOPs\n")

            if cntr_exists:
                totals.append(cntr_tot)
                flops.append(flops_tot)
            else:    
                if 0.0 == cntr_mu:
                    min_val = np.min(cntr_vals_np)
                    max_val = np.max(cntr_vals_np)
                    ext = max_val - min_val
                    if ext > 0.0:
                        cntr_mu = (cntr_mu - min_val) / ext
                        cntr_sigma = (cntr_sigma - min_val) / ext

                cntr_mu = abs(cntr_mu)
                ceoffs_var.append((cntr_sigma/cntr_mu) if cntr_mu > 0.0 else 0.0)  

        if cntr_exists:
            errors = []
            rec_values = []
            for i, exp_val in enumerate(exp_values):
                rec_val = totals[i]
                if plot_flops:
                    rec_val = flops[i]
                elif plot_intensity:
                    rec_val = float(flops[i]) / float(rec_val*cntr_line_size)
                errors.append(rec_val/exp_val)
                rec_values.append(rec_val)

            if plot_error:
                plt.plot(range(1,len(plot_labels)+1), errors, marker='o', color="blue")
            elif plot_error_func:
                for i, rec_val in enumerate(rec_values):
                    plt.semilogx(rec_val, errors[i], marker=ef_markers[i], linestyle='None', color=ef_colours[i])
            else:
                if plot_intensity:
                    plt.plot(range(1,len(plot_labels)+1), rec_values, marker='o', color="red", label="recorded")
                    plt.plot(range(1,len(plot_labels)+1), exp_values, marker='d', color="gray", label="expected")
                else:
                    plt.semilogy(range(1,len(plot_labels)+1), rec_values, marker='o', color="red", label="recorded")
                    plt.semilogy(range(1,len(plot_labels)+1), exp_values, marker='d', color="gray", label="expected")
                
            totals_np = np.array(totals)
            log.write(counters[0] + ": " + round2precision(np.mean(totals_np),rnd) + " +/- " + round2precision(np.std(totals_np),rnd) + \
                " [" + round2precision(np.max(totals_np) - np.min(totals_np),rnd) + "]\n")
        else:
            if "_COUNT_HW_" in cntr:
                cntr = cntr.replace("_COUNT_HW_",'_')

            cbs_colour = cbs_palette[cbs_brush] if cbs_brush >= 0 and cbs_brush < len(cbs_palette) else ""
            plt_marker = plt_markers[cbs_brush] if cbs_brush >= 0 and cbs_brush < len(plt_markers) else '.'
            plt.plot(range(1,len(plot_labels)+1), ceoffs_var, marker=plt_marker, label=cntr, color=cbs_colour)
            cbs_brush += 1

            coeffs_np = np.array(ceoffs_var)
            log.write(cntr + ": " + round2precision(np.mean(coeffs_np),rnd) + " +/- " + round2precision(np.std(coeffs_np),rnd) + \
                " [" + round2precision(np.max(coeffs_np) - np.min(coeffs_np),rnd) + "]\n")


ax.tick_params(direction="out")
ax.xaxis.set_ticks_position("bottom")
ax.yaxis.set_ticks_position("both")

if cntr_exists:
    if not (plot_error or plot_error_func):
        plt.legend(ncol=2, loc="lower right", fontsize=9, framealpha=0.75)
    else:
        if plot_error_func:
            ef_legend_items = []
            for a_size in sorted(as_colours.keys()):
                ef_legend_items.append(
                    Line2D([0], [0], marker='o', color=as_colours[a_size], markerfacecolor=as_colours[a_size],
                        label=as_labels[a_size], markersize=7, linestyle = 'None'))
            for lt in sorted(lt_labels.keys()):
                ef_legend_items.append(
                    Line2D([0], [0], marker=lt_markers[lt], color="gray", markerfacecolor="white",
                        label=lt_labels[lt], markersize=7, linestyle = 'None'))
                
            ax.legend(handles=ef_legend_items, loc="upper left", numpoints=1)

else:  
    plt.legend(ncol=1, loc="upper left", fontsize=9, framealpha=0.75)
    if 0.0 == ymax:
        ymin, ymax = plt.ylim()
    plt.ylim(-0.1,ymax)

plt.show()
fig.savefig(fig_name, format='eps', dpi=1000)
plt.clf()

if no_log:
    os.remove(log_name)

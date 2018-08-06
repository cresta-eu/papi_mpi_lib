#!/usr/bin/env python
# Copyright EPCC,
# Michael Bareford, Copyright 2018
# v1.0

import sys
import re
import math
import numpy as np
import matplotlib.pyplot as plt

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

        -data         Name of file containing counter recordings
        -cntr         Name of counter whose value is some proxy for data movement
        -flops        Name of FLOPS counter

        -round        The number of decimal places to round logged results
        -ymax         Maximum limit on y-axis
"""


def init_args():
    global data_file_name
    global cntr_name
    global flops_cntr_names
    global log_name
    global fig_name
    global rnd
    global ymax

    data_file_name = ""
    cntr_name = ""
    flops_cntr_names = []
    log_name = ""
    fig_name = ""
    rnd = 3
    ymax = 0.0

    

def print_args():
    global data_file_name
    global cntr_name
    global flops_cntr_names
    global log_name
    global fig_name
    global rnd
    global ymax

    print "data_file_name =", data_file_name
    print "cntr_name =", cntr_name
    print "flops_cntr_name(s) =", str(flops_cntr_names)
    print "log_name =", log_name
    print "fig_name =", fig_name
    print "rnd =", str(rnd)
    print "ymax =", str(ymax)


    
def parse_args():
    global data_file_name
    global cntr_name 
    global flops_cntr_names
    global log_name
    global fig_name
    global rnd
    global ymax

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
        log_name = fname + ".txt"
        fig_name = fname + ".eps"



def parse_counter_data(data_file_name, cntr_name, flops_names):
    global ARRAY_SIZES
    global SERIES_ORDERS
    global LOOP_TYPES
    global PRECISIONS
    global TEST_COUNT

    cntr_dict = {}
    m = 1
    for i in range(len(PRECISIONS)):
        for j in range(len(LOOP_TYPES)):
            for k in range(len(ARRAY_SIZES)):
                for l in range(len(SERIES_ORDERS)):
                    label = PRECISIONS[i][0] + '-' + LOOP_TYPES[j][0] + '-' + str(ARRAY_SIZES[k]) + '-' + str(SERIES_ORDERS[l])
                    cntr_dict[m] = {"label": label}
                    m += 1
                    
    INDEX_TIME    = 0
    INDEX_STEP    = 1
    INDEX_SUBSTEP = 2
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
                if -1 < step and step <= TEST_COUNT:
                    # skip step recorded by pat/papi_mpi_initialise
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
script_version = "v1.0.0"


ARRAY_SIZES   = [64, 256, 1024, 4096]
MIN_SERIES_ORDER = 1
MAX_SERIES_ORDER = 29
SERIES_ORDERS = range(MIN_SERIES_ORDER,MAX_SERIES_ORDER+1)
LOOP_TYPES    = ["flat","inline","recursive"]
PRECISIONS    = ["single","double"]
TEST_COUNT = len(PRECISIONS)*len(LOOP_TYPES)*len(ARRAY_SIZES)*len(SERIES_ORDERS)
    
parse_args()

if 0 == len(flops_cntr_names):
    print "Error, no flops counter name specified."
    sys.exit()
   
cntr_dict = parse_counter_data(data_file_name, cntr_name, flops_cntr_names)

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
   
if cntr_exists:
    print "Analysing counter data associated with " + cntr_name + " in " + data_file_name + "..."
else:
    print "Analysing counter data associated in " + data_file_name + "..."


# format the x-axis labels
labels = []
test = 1
while test <= TEST_COUNT:
    label = cntr_dict[test]["label"]
    label = label[:label.rfind('-')]
    if "1024" in label:
        label = label.replace("1024","1k")
    elif "4096" in label:
        label = label.replace("4096","4k")
    labels.append(label)
    test += len(SERIES_ORDERS)


do_scatter = False
ax = plt.gca()
fig = plt.gcf()

plt.xticks(range(1,len(labels)+1), labels, rotation="70", fontsize=10)
plt.xlim(0,len(labels)+1)

if cntr_exists:
    plt.ylabel("counter value")
    plt.title(counters[0])
else:
    plt.ylabel("coefficients of variation")
    plt.title(data_file_name)
    
    
with open(log_name, 'w') as log:
    
    for cntr in counters:
        test = 1
        ceoffs_var = []
        means = []
        stds = []
        while test <= TEST_COUNT:
            cntr_vals = []
            for subtest in SERIES_ORDERS:
                cntr_vals.append(cntr_dict[test][cntr]["value"])
                test += 1
            cntr_vals_np = np.array(cntr_vals)

            mu = np.mean(cntr_vals_np)
            sigma = np.std(cntr_vals_np)
            coeff = sigma / mu

            log.write(str(test) + ": " + str(round2precision(mu,3)) + " +/- " + str(round2precision(sigma,3)) + \
                ", " + str(round2precision(coeff,3)) + "\n")

            if cntr_exists:
                means.append(mu)
                stds.append(sigma)
            else:    
                if 0.0 == mu:
                    min_val = np.min(cntr_vals_np)
                    max_val = np.max(cntr_vals_np)
                    ext = max_val - min_val
                    if ext > 0.0:
                        mu = (mu - min_val) / ext
                        sigma = (sigma - min_val) / ext

                mu = abs(mu)
                ceoffs_var.append((sigma/mu) if mu > 0.0 else 0.0)  

        if cntr_exists:
            if do_scatter:
                plt.scatter(range(1,len(labels)+1), means, s=100, marker='.')
            else:
                plt.plot(range(1,len(labels)+1), means, marker='o')
                plt.errorbar(range(1,len(labels)+1), means, yerr=stds)

            means_np = np.array(means)
            log.write(counters[0] + ": " + str(round2precision(np.mean(means_np),3)) + " +/- " + str(round2precision(np.std(means_np),3)) + \
                " [" + str(round2precision(np.max(means_np) - np.min(means_np),3)) + "]\n")
        else:
            if "_COUNT_HW_" in cntr:
                cntr = cntr.replace("_COUNT_HW_",'_')
            if do_scatter:
                plt.scatter(range(1,len(labels)+1), ceoffs_var, s=100, marker='.', label=cntr)
            else:
                plt.plot(range(1,len(labels)+1), ceoffs_var, marker='o', label=cntr)

            coeffs_np = np.array(ceoffs_var)
            log.write(cntr + ": " + str(round2precision(np.mean(coeffs_np),3)) + " +/- " + str(round2precision(np.std(coeffs_np),3)) + \
                " [" + str(round2precision(np.max(coeffs_np) - np.min(coeffs_np),3)) + "]\n")


ax.tick_params(direction="out")
ax.xaxis.set_ticks_position("bottom")
ax.yaxis.set_ticks_position("both")
if 0.0 == ymax:
  ymin, ymax = plt.ylim()
plt.ylim(-0.1,ymax)
  
plt.legend(ncol=1, loc="upper right", fontsize=10)
plt.show()
fig.savefig(fig_name, format='eps', dpi=1000)
plt.clf()

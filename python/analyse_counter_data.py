#!/usr/bin/env python
# Copyright EPCC,
# Michael Bareford, Copyright 2018
# v1.0
#
#
# python analyse_counter_data.py -data ./jetcrf_papi/arc/PERF_COUNT_HW_CACHE_L1D/nek5kpapi.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -min-substep 1 -max-substep 6 -multiplier 64 -unit 9 -shave-steps 20
#
# python analyse_counter_data.py -data ./jetcrf_papi/arc/PERF_COUNT_HW_CACHE_L1D/fluid/nek5kpapi.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -min-substep 1 -max-substep 5 -map-substep '{ "1": [1,6], "2": [2,7], "3": [3,8], "4": [9], "5": [10] }' -multiplier 64 -unit 9 -shave-steps 20
#
# python analyse_counter_data.py -data ./jetcrf_papi/arc/PERF_COUNT_HW_CACHE_L1D/fluid/plan3/nek5kpapi.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -min-substep 1 -max-substep 6 -map-substep '{ "1": [1], "2": [8], "3": [9], "4": [10], "5": [11], "6": [12] }' -multiplier 64 -unit 9 -shave-steps 20
#


import sys
import re
import json
import collections
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
    print """usage: python analyse_counter_data.py -data data_file_name -cntr cntr_name -min-substep min -max-substep max

    By default the raw counter value per time step will be plotted.

    Arguments:

        -data         Name of file containing counter recordings
        -cntr         Name of counter whose value is some proxy for data movement
        -flops        Name of FLOPS counter
        -log          Name of log file

        -multiplier   The multiplier required to convert from counter value to bytes (typically cache line size)
        -unit         The cntr/flops unit expressed as a power of 10
        -round        The number of decimal places to round logged results

        -min-substep  The minimum substep number within a single (time) step
        -max-substep  The maximum substep number within a single (time) step
        -map-substep  A dictionary that maps a substep number written the data file to a 'normalised' substep number.
                      Such mappings are necessary when branching logic is active within a time step.

        -from-step    Plot/log from (time) step number -from-step
        -to-step      Plot/log to (time) step number -to-step
        -shave-steps  The first and last -shave-steps steps are not plotted/logged

        -show-plot           Show plot to user not just to eps file
        -plot-data-movement  Plot the amount of data movement per (time) step (the multiplier is used to convert the
                             the raw counter value to bytes).
        -plot-time           Plot the execution time per (time) step
        -plot-flops          Plot the number of FLOPs executed per (time) step
        -plot-flops-rate     Plot the number of FLOPs executed per second per (time) step
        -plot-intensity      Plot the arithmetic intensity per (time) step
"""

    

def init_args():
    global data_file_name
    global cntr_name
    global flops_cntr_name
    global log_name
    global multiplier
    global unit
    global rnd
    global min_substep
    global max_substep
    global map_substep
    global from_step
    global to_step
    global shave_steps
    global show_plot
    global plot_data_movement
    global plot_time
    global plot_flops
    global plot_flops_rate
    global plot_intensity
    data_file_name = ""
    cntr_name = ""
    flops_cntr_name = ""
    log_name = ""
    multiplier = 1.0
    unit = 1.0
    rnd = 3
    min_substep = 1
    max_substep = 2
    map_substep = {}
    from_step = 1
    to_step = -1
    shave_steps = 0
    show_plot = False
    plot_data_movement = False
    plot_time = False
    plot_flops = False
    plot_flops_rate = False
    plot_intensity = False


    
def print_args():
    global data_file_name
    global cntr_name
    global flops_cntr_name
    global log_name
    global multiplier
    global unit
    global rnd
    global min_step
    global max_step
    global min_substep
    global max_substep
    global map_substep
    global from_step
    global to_step
    global shave_steps
    global show_plot
    global plot_data_movement
    global plot_time
    global plot_flops
    global plot_flops_rate
    global plot_intensity
    print "data_file_name =", data_file_name
    print "cntr_name =", cntr_name
    print "flops_cntr_name =", flops_cntr_name
    print "log_name =", log_name
    print "multiplier =", str(multiplier)
    print "unit =", str(unit)
    print "rnd =", str(rnd)
    print "min_step =", str(min_step)
    print "max_step =", str(max_step)
    print "min_substep =", str(min_substep)
    print "max_substep =", str(max_substep)
    print "map_substep =", str(map_substep)
    print "from_step =", str(from_step)
    print "to_step =", str(to_step)
    print "shave_steps =", str(shave_steps)
    print "show_plot =", str(show_plot)
    print "plot_data_movement =", str(plot_data_movement)
    print "plot_time =", str(plot_time)
    print "plot_flops =", str(plot_flops)
    print "plot_flops_rate =", str(plot_flops_rate)
    print "plot_intensity =", str(plot_intensity)

    
    
def parse_args():
    global data_file_name
    global cntr_name 
    global flops_cntr_name
    global log_name
    global multiplier
    global unit
    global rnd
    global min_substep
    global max_substep
    global map_substep
    global from_step
    global to_step
    global shave_steps
    global show_plot
    global plot_data_movement
    global plot_time
    global plot_flops
    global plot_flops_rate
    global plot_intensity
    
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
            flops_cntr_name = sys.argv[i+1]
            i += 2
        elif arg == "-log":
            log_name = sys.argv[i+1]
            i += 2

        elif arg == "-multiplier":
            multiplier = float(sys.argv[i+1])
            i += 2
        elif arg == "-unit":
            unit_str = "1e"+sys.argv[i+1]
            unit = float(unit_str)
            i += 2
        elif arg == "-round":
            rnd = int(sys.argv[i+1])
            i += 2
        
        elif arg == "-min-substep":
            min_substep = int(sys.argv[i+1])
            i += 2
        elif arg == "-max-substep":
            max_substep = int(sys.argv[i+1])
            i += 2
        elif arg == "-map-substep":
            map_substep = json.loads(sys.argv[i+1])
            i += 2
            
        elif arg == "-from-step":
            from_step = int(sys.argv[i+1])
            i += 2
        elif arg == "-to-step":
            to_step = int(sys.argv[i+1])
            i += 2
        elif arg == "-shave-steps":
            shave_steps = int(sys.argv[i+1])
            i += 2

        elif arg == "-show-plot":
            show_plot = True
            i += 1
        elif arg == "-plot-data-movement":
            plot_data_movement = True
            i += 1
        elif arg == "-plot-time":
            plot_time = True
            i += 1
        elif arg == "-plot-flops":
            plot_flops = True
            i += 1
        elif arg == "-plot-flops-rate":
            plot_flops_rate = True
            i += 1
        elif arg == "-plot-intensity":
            plot_intensity = True
            i += 1

        else:
            print "Error, argument", arg, "not recognised."
            help()
            sys.exit()
        

    if 0 == len(log_name):
        log_name = cntr_name.replace(":","-") if ":" in cntr_name else cntr_name
        log_name = log_name + ".txt"
        
    if 0 == len(map_substep):
        for i in range(min_substep,max_substep+1):
            map_substep[i] = [i]

        

    
def parse_counter_data(data_file_name, cntr_name, flops_name):

    cntr_dict = { "time": [], "step": [], "substep": [],
                  "value": [], "flops": [] }

    INDEX_TIME    = 0
    INDEX_STEP    = 1
    INDEX_SUBSTEP = 2
    index_value = -1
    index_flops = -1

    with open(data_file_name) as fin:
        for line in fin:
            
            cols = line.split()
            
            if "_mpi_lib" in cols[0]:
                # parse header to get counter name
                cols = line.split(',')
                cols[-1] = cols[-1][0:len(cols[-1])-1]
                
                for i, col_name in enumerate(reversed(cols)):
                    if col_name == " substep":
                        # we have now iterated past the hardware counters
                        break
                    if 0 < len(cntr_name) and cntr_name in col_name:
                        index_value = len(cols)-1-i
                    elif 0 < len(flops_cntr_name) and flops_cntr_name in col_name:
                        index_flops = len(cols)-1-i
                    
            elif len(line) > 0:
                step = int(cols[INDEX_STEP])
                if -1 < step:
                    # skip step recorded by pat/papi_mpi_initialise
                    cntr_dict["time"].append(float(cols[INDEX_TIME]))
                    cntr_dict["step"].append(step)
                    cntr_dict["substep"].append(int(cols[INDEX_SUBSTEP]))
                    if -1 < index_value:
                        cntr_dict["value"].append(long(cols[index_value]))
                    if -1 < index_flops:
                        cntr_dict["flops"].append(long(cols[index_flops]))

                    
    # remove record called from pat/papi_mpi_finalise
    cntr_dict["time"] = cntr_dict["time"][:-1]
    cntr_dict["step"] = cntr_dict["step"][:-1]
    cntr_dict["substep"] = cntr_dict["substep"][:-1]
    cntr_dict["value"] = cntr_dict["value"][:-1]
    cntr_dict["flops"] = cntr_dict["flops"][:-1]
                
    return cntr_dict



def get_mapped_substep(ss):
    global min_substep
    global max_substep
    global map_substep

    for mss in map_substep:
        if ss in map_substep[mss]:
            return int(mss)

    print "Error, mapped substep not found for substep ", str(ss), "."
    sys.exit()

    

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



def get_unit_label(unit, suffix):
    label = ""
    
    if 1e3 == unit:
        label = "k"
    elif 1e6 == unit:
        label = "M"
    elif 1e9 == unit:
        label = "G"
    elif 1e12 == unit:
        label = "T"
        
    return label + suffix



script_title = "analyse_counter_data"
script_version = "v1.0.0"

parse_args()

cntr_dict = parse_counter_data(data_file_name, cntr_name, flops_cntr_name)
cntr_exists = (0 < len(cntr_dict["value"]))
flops_cntr_exists = (0 < len(cntr_dict["flops"]))

if not cntr_exists:
    if 0 == len(cntr_name):
        print "Error, no counter name specified."
    else:
        print "Error, counter \"" + cntr_name + "\" does not exist in data file."
    sys.exit()
    
    
print "Analysing counter data associated with " + cntr_name + " in " + data_file_name + "..."

max_step = cntr_dict["step"][-1]
min_step = from_step if shave_steps < from_step else shave_steps+1
max_step = to_step if -1 < to_step and to_step < max_step-shave_steps else max_step-shave_steps


# collating substep data
substep_values = collections.OrderedDict({ "time": [], "value": [] })
if flops_cntr_exists:
    substep_values["flops"] = []
    substep_values["flops-rate"] = []
    substep_values["intensity"] = []
for key in substep_values:
    substep_values[key] = [[] for i in range(max_substep)]

#print_args()

for i in range(len(cntr_dict["value"])):
    step = cntr_dict["step"][i]
    if step < min_step:
        continue
    elif step > max_step:
        break
    
    substep = get_mapped_substep(cntr_dict["substep"][i])-1
    substep_values["time"][substep].append(cntr_dict["time"][i])
    substep_values["value"][substep].append(cntr_dict["value"][i])

    if flops_cntr_exists:
        substep_values["flops"][substep].append(cntr_dict["flops"][i])
        substep_values["flops-rate"][substep].append(cntr_dict["flops"][i]/cntr_dict["time"][i])
        substep_values["intensity"][substep].append(cntr_dict["flops"][i]/(cntr_dict["value"][i]*multiplier))


# logging substep data
with open(log_name, 'w') as log:

    substep_sums = {}
    
    for key in substep_values:

        substep_sums[key] = 0.0
        for i in range(max_substep):
            values_np = np.array(substep_values[key][i])
            substep_sums[key] += np.sum(values_np)

        for i in range(max_substep):
            values_np = np.array(substep_values[key][i])
            avg = round2precision(np.mean(values_np),rnd)
            dev = round2precision(np.std(values_np),rnd)
            min = round2precision(np.min(values_np),rnd)
            max = round2precision(np.max(values_np),rnd)
            sum = round2precision(np.sum(values_np),rnd)
            per = round2precision((float(sum)/substep_sums[key])*100.0,rnd)
            log.write(key + ": " + str(1+i) + ": " + avg + " +/- " + dev + " [" + min + " - " + max + "] " + str(per) + "%\n")
            if "value" == key:
                unit_label = get_unit_label(unit, "B")
                avg = round2precision(float(avg)*(multiplier/unit),rnd)
                dev = round2precision(float(dev)*(multiplier/unit),rnd)
                min = round2precision(float(min)*(multiplier/unit),rnd)
                max = round2precision(float(max)*(multiplier/unit),rnd)
                log.write(key + ": " + str(1+i) + ": " + avg + " +/- " + dev + " [" + min + " - " + max + "] [" + unit_label + "]\n")
            elif "flops" in key:
                unit_label = get_unit_label(unit, "FLOPs")
                if "flops-rate" == key:
                    unit_label += "/sec"
                avg = round2precision(float(avg)/(unit),rnd)
                dev = round2precision(float(dev)/(unit),rnd)
                min = round2precision(float(min)/(unit),rnd)
                max = round2precision(float(max)/(unit),rnd)
                log.write(key + ": " + str(1+i) + ": " + avg + " +/- " + dev + " [" + min + " - " + max + "] [" + unit_label + "]\n")
            log.write("\n")

        log.write("\n")

    log.write("\n")
        
    
# collating (time) step data
step_values = collections.OrderedDict({ "step": [], "time": [], "value": [] })
if flops_cntr_exists:
    step_values["flops"] = []
    step_values["flops-rate"] = []
    step_values["intensity"] = []
    
for i in range(len(cntr_dict["value"])):
    step = cntr_dict["step"][i]
    if step < min_step:
        continue
    elif step > max_step:
        break
    
    substep = get_mapped_substep(cntr_dict["substep"][i])
    if min_substep == substep and min_substep == cntr_dict["substep"][i]:
        step_values["step"].append(cntr_dict["step"][i])
        step_values["time"].append(0.0)
        step_values["value"].append(0)
        if flops_cntr_exists:
            step_values["flops"].append(0)

    step_values["time"][-1] += cntr_dict["time"][i]
    step_values["value"][-1] += cntr_dict["value"][i]
    if flops_cntr_exists:
        step_values["flops"][-1] += cntr_dict["flops"][i]
        if max_substep == substep:
            step_values["flops-rate"].append(step_values["flops"][-1] / step_values["time"][-1])
            step_values["intensity"].append(step_values["flops"][-1] / (step_values["value"][-1]*multiplier))
        
# logging (time) step data
with open(log_name, 'a') as log:

    for key in step_values:
        if "step" == key:
            continue
        
        values_np = np.array(step_values[key])
        avg = round2precision(np.mean(values_np),rnd)
        dev = round2precision(np.std(values_np),rnd)
        min = round2precision(np.min(values_np),rnd)
        max = round2precision(np.max(values_np),rnd)
        log.write(key + ": " + avg + " +/- " + dev + " [" + min + " - " + max + "]\n")
        if "value" == key:
            unit_label = get_unit_label(unit, "B")
            avg = round2precision(float(avg)*(multiplier/unit),rnd)
            dev = round2precision(float(dev)*(multiplier/unit),rnd)
            min = round2precision(float(min)*(multiplier/unit),rnd)
            max = round2precision(float(max)*(multiplier/unit),rnd)
            log.write(key + ": " + avg + " +/- " + dev + " [" + min + " - " + max + "] [" + unit_label + "]\n")
        elif "flops" in key:
            unit_label = get_unit_label(unit, "FLOPs")
            if "flops-rate" == key:
                unit_label += "/sec"
            avg = round2precision(float(avg)/(unit),rnd)
            dev = round2precision(float(dev)/(unit),rnd)
            min = round2precision(float(min)/(unit),rnd)
            max = round2precision(float(max)/(unit),rnd)
            log.write(key + ": " + avg + " +/- " + dev + " [" + min + " - " + max + "] [" + unit_label + "]\n")
        log.write("\n")

    log.write("\n")

    
# plotting (time) step data
plt.xlabel("step")
plt.ylabel("counter value")
plot_values = step_values["value"]
plt.title(cntr_name)
fig_name = cntr_name.replace(":","-") if ":" in cntr_name else cntr_name

if plot_data_movement:
    unit_label = get_unit_label(unit, "B")
    plt.ylabel("data movement ["+unit_label+"]")
    plot_values = [x*multiplier/unit for x in plot_values]
    fig_name += "-data"
elif plot_time:
    unit_label = "s"
    plt.ylabel("time ["+unit_label+"]")
    plot_values = step_values["time"]
    fig_name += "-time"
elif plot_flops:
    unit_label = get_unit_label(unit, "FLOPs")
    plt.ylabel(unit_label)
    plot_values = step_values["flops"]
    plot_values = [x/unit for x in plot_values]
    plt.title(flops_cntr_name)
    fig_name += "-" + flops_cntr_name
elif plot_flops_rate:
    unit_label = get_unit_label(unit, "FLOPs/sec")
    plt.ylabel(unit_label)
    plot_values = step_values["flops-rate"]
    plot_values = [x/unit for x in plot_values]
    plt.title(flops_cntr_name)
    fig_name += "-" + flops_cntr_name + "-rate"
elif plot_intensity:
    plt.ylabel("arithmetic intensity [FLOPs/byte]")
    plot_values = step_values["intensity"]
    fig_name += "-" + flops_cntr_name + "-intensity"
    
fig_name += ".eps"
    
    
plt.plot(step_values["step"], plot_values, marker='o')

plt.xlim(step_values["step"][0],step_values["step"][-1])    
values_np = np.array(plot_values)
plt.ylim(np.min(values_np),np.max(values_np))

if show_plot:
    plt.show()
plt.savefig(fig_name)
plt.clf()

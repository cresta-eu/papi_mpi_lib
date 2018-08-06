#!/bin/bash --login

if [ "$1" == "archer" ] || [ "$1" == "" ]; then
  ./gen_counter_plots.sh archer papi cray O0n24
  ./gen_counter_plots.sh archer papi cray O3n24
  ./gen_counter_plots.sh archer papi intel O0n24
  ./gen_counter_plots.sh archer papi intel O3n24
  ./gen_counter_plots.sh archer papi gnu O0n24
  ./gen_counter_plots.sh archer papi gnu O3n24
elif [ "$1" == "cirrus" ]; then
  ./gen_counter_plots.sh cirrus papi intel O0n36
  ./gen_counter_plots.sh cirrus papi intel O3n36
  ./gen_counter_plots.sh cirrus papi gnu O0n36
  ./gen_counter_plots.sh cirrus papi gnu O3n36
fi

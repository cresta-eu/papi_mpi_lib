#!/bin/bash

if [ "$1" == "archer2" ]; then

  # See the "install_pypp.sh" script for how to install
  # a local Python post-processing virtual environment.
  . ${HOME/home/work}/utils/pypp/bin/activate

  ./gen_counter_plots.sh archer2 papi cray O0n128
  ./gen_counter_plots.sh archer2 papi cray O3n128
  ./gen_counter_plots.sh archer2 papi gnu O0n128
  ./gen_counter_plots.sh archer2 papi gnu O3n128
  ./gen_counter_plots.sh archer2 papi aocc O0n128
  ./gen_counter_plots.sh archer2 papi aocc O3n128

  deactivate

else

  echo -e "Error, unrecognised system, $1."

fi

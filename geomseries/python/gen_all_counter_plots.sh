#!/bin/bash --login

if [ "$1" == "archer2" ] || [ "$1" == "" ]; then
  module -q restore
  module -q load cpe/21.09
  module -q load PrgEnv-gnu
  module -q load cray-python

  export LD_LIBRARY_PATH=${CRAY_LD_LIBRARY_PATH}:${LD_LIBRARY_PATH}

  ROOT=${HOME/home/work}
  PYPP_HOME=${ROOT}/utils/pypp

  . ${PYPP_HOME}/bin/activate

  ./gen_counter_plots.sh archer2 papi cray O0n128
  ./gen_counter_plots.sh archer2 papi cray O3n128
  ./gen_counter_plots.sh archer2 papi gnu O0n128
  ./gen_counter_plots.sh archer2 papi gnu O3n128
  ./gen_counter_plots.sh archer2 papi aocc O0n128
  ./gen_counter_plots.sh archer2 papi aocc O3n128

  deactivate
fi

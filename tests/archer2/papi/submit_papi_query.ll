#!/bin/bash --login
  
#SBATCH -J papi
#SBATCH --time=00:20:00
#SBATCH --exclusive
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --account=<budget code>
#SBATCH --partition=standard
#SBATCH --qos=standard
#SBATCH --export=none


function papi_query() {
  export LD_LIBRARY_PATH=/opt/cray/pe/papi/$2/lib64:/opt/cray/libfabric/$3/lib64
  module -q restore

  module -q load cpe/$1
  module -q load papi/$2

  mkdir -p $1
  papi_component_avail -d &> $1/papi_component_avail.txt
  papi_native_avail -c &> $1/papi_native_avail.txt
  papi_avail -c -d &> $1/papi_avail.txt
}


papi_query 22.12 6.0.0.17 1.12.1.2.2.0.0


# pat_help counters rome deriv
# pat_help counters rome native
# pat_help counters rome groups
# pat_help counters rome papi

#!/bin/bash --login
  
#SBATCH --job-name=papi
#SBATCH --nodes=1
#SBATCH --tasks-per-node=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --account=z19
#SBATCH --partition=standard
#SBATCH --qos=short

module -q restore
module -q load cpe/21.09
module -q load PrgEnv-cray

module -q load papi 

export LD_LIBRARY_PATH=${CRAY_LD_LIBRARY_PATH}:${LD_LIBRARY_PATH}


export OMP_NUM_THREADS=1
export PAPI_RT_PERFCTR=PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_FP_OPS,PAPI_FP_INS

srun --distribution=block:block --hint=nomultithread --unbuffered ./papi_mpi_test

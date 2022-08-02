#!/bin/bash --login
  
#SBATCH --job-name=geoms
#SBATCH --nodes=1
#SBATCH --tasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --account=z19
#SBATCH --partition=standard
#SBATCH --qos=standard


module -q restore
module -q load cpe/21.09
module -q load PrgEnv-aocc

module -q load papi

export LD_LIBRARY_PATH=${CRAY_LD_LIBRARY_PATH}:${LD_LIBRARY_PATH}


SRUN_ARGS="--distribution=block:block --hint=nomultithread --unbuffered -n ${SLURM_NTASKS}"


exename=./exe/O0/cray/geomseries_CRAY
#exename=./exe/O3/cray/geomseries_CRAY
#exename=./exe/O0/gnu/geomseries_GNU
#exename=./exe/O3/gnu/geomseries_GNU
#exename=./exe/O0/aocc/geomseries_AOCC
#exename=./exe/O3/aocc/geomseries_AOCC

export OMP_NUM_THREADS=1


export PAPI_RT_PERFCTR=PAPI_TOT_CYC,PAPI_FP_OPS,PAPI_L1_DCA
srun ${SRUN_ARGS} ${exename} -nodouble

export PAPI_RT_PERFCTR=PAPI_TOT_CYC,PAPI_FP_OPS,PAPI_L1_DCA
srun ${SRUN_ARGS} ${exename} -nosingle


export PAPI_RT_PERFCTR=PAPI_TOT_CYC,PAPI_FP_OPS,PERF_COUNT_HW_CACHE_L1D
srun ${SRUN_ARGS} ${exename} -nodouble

export PAPI_RT_PERFCTR=PAPI_TOT_CYC,PAPI_FP_OPS,PERF_COUNT_HW_CACHE_L1D
srun ${SRUN_ARGS} ${exename} -nosingle


export PAPI_RT_PERFCTR=PAPI_TOT_CYC,PAPI_FP_OPS,PERF_COUNT_HW_CACHE_LL:ACCESS
srun ${SRUN_ARGS} ${exename} -nodouble

export PAPI_RT_PERFCTR=PAPI_TOT_CYC,PAPI_FP_OPS,PERF_COUNT_HW_CACHE_LL:ACCESS
srun ${SRUN_ARGS} ${exename} -nosingle


export PAPI_RT_PERFCTR=PAPI_TOT_CYC,PAPI_FP_OPS,PERF_COUNT_HW_CACHE_NODE:ACCESS
srun ${SRUN_ARGS} ${exename} -nodouble

export PAPI_RT_PERFCTR=PAPI_TOT_CYC,PAPI_FP_OPS,PERF_COUNT_HW_CACHE_NODE:ACCESS
srun ${SRUN_ARGS} ${exename} -nosingle

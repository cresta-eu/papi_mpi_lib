#!/bin/bash --login
  
#SBATCH --job-name=geoms
#SBATCH --nodes=1
#SBATCH --tasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --account=z19
#SBATCH --partition=standard
#SBATCH --qos=standard


export OMP_NUM_THREADS=1


declare -a optimisation_level=("O0" "O3")
declare -a compiler=("cray" "gnu" "aocc")
declare -a papi_counters=("PAPI_L1_DCA" "PERF_COUNT_HW_CACHE_L1D" "PERF_COUNT_HW_CACHE_LL:ACCESS" "PERF_COUNT_HW_CACHE_NODE:ACCESS")
declare -a geomseries_precision=("-nodouble" "-nosingle")

BASIC_PAPI_CNTRS="PAPI_TOT_CYC,PAPI_FP_OPS"
SRUN_ARGS="--distribution=block:block --hint=nomultithread --unbuffered -n ${SLURM_NTASKS}"

for cmp in "${compiler[@]}"; do

  for opt in "${optimisation_level[@]}"; do

    exename=${SLURM_SUBMIT_DIR}/exe/${cmp}/${opt}/geomseries_${cmp^^}
    
    respath=${SLURM_SUBMIT_DIR}/results/${cmp}/${opt}n128
    mkdir -p ${respath}

    for papi_cntr in "${papi_counters[@]}"; do

      export PAPI_RT_PERFCTR="${BASIC_PAPI_CNTRS},${papi_cntr}"

      for gs_prec in "${geomseries_precision[@]}"; do
        
        srun ${SRUN_ARGS} ${exename} ${gs_prec}

	if [ -f "${respath}/papi_test.out" ]; then
	  cat papi_test.out >> ${respath}/papi_test.out
	  rm papi_test.out
	else
	  mv papi_test.out ${respath}/
	fi

      done

    done
  done
done

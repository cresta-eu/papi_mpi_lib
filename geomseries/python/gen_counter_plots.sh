#!/bin/bash --login

if [ "$1" == "archer" ]; then

  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -flops PAPI_FP_OPS -ymax 5.0
  
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 24
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PAPI_L2_DCA -flops PAPI_FP_OPS -nprocs 24
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_LL:ACCESS -flops PAPI_FP_OPS -nprocs 24
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_NODE:ACCESS -flops PAPI_FP_OPS -nprocs 24

  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 24 -plot-error -no-log
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 24 -plot-error-func -no-log

  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 24 -plot-flops -no-log
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 24 -plot-flops -plot-error -no-log
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 24 -plot-flops -plot-error-func -no-log

  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 24 -plot-intensity -no-log
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 24 -plot-intensity -plot-error -no-log
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 24 -plot-intensity -plot-error-func -no-log

elif [ "$1" == "cirrus" ]; then

  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -ymax 7.0

  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_L1D:ACCESS -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PAPI_L2_DCA -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_LL:ACCESS -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PERF_COUNT_HW_CACHE_NODE:ACCESS -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36

  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PAPI_L2_DCA -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36 -plot-error -no-log
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PAPI_L2_DCA -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36 -plot-error-func -no-log

  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PAPI_L2_DCA -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36 -plot-flops -no-log
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PAPI_L2_DCA -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36 -plot-flops -plot-error -no-log
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PAPI_L2_DCA -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36 -plot-flops -plot-error-func -no-log

  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PAPI_L2_DCA -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36 -plot-intensity -no-log
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PAPI_L2_DCA -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36 -plot-intensity -plot-error -no-log
  python analyse_counter_variations.py -data ../arc/$3/$4/$2_test.out -cntr PAPI_L2_DCA -single-flops PAPI_SP_OPS -double-flops PAPI_DP_OPS -nprocs 36 -plot-intensity -plot-error-func -no-log

fi

if ls ./*.eps 1> /dev/null 2>&1; then
  mv *.eps ../arc/$3/$4/
  mv *.txt ../arc/$3/$4/
fi

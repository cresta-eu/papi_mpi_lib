#!/bin/bash --login

if [ "$1" == "archer2" ]; then

  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -flops PAPI_FP_OPS -ymax 5.0
  
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L1_DCA -flops PAPI_FP_OPS -nprocs 128
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L2_DCR -flops PAPI_FP_OPS -nprocs 128
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L2_DCH -flops PAPI_FP_OPS -nprocs 128
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L2_DCM -flops PAPI_FP_OPS -nprocs 128
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 128


  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 128 -plot-error -no-log
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 128 -plot-error-func -no-log

  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 128 -plot-flops -no-log
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 128 -plot-flops -plot-error -no-log
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 128 -plot-flops -plot-error-func -no-log

  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 128 -plot-intensity -no-log
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 128 -plot-intensity -plot-error -no-log
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS -nprocs 128 -plot-intensity -plot-error-func -no-log


  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L2_DCR -flops PAPI_FP_OPS -nprocs 128 -plot-error -no-log
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L2_DCR -flops PAPI_FP_OPS -nprocs 128 -plot-error-func -no-log

  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L2_DCR -flops PAPI_FP_OPS -nprocs 128 -plot-flops -no-log
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L2_DCR -flops PAPI_FP_OPS -nprocs 128 -plot-flops -plot-error -no-log
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L2_DCR -flops PAPI_FP_OPS -nprocs 128 -plot-flops -plot-error-func -no-log

  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L2_DCR -flops PAPI_FP_OPS -nprocs 128 -plot-intensity -no-log
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L2_DCR -flops PAPI_FP_OPS -nprocs 128 -plot-intensity -plot-error -no-log
  python analyse_counter_variations.py -path ../results/$3/$4 -data $2_test.out -cntr PAPI_L2_DCR -flops PAPI_FP_OPS -nprocs 128 -plot-intensity -plot-error-func -no-log

fi

if ls ./*.eps 1> /dev/null 2>&1; then
  mv *.eps ../results/$3/$4/
  mv *.txt ../results/$3/$4/
fi

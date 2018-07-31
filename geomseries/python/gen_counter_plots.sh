python analyse_counter_variations.py -data ../arc/$2/$3/$1_test.out -flops PAPI_FP_OPS

python analyse_counter_variations.py -data ../arc/$2/$3/$1_test.out -cntr PERF_COUNT_HW_CACHE_L1D -flops PAPI_FP_OPS
python analyse_counter_variations.py -data ../arc/$2/$3/$1_test.out -cntr PAPI_L2_DCA -flops PAPI_FP_OPS
python analyse_counter_variations.py -data ../arc/$2/$3/$1_test.out -cntr PERF_COUNT_HW_CACHE_LL:ACCESS -flops PAPI_FP_OPS
python analyse_counter_variations.py -data ../arc/$2/$3/$1_test.out -cntr PERF_COUNT_HW_CACHE_NODE:ACCESS -flops PAPI_FP_OPS

mv *.eps ../arc/$2/$3/
mv *.txt ../arc/$2/$3/

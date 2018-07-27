#!/bin/bash

# ./analyse_counter_data.sh papi PERF_COUNT_HW_CACHE_L1D PAPI_FP_OPS 
# ./analyse_counter_data.sh papi PAPI_L2_DCA PAPI_FP_OPS
# ./analyse_counter_data.sh papi PERF_COUNT_HW_CACHE_LL PAPI_FP_OPS 
# ./analyse_counter_data.sh papi PERF_COUNT_HW_CACHE_NODE PAPI_FP_OPS  

path=./jetcrf_$1/arc/$2/
map="-min-substep 1 -max-substep 6"

echo $path
echo $map

python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-data-movement
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-time
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-flops
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-flops-rate
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-intensity

mv *.eps *.txt $path


path=./jetcrf_$1/arc/$2/fluid
map="-min-substep 1 -max-substep 5 -map-substep {\"1\":[1,6],\"2\":[2,7],\"3\":[3,8],\"4\":[9],\"5\":[10]}"

echo $path
echo $map

python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-data-movement
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-time
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-flops
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-flops-rate
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-intensity

mv *.eps *.txt $path


path=./jetcrf_$1/arc/$2/fluid/plan3
map="-min-substep 1 -max-substep 6 -map-substep {\"1\":[1],\"2\":[8],\"3\":[9],\"4\":[10],\"5\":[11],\"6\":[12]}"

echo $path
echo $map

python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-data-movement
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-time
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-flops
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-flops-rate
python analyse_counter_data.py -data $path/nek5k$1.out -cntr $2 -flops $3 $map -multiplier 64 -unit 9 -shave-steps 20 -plot-intensity

mv *.eps *.txt $path

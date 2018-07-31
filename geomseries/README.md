The `geomseries` code is designed to run through a set of geometric series calculations in such a way
that the CPU undergoes a range of arithmetic intensities.

Each run of `geomseries` performs `696*np` sets of geometric series calculations, where `np` is the
number of MPI processes.

A set of calculations depends on the size, `m`, of a 2D array; there are four sizes, 64, 256, 1024 and 4096.
For each element in the array, `n` geometric series calculations are performed six times, where `n` is the
series order in the range 1 to 29. 

A single geometric series calculation is actually repeated: once, using single precision, for three different
loop implementations, flat, inline and recursive; then the three calculations are repeated using double precision.
Hence the factor of `696` mentioned earlier comes from `2*3*29*4`.

The makefile is intended for use on the ARCHER Cray XC30 MPP Supercomputer:

Before compiling please load the papi module (`module load papi`), and then compile by running `make`.
The `geomseries` code should automatically link to freshly built `libpapimpi` library.

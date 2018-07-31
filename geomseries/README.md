The `geomseries` code is designed to run through a set of geometric series calculations in such a way<br>
that the CPU undergoes a range of arithmetic intensities, measured as FLOPs per byte. In theory, the<br>
size of the data movement is always the number of bytes required for two variables (16 for double precision,<br>
8 for single), regardless of the number of terms in the geometric series.

The `geomseries` code then allows us to evaluate which PAPI counters are the most consistent as measures<br>
of data movement. The calculation of a geometric series will change a counter's value. If we record the size<br>
of these changes for different series orders, we should find that the variation in those recorded values is<br>
close to zero, assuming that the counter acts as good proxy for data movement.

The scheme described above has already been implemented by Kwack et al. 2018 for the Blue Waters Cray XE6 platform.

J. Kwack, G. Arnold, C. Mendes G. H. Bauer, National Center for Supercomputing Applications, University of Illinois at Urbana-Champaign, [Roofline Analysis with Cray Performance Analysis Tools (CrayPat) and Roofline-based Performance Projections for a Future Architecture](https://bluewaters.ncsa.illinois.edu/liferay-content/document-library/content/BWsymposium_2018_CrayPAT_based_Roofline_Analysis_v02.pdf), Cray User Group Conference Proceedings 2018.

The code listed here has been tested on the ARCHER Cray XC30 MPP Supercomputer. Before compiling please load<br>
the papi module (`module load papi`), and then compile by running `make`. The `geomseries` code should automatically<br>
link to a freshly built `libpapimpi` library.

It should be possible to run `geomseries` on non-Cray platforms too; however, it will be necessary to change<br>
the makefile. What follows is a more detailed description of the workings of `geomseries`.

Each run of `geomseries` performs `696*np` sets of geometric series calculations, where `np` is the<br>
number of MPI processes.

A set of calculations depends on the size, `m`, of a 2D array; there are four sizes, 64, 256, 1024 and 4096.<br>
For each element in the array, `n` geometric series calculations are performed six times, where `n` is the<br>
series order in the range 1 to 29. 

A single geometric series calculation is actually repeated: once, using single precision, for three different<br>
loop implementations, flat, inline and recursive; then the three calculations are repeated using double precision.<br>
Hence, the factor of `696` mentioned earlier comes from `2*3*29*4`.

The `submit.pbs` file is also intended for the ARCHER platform. This submission script calls six versions of the<br> `geomseries` executable that cover the Cray, Intel and GNU compilers with no optimisations (`-O0`) and with `-O3`.<br>
Furthermore, the script is setup to evaluate several counters, one for each cache level and one for the node memory.


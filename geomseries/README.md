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

The code listed here has been tested on the ARCHER Cray XC30 MPP Supercomputer. Before compiling please run the configure script to set the platform and compiler: e.g., `source ./configure archer cray 3` will prepare your environment for building `geomseries` on the ARCHER platform using the Cray compiler and with the optimisation level set to 3. The actual compilation is then done by running `make`. The `geomseries` code should automatically link to a freshly built `libpapimpi` library.

It should be possible to run `geomseries` on non-Cray platforms too; however, it will be necessary to change<br>
the configure/make files. What follows is a more detailed description of the workings of `geomseries`.

Each run of `geomseries` performs `464*np` sets of geometric series calculations, where `np` is the<br>
number of MPI processes.

A set of calculations depends on the size, `m`, of a 2D array; there are four sizes, 64, 256, 1024 and 4096.<br>
For each element in the array, `n` geometric series calculations are performed four times, where `n` is the<br>
series order in the range 1 to 29. 

A single geometric series calculation is actually repeated: once, using single precision, for two different<br>
loop implementations, flat and recursive; then the three calculations are repeated using double precision.<br>
Hence, the factor of `464` mentioned earlier comes from `2*2*29*4`. (Please note, originally the third loop<br>
type, inline, was also implemented but this has now been removed due to the reasons given in [notes.md](https://github.com/cresta-eu/papi_mpi_lib/blob/master/geomseries/notes.md)).

The `submit.pbs` file is also intended for the ARCHER platform. This submission script calls six versions of the<br> `geomseries` executable that cover the Cray, Intel and GNU compilers with no optimisations (`-O0`) and with `-O3`.<br>
Furthermore, the script is setup to evaluate several counters, one for each cache level and one for the node memory.

Once a `geomseries` job has completed the output can be processed by the `python/analyse_counter_variations.py`<br>
script in order to produce plots similar to the ones presented by Kwack et al. 2018.

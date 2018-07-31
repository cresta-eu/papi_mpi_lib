The geomseries code is designed to run through a set of geometric series calculations
in such a way that the CPU undergoes a range of arithmetic intensities.

The makefile is intended for use on the ARCHER Cray XC30 MPP Supercomputer:

Before compiling please load the papi module (`module load papi`),
and then compile by running `make`. The geomseries code should automatically link
to freshly built `libpapimpi` library.

# Copyright (c) 2018 The University of Edinburgh

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FC=ftn
CC=cc
ifeq ($(PE_PLAT),cirrus)
  FC=mpif90
  CC=mpicc
  ifeq ($(PE_ENV),INTEL)
    FC=mpiifort
    CC=mpiicc
  endif
endif

ifeq ($(PE_PLAT),cirrus)
  FFLAGS_EXTRA=-DUSE_MPIF_H
endif

ifeq ($(PE_PLAT),archer)
  CFLAGS_EXTRA=-DUSE_PERF_EVENT_H
endif

ifneq ($(PE_ENV),CRAY)
  CFLAGS_EXTRA2=-std=c99
endif

CFLAGS = -fPIC $(CFLAGS_EXTRA) $(CFLAGS_EXTRA2)
FFLAGS = $(FFLAGS_EXTRA)

all: papi_mpi_lib.o libpapimpi.a libpapimpi.so papi_mpi_test papi_mpi_testf

papi_mpi_lib.o: papi_mpi_lib.c papi_mpi_lib.h
	$(CC) $(CFLAGS) -c papi_mpi_lib.c

libpapimpi.a: papi_mpi_lib.o
	ar rcs $@ $^

libpapimpi.so: papi_mpi_lib.o
	$(CC) -fPIC -shared -o libpapimpi.so papi_mpi_lib.o

papi_mpi_lib_interface.o: papi_mpi_lib_interface.f90
	$(FC) $(FFLAGS) -c papi_mpi_lib_interface.f90

papi_mpi_testf: papi_mpi_testf.F90 papi_mpi_lib_interface.o papi_mpi_lib.o
	$(FC) $(FFLAGS) -o papi_mpi_testf papi_mpi_testf.F90 papi_mpi_lib_interface.o papi_mpi_lib.o -lpapi

papi_mpi_test: papi_mpi_test.c papi_mpi_lib.o papi_mpi_lib.h
	$(CC) $(CFLAGS) -o papi_mpi_test papi_mpi_test.c papi_mpi_lib.o -lpapi

clean: 
	$(RM) *.o *.mod *.out *.a *.so pat_mpi_test pat_mpi_testf

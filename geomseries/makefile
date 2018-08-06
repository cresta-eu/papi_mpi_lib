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
  ifeq ($(PE_ENV),intel)
    FC=mpiifort
    CC=mpiicc
  endif
endif

CFLAGS_EXTRA=-std=c99
ifeq ($(PE_PLAT),cirrus)
  FFLAGS_EXTRA=-DUSE_MPIF_H
endif

CFLAGS = -O$(PE_OPT_LEVEL) -fPIC $(CFLAGS_EXTRA)
FFLAGS = -O$(PE_OPT_LEVEL) $(FFLAGS_EXTRA)

all: papi_mpi_lib.o libpapimpi.a libpapimpi.so geomseries

papi_mpi_lib.o: ../papi_mpi_lib.c ../papi_mpi_lib.h
	$(CC) $(CFLAGS) -c ../papi_mpi_lib.c

libpapimpi.a: papi_mpi_lib.o
	ar rcs $@ $^

libpapimpi.so: papi_mpi_lib.o
	$(CC) ${CFLAGS} -shared -o libpapimpi.so papi_mpi_lib.o

papi_mpi_lib_interface.o: ../papi_mpi_lib_interface.f90
	$(FC) ${FFLAGS} -c ../papi_mpi_lib_interface.f90

geomseries: geomseries.F90 papi_mpi_lib_interface.o papi_mpi_lib.o
	$(FC) ${FFLAGS} -o geomseries_$(PE_ENV) geomseries.F90 papi_mpi_lib_interface.o papi_mpi_lib.o -lpapi

clean: 
	$(RM) *.o *.mod *.out *.a *.so geomseries_$(PE_ENV)

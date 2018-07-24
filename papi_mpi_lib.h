/* 
  Copyright (c) 2018 The University of Edinburgh.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

#ifndef PAPI_MPI_LIB_H
#define PAPI_MPI_LIB_H

extern void papi_mpi_initialise(const char* out_fn);
extern void papi_mpi_reset(const int initial_sync);
extern int papi_mpi_record(const int nstep, const int sstep, const int initial_sync, const int initial_rec);
extern void papi_mpi_finalise();

#endif

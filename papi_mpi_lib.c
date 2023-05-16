/* 
  Copyright (c) 2023 The University of Edinburgh.

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

#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <mpi.h>
#include "papi.h"

#ifdef USE_PERF_EVENT_H 
#include "perfmon/perf_event.h"
#endif

#include "papi_mpi_lib.h"


static char ver[]="1.0.0";

#define PAPI_MPI_LIB_UNINITIALISED 1001
#define MAX_NAME_LEN 128
#define PAPI_RT_SEPARATOR ","

static int nprocs = 0;
static int rank = -1;
static int root_rank = -1;

static FILE* log_fp = NULL;
static int first_record = 1;
static double tm0 = 0.0;
static double tm = 0.0;
static int last_nstep = 0;

static int papi_res = 0;
static int cntr_event_set = PAPI_NULL;
static int ncntrs = 0;
static char** cntr_names = NULL;
static int* cntr_ids = NULL;
static long long* cntr_values = NULL;
static long long* cntr_value_totals = NULL;

static int initialised = 0;
static int debug = 0;


// return 1 if papi_mpi_initialise has been called successfully
int papi_mpi_ok() {
  int ok = 0;

  if (-1 != rank && -1 != root_rank && nprocs > 0) {
    ok = 1;

    ok = (0 != ok && ncntrs > 0);

    ok = (0 != ok && NULL != cntr_names);
    for (int i = 0; i < ncntrs; i++) {
      ok = (0 != ok && NULL != cntr_names[i]);
    }
    ok = (0 != ok && NULL != cntr_ids && NULL != cntr_values);
    
    if (root_rank == rank) {
      ok = (0 != ok && NULL != cntr_value_totals);
    } 

    ok = (0 != ok && PAPI_LOW_LEVEL_INITED == PAPI_is_initialized());
    ok = (0 != ok && PAPI_NULL != cntr_event_set && ncntrs == PAPI_num_events(cntr_event_set));
    if (root_rank == rank) {
      ok = (0 != ok && NULL != log_fp);
    }
  } // end of <if (-1 != rank && -1 != root_rank && nprocs > 0)> clause

  return ok;
}


// get the PAPI counter names specified in the submission script
// allocate memory to hold PAPI counter names, ids and values
// initialise PAPI library, create PAPI event set and start the PAPI counters
// root rank opens the output file
// all being well call papi_mpi_record(-1,1,1,0)
void papi_mpi_initialise(const char* log_fpath) {
  
  int str_len = 0;
  char* cntr_list_str = NULL;
  char* name_str = NULL;
  PAPI_event_info_t cntr_info;

  if (0 != initialised) {
    // already initialised
    return;
  }
  
  // initialise MPI variables
  MPI_Comm_size(MPI_COMM_WORLD, &nprocs);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  root_rank = 0;

  // get the counter names specified in the submission script
  ///////////////////////////////////////////////////////////
  ncntrs = 0;
  cntr_list_str = getenv("PAPI_RT_PERFCTR");
  str_len = (NULL == cntr_list_str) ? 0 : strlen(cntr_list_str);
  ncntrs = str_len > 0 ? 1 : 0;
  for (int i = 0; i < str_len; i++) {
    if (PAPI_RT_SEPARATOR[0] == cntr_list_str[i]) {
      ncntrs++;
    }
  }
  if (0 != debug && 0 == rank) {
    printf("%d: %d PAPI counters listed.\n", rank, ncntrs);
  }
  if (ncntrs <= 0) {
    printf("%d: no PAPI counters specified.\n", rank);
    return;
  }
  ///////////////////////////////////////////////////////////

  // allocate memory to hold PAPI counter names, ids and values
  ///////////////////////////////////////////////////////////////////////////////////
  cntr_names = (char**) calloc(ncntrs, sizeof(char*));
  if (!cntr_names) {
    printf("%d: unable to allocate memory for PAPI counter names.\n", rank);
    return;
  }
  for (int i = 0; i < ncntrs; i++) {
    cntr_names[i] = (char*) calloc(MAX_NAME_LEN, sizeof(char));
  }
  name_str = strtok(cntr_list_str, PAPI_RT_SEPARATOR);
  for (int i = 0; i < ncntrs; i++) {
    if (NULL != name_str && NULL != cntr_names[i]) {
      str_len = strlen(name_str);
      strncpy(cntr_names[i], name_str, str_len);
      name_str = strtok(NULL, PAPI_RT_SEPARATOR);
    }
  }
  cntr_ids = (int*) calloc(ncntrs, sizeof(int));
  if (NULL == cntr_ids) {
    printf("%d: unable to allocate memory for PAPI counter ids.\n", rank);
    return;
  }
  cntr_values = (long long*) calloc(ncntrs, sizeof(long long));
  if (NULL == cntr_values) {
    printf("%d: unable to allocate memory for PAPI counter values.\n", rank);
    return;
  }
  if (root_rank == rank) {
    cntr_value_totals = (long long*) calloc(ncntrs, sizeof(long long));
    if (NULL == cntr_value_totals) {
      printf("%d: unable to allocate memory for PAPI counter value totals.\n", rank);
      return;
    }
  }
  else {
    cntr_value_totals = NULL;
  }
  ///////////////////////////////////////////////////////////////////////////////////

  // initialise PAPI library, create PAPI event set and start the PAPI counters
  /////////////////////////////////////////////////////////////////////////////////////////////////////
  papi_res = PAPI_library_init(PAPI_VER_CURRENT);
  if (PAPI_VER_CURRENT != papi_res) {
    printf("%d: PAPI_library_init(%d) failed with error %d.\n", rank, PAPI_VER_CURRENT, papi_res);
    return;
  }
  cntr_event_set = PAPI_NULL;
  papi_res = PAPI_create_eventset(&cntr_event_set);
  if (PAPI_OK != papi_res) {
    printf("%d: PAPI_create_eventset failed with error %d.\n", rank, papi_res);
    return;
  }   
  for (int i = 0; i < ncntrs; i++) {
    papi_res = PAPI_event_name_to_code(cntr_names[i],cntr_ids+i);
    if (PAPI_OK != papi_res) {
      printf("%d: PAPI_event_name_to_code(%s) failed with error %d.\n", rank, cntr_names[i], papi_res);
      break;
    }	
    papi_res = PAPI_query_event(cntr_ids[i]);
    if (PAPI_OK != papi_res) {
      printf("%d: PAPI_query_event(%s) failed with error %d.\n", rank, cntr_names[i], papi_res);
      break;
    }
    papi_res = PAPI_add_event(cntr_event_set, cntr_ids[i]);
    if (PAPI_OK != papi_res) {
      printf("%d: PAPI_add_event(%s) failed with error %d.\n", rank, cntr_names[i], papi_res);
      break;
    }	
    if (0 != debug) {
      if (root_rank == rank) {
        papi_res = PAPI_get_event_info(cntr_ids[i], &cntr_info);
        if (PAPI_OK != papi_res) {
          printf("%d: PAPI_get_event_info(%s) failed with error %d.\n", rank, cntr_names[i], papi_res);
          break;
        }
        printf("%s\n", cntr_names[i]);
        printf("symbol: %s\n", cntr_info.symbol);
        printf("short desc: %s\n", cntr_info.short_descr);
        printf("long desc: %s\n", cntr_info.long_descr);
        printf("units: %s\n", cntr_info.units);
        printf("component_index: %d\n", cntr_info.component_index);
        printf("location: %d\n", cntr_info.location);
        printf("update_freq: %d\n", cntr_info.update_freq);
        printf("note: %s\n\n", cntr_info.note);
      }
      MPI_Barrier(MPI_COMM_WORLD);
    }
  } // end of <for (i = 0; i < ncntrs; i++)> loop

  if (PAPI_OK != papi_res) {
    // error occurred setting up PAPI event set
    return;
  }

  papi_res = PAPI_start(cntr_event_set);
  if (PAPI_OK != papi_res) {
    printf("%d: PAPI_start failed with error %d.\n", rank, papi_res);
    return;
  }
  /////////////////////////////////////////////////////////////////////////////////////////////////////
  
  // root rank opens file for counter data
  ////////////////////////////////////////
  if (root_rank == rank) {
    if (NULL != log_fp) {
      fclose(log_fp);
      log_fp = NULL;
    }
    
    // open performance counter data file
    if (NULL != log_fpath) {
      struct stat buffer;   
      if (0 == stat(log_fpath, &buffer)) {
        log_fp = fopen(log_fpath, "a");
      }
      else {
        log_fp = fopen(log_fpath, "w");
      }
    }
    if (NULL == log_fp) {
      log_fp = fopen("./papi_log.out", "w");
    }
  }
  ////////////////////////////////////////
 
  int all_ok = papi_mpi_ok();
  if (0 != debug) {
    printf("%d: papi_mpi_ok() returned %d.\n", rank, all_ok);
  }
  MPI_Allreduce(MPI_IN_PLACE, &all_ok, 1, MPI_LOGICAL, MPI_LAND, MPI_COMM_WORLD);
  if (0 == all_ok) {
    initialised = 0;
    papi_mpi_finalise();
  }
  else {
    // do initial recording call, which ends with MPI_Barrier
    initialised = 1;
    first_record = 1;
    papi_mpi_record(-1, 1, 1, 0);
  }
  
} // end of papi_mpi_initialise() function


// reset the PAPI counters to zero
void papi_mpi_reset(const int initial_sync) {
  if (0 == initialised) {
    return;
  }

  if (0 != initial_sync) {
    MPI_Barrier(MPI_COMM_WORLD);
  }

  if (root_rank == rank) {
    tm0 = MPI_Wtime();
  }
  
  papi_res = PAPI_reset(cntr_event_set);
  if (PAPI_OK != papi_res) {
    printf("%d: PAPI_reset failed with error %d.\n", rank, papi_res);
  }
}


// read counter values and output those value totals if root rank
int papi_mpi_read_counter_values(const int nstep, const int sstep) {
   
  if (root_rank == rank) {
    tm = MPI_Wtime();
    if (0 != first_record) {
      tm0 = tm;
      first_record = 0;
    }
  }

  // read counters
  if (ncntrs > 0) {
    papi_res = PAPI_read(cntr_event_set, cntr_values);
    if (PAPI_OK != papi_res) {
      printf("%d: PAPI_read failed with error %d.\n", rank, papi_res);
    }

    MPI_Reduce(cntr_values, cntr_value_totals, ncntrs, MPI_UNSIGNED_LONG_LONG, MPI_SUM, root_rank, MPI_COMM_WORLD);
  }

  // update counter data file
  if (root_rank == rank) {
    if (NULL != log_fp) {
      if (tm0 == tm) {
        fprintf(log_fp, "papi_mpi_lib v%s: time (s), step, substep", ver);
        for (int i = 0; i < ncntrs; i++) {
          fprintf(log_fp, ", %s", cntr_names[i]);
        }
        fprintf(log_fp, "\n");
      }
      fprintf(log_fp, "%f %d %d", tm-tm0, nstep, sstep);
      for (int i = 0; i < ncntrs; i++) {
        fprintf(log_fp, " %llu", cntr_value_totals[i]);
      }
      fprintf(log_fp, "\n");
    }
  }

  return papi_res;
  
} // end of papi_mpi_read_counter_values() function


// read and record counter values
// the reading will be labelled with the step and substep numbers
// if initial_sync is true MPI_Barrier is called before reading takes place
// if initial_sync and initial_rec are true then counters are read before and after initial barrier
// initial_rec is only used when initial_sync is true
int papi_mpi_record(const int nstep, const int sstep, const int initial_sync, const int initial_rec) {
   
  if (0 == initialised) {
    return PAPI_MPI_LIB_UNINITIALISED;
  }

  int res = PAPI_OK;
  if (0 != initial_sync) {
    if (0 != initial_rec) {
      res = papi_mpi_read_counter_values(nstep, sstep);
    }
	
    MPI_Barrier(MPI_COMM_WORLD);
  }

  if (PAPI_OK == res) {
    res = papi_mpi_read_counter_values(nstep, sstep);
  }
    
  last_nstep = nstep;

  MPI_Barrier(MPI_COMM_WORLD);

  return res;
  
} // end of papi_mpi_record() function


// do the last recording call
// stop the PAPI counters, destroy the PAPI event set and shutdown the PAPI library
// deallocate the memory used to store PAPI counter names, ids and values
// close performance counter data file
void papi_mpi_finalise() {
  
  if (0 != initialised) {
    // do the last recording call
    papi_mpi_record(last_nstep+1, 1, 1, 0);
  }

  // stop the PAPI counters, destroy the PAPI event set and shutdown the PAPI library
  ///////////////////////////////////////////////////////////////////////////////////
  if (PAPI_NULL != cntr_event_set) {
    papi_res = PAPI_stop(cntr_event_set, cntr_values);
    if (PAPI_OK != papi_res) {
      printf("%d: PAPI_stop failed with error %d.\n", rank, papi_res);
    }
    papi_res = PAPI_cleanup_eventset(cntr_event_set);
    if (PAPI_OK != papi_res) {
      printf("%d: PAPI_cleanup_eventset failed with error %d.\n", rank, papi_res);
    }
    papi_res = PAPI_destroy_eventset(&cntr_event_set);
    if (PAPI_OK != papi_res) {
      printf("%d: PAPI_destroy_eventset failed with error %d.\n", rank, papi_res);
    }
  }
  PAPI_shutdown();
  ///////////////////////////////////////////////////////////////////////////////////

  // deallocate the memory used to store PAPI counter names, ids and values
  /////////////////////////////////////////////////////////////////////////
  if (ncntrs > 0) {
    if (root_rank == rank && NULL != cntr_value_totals) {
      free(cntr_value_totals);
      cntr_value_totals = NULL;
    }
    if (NULL != cntr_values) {
      free(cntr_values);
      cntr_values = NULL;
    }
    if (NULL != cntr_ids) {
      free(cntr_ids);
      cntr_ids = NULL;
    }	
    for (int i = 0; i < ncntrs; i++) {
      if (NULL != cntr_names[i]) {
	free(cntr_names[i]);
	cntr_names[i] = NULL;
      }
    }
    free(cntr_names);
    cntr_names = NULL;
    
    ncntrs = 0;
  }
  /////////////////////////////////////////////////////////////////////////

  // close performance counter data file
  if (rank == root_rank) {
    if (NULL != log_fp) {
      fclose(log_fp);
      log_fp = NULL;
    }
  }

  root_rank = -1;
  rank = -1;
  nprocs = 0;

  initialised = 0;
  MPI_Barrier(MPI_COMM_WORLD); 
  
} // end of papi_mpi_finalise() function

! Copyright (c) 2018 The University of Edinburgh

! Licensed under the Apache License, Version 2.0 (the "License");
! you may not use this file except in compliance with the License.
! You may obtain a copy of the License at

! http://www.apache.org/licenses/LICENSE-2.0

! Unless required by applicable law or agreed to in writing, software
! distributed under the License is distributed on an "AS IS" BASIS,
! WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
! See the License for the specific language governing permissions and
! limitations under the License.

program papi_testf
  use mpi
  use papi_mpi_lib
  
  implicit none
 
  integer :: ierr, i, res
  integer :: comm, rank
  character (len=14) :: out_fn = "papi_test.out"//CHAR(0)
  
  call MPI_Init(ierr)
  
  call papi_mpi_initialise(out_fn)

  do i=1,10
    call papi_mpi_reset(1)
    call sleep(1)
    res = papi_mpi_record(1,i,1,0)
  end do

  call papi_mpi_finalise()

  call MPI_Finalize(ierr)
 
end program papi_testf


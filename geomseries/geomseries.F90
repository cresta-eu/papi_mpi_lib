program geomseries
#ifndef USE_MPIF_H
  use mpi
#endif
  use papi_mpi_lib
  implicit none
#ifdef USE_MPIF_H
  include "mpif.h"
#endif
  
  integer, parameter :: ARRAY_SIZE_CNT = 4
  integer, parameter :: MIN_SERIES_ORDER = 1
  integer, parameter :: MAX_SERIES_ORDER = 29
  integer, parameter :: LOOP_TYPE_CNT = 3
  integer, parameter :: PRECISION_TYPE_CNT = 2
  
  integer :: nargs = 0
  integer :: iarg
  character(len=20) :: arg_name
  logical :: cs_single = .true.
  logical :: cs_double = .true.
  integer :: comm, rank, size, ierr
  integer, dimension(ARRAY_SIZE_CNT) :: array_sizes = (/ 64, 256, 1024, 4096 /)
  integer :: i, m, n, lt, id
  character (len=15) :: out_fn = "papi_test.out"//CHAR(0)
   

  nargs = command_argument_count()
  if (nargs > 0) then
    do iarg = 1, nargs
      call get_command_argument(iarg, arg_name)
      select case(adjustl(arg_name))
        case("-nosingle")
          cs_single = .false.
        case("-nodouble")
          cs_double = .false.
      endselect
    enddo
  endif
 
  comm = MPI_COMM_WORLD
  call MPI_INIT(ierr)
  call MPI_COMM_RANK(comm, rank, ierr)
  call MPI_COMM_SIZE(comm, size, ierr)

  call papi_mpi_initialise(out_fn)
  
  id = 1
  do i = 1, 4
    m = array_sizes(i)
    do n = 1, 29
      do lt = 1, LOOP_TYPE_CNT
        if (cs_single) then
          call calc_series_single(rank, m, n, lt, id)
        endif
        if (cs_double) then
          call calc_series_double(rank, m, n, lt, id+1)
        endif
        id = id + 2
      enddo
    enddo
  enddo

  call papi_mpi_finalise()
   
  call MPI_FINALIZE(ierr)
end program geomseries


subroutine calc_series_single(rk, m, n, lt, id)
  use papi_mpi_lib
  implicit none
    
  integer, intent(in) :: rk, m, n, lt, id

  integer, parameter :: GS_SINGLE_PRECISION = selected_real_kind(6,30)
  integer, parameter :: LOOP_TYPE_FLAT = 1
  integer, parameter :: LOOP_TYPE_INLINE = 2
  integer, parameter :: LOOP_TYPE_RECURSIVE = 3
  integer :: i, j, k, stat
    
  real(kind=GS_SINGLE_PRECISION), dimension(:,:), pointer :: im, om
  character(32) :: label
  
  write(label,'(i4,a1,i2,a1,i1,a1,i1)') m, ',', n, ',', lt, ',', 1
  label = trim(label)
  write(*,*) 'calc_series_single: label=', label
  
  nullify(im)
  nullify(om)
  
  allocate(im(m,m))
  allocate(om(m,m))
  
  call random_number(im)

  if (lt .eq. LOOP_TYPE_RECURSIVE) then

    call papi_mpi_reset(1)
    do i=1,m
      do j=1,m
        om(i,j) = 1.0  
        do k=1,n
          om(i,j) = om(i,j)*im(i,j) + 1.0
        enddo   
      enddo
    enddo
    stat = papi_mpi_record(id,1,1,0)
    if (stat .ne. 0) write(*,*) rk, ': papi_mpi_record: error=', stat
    
  elseif (lt .eq. LOOP_TYPE_INLINE) then

    call papi_mpi_reset(1)
    do i=1,m
      do j=1,m
!DIR$ INLINE         
        do k=0,n
          om(i,j) = im(i,j)**k
        enddo   
      enddo
    enddo
    stat = papi_mpi_record(id,1,1,0)
    if (stat .ne. 0) write(*,*) rk, ': papi_mpi_record: error=', stat
    
  else
    
    ! if (lt .eq. LOOP_TYPE_FLAT) then
    call papi_mpi_reset(1)
    do i=1,m
      do j=1,m
        om(i,j) = 1.0
        do k=1,n
          om(i,j) = om(i,j) + im(i,j)**k
        enddo   
      enddo
    enddo
    stat = papi_mpi_record(id,1,1,0)
    if (stat .ne. 0) write(*,*) rk, ': papi_mpi_record: error=', stat
    
  endif
 
  deallocate(om)
  deallocate(im)
end subroutine calc_series_single


subroutine calc_series_double(rk, m, n, lt, id)
  use papi_mpi_lib
  implicit none
    
  integer, intent(in) :: rk, m, n, lt, id

  integer, parameter :: GS_DOUBLE_PRECISION = selected_real_kind(15,307)
  integer, parameter :: LOOP_TYPE_FLAT = 1
  integer, parameter :: LOOP_TYPE_INLINE = 2
  integer, parameter :: LOOP_TYPE_RECURSIVE = 3
  integer :: i, j, k, stat
  
  real(kind=GS_DOUBLE_PRECISION), dimension(:,:), pointer :: imm, omm
  character(32) :: label
  
  write(label,'(i4,a1,i2,a1,i1,a1,i1)') m, ',', n, ',', lt, ',', 2
  label = trim(label)
  write(*,*) 'calc_series_double: label=', label
  
  nullify(imm)
  nullify(omm)
  
  allocate(imm(m,m))
  allocate(omm(m,m))
  
  call random_number(imm)

  if (lt .eq. LOOP_TYPE_RECURSIVE) then

    call papi_mpi_reset(1)
    do i=1,m
      do j=1,m
        omm(i,j) = 1.0  
        do k=1,n
          omm(i,j) = omm(i,j)*imm(i,j) + 1.0
        enddo   
      enddo
    enddo
    stat = papi_mpi_record(id,1,1,0)
    if (stat .ne. 0) write(*,*) rk, ': papi_mpi_record: error=', stat
    
  elseif (lt .eq. LOOP_TYPE_INLINE) then

    call papi_mpi_reset(1)
    do i=1,m
      do j=1,m
!DIR$ INLINE         
        do k=0,n
          omm(i,j) = imm(i,j)**k
        enddo   
      enddo
    enddo
    stat = papi_mpi_record(id,1,1,0)
    if (stat .ne. 0) write(*,*) rk, ': papi_mpi_record: error=', stat
    
  else
    
    ! if (lt .eq. LOOP_TYPE_FLAT) then
    call papi_mpi_reset(1)
    do i=1,m
      do j=1,m
        omm(i,j) = 1.0
        do k=1,n
          omm(i,j) = omm(i,j) + imm(i,j)**k
        enddo   
      enddo
    enddo
    stat = papi_mpi_record(id,1,1,0)
    if (stat .ne. 0) write(*,*) rk, ': papi_mpi_record: error=', stat
    
  endif

  deallocate(omm)
  deallocate(imm)
end subroutine calc_series_double

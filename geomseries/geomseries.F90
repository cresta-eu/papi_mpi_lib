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
  integer, parameter :: LOOP_TYPE_CNT = 2
  integer, parameter :: PRECISION_TYPE_CNT = 2
  integer, parameter :: SINGLE_PRECISION_TYPE = 1
  integer, parameter :: DOUBLE_PRECISION_TYPE = 2
  
  integer :: nargs = 0
  integer :: iarg
  character(len=20) :: arg_name
  character(len=10) :: arg_value
  integer :: comm, rank, size, ierr
  logical, dimension(PRECISION_TYPE_CNT) :: precision_types = (/ .true., .true. /)
  integer, dimension(ARRAY_SIZE_CNT) :: array_sizes = (/ 64, 256, 1024, 4096 /)
  integer*4 :: cs = 0
  integer :: pt, lt, i, m, n, id
  character (len=15) :: out_fn = "papi_test.out"//CHAR(0)
   

  nargs = command_argument_count()
  if (nargs > 0) then
    iarg = 1
    do while (iarg .le. nargs)
      call get_command_argument(iarg, arg_name)
      select case(adjustl(arg_name))
        case("-nosingle")
          precision_types(SINGLE_PRECISION_TYPE) = .false.
        case("-nodouble")
          precision_types(DOUBLE_PRECISION_TYPE) = .false.
        case("-cachesize")
          ! specify the size of the cache that should be
          ! filled (via allocate) before geometric series
          ! calculations commence 
          iarg = iarg + 1  
          call get_command_argument(iarg, arg_value)
          read(arg_value,*) cs
      endselect
      iarg = iarg + 1 
    enddo
  endif
 
  comm = MPI_COMM_WORLD
  call MPI_INIT(ierr)
  call MPI_COMM_RANK(comm, rank, ierr)
  call MPI_COMM_SIZE(comm, size, ierr)

  call papi_mpi_initialise(out_fn)
  
  id = 1
  do pt = 1, PRECISION_TYPE_CNT
    if (precision_types(pt)) then
        
      do lt = 1, LOOP_TYPE_CNT
        do i = 1, ARRAY_SIZE_CNT
          m = array_sizes(i)  
          do n = MIN_SERIES_ORDER, MAX_SERIES_ORDER
            if (pt .eq. SINGLE_PRECISION_TYPE) then
              call calc_series_single(rank, m, n, lt, id, cs/4)
            else if (pt .eq. DOUBLE_PRECISION_TYPE) then
              call calc_series_double(rank, m, n, lt, id, cs/8)
            endif
            id = id + 1
          enddo
        enddo
      enddo
   
    endif
  enddo
     
  call papi_mpi_finalise()
   
  call MPI_FINALIZE(ierr)
end program geomseries


subroutine calc_series_single(rk, m, n, lt, id, cs)
  use papi_mpi_lib
  implicit none
    
  integer, intent(in) :: rk, m, n, lt, id
  integer*4, intent(in) :: cs
  
  integer, parameter :: GS_SINGLE_PRECISION = selected_real_kind(6,30)
  integer, parameter :: LOOP_TYPE_FLAT = 1
  integer, parameter :: LOOP_TYPE_RECURSIVE = 2
  integer :: m2, i, j, k, stat
    
  real(kind=GS_SINGLE_PRECISION), dimension(:), pointer :: im, om
  real(kind=GS_SINGLE_PRECISION), dimension(:), pointer :: cf
  character(64) :: label

  if (0 .eq. rk) then
    write(label,'(i4,a1,i2,a1,i1,a1,i1,a1,i6)') m, ',', n, ',', lt, ',', 1, ',', cs
    label = trim(label)
    write(*,*) 'calc_series_single: label=', label
  endif

  if (cs .gt. 0) nullify(cf)
  nullify(im)
  nullify(om)

  if (cs .gt. 0) allocate(cf(cs))
  m2 = m**2
  allocate(im(m2),om(m2))
  
  if (cs .gt. 0) cf = 1.0
  call random_number(im)
  om = 1.0
  
  if (lt .eq. LOOP_TYPE_RECURSIVE) then

    call papi_mpi_reset(1)
    do i=1,m2
      do k=1,n
        om(i) = 1.0 + om(i)*im(i)
      enddo   
    enddo
    stat = papi_mpi_record(id,1,1,0)
    if (stat .ne. 0) write(*,*) rk, ': papi_mpi_record: error=', stat
    
  else
    
    ! if (lt .eq. LOOP_TYPE_FLAT) then
    call papi_mpi_reset(1)
    do i=1,m2
      do k=1,n
        om(i) = om(i) + im(i)**k
      enddo   
    enddo
    stat = papi_mpi_record(id,1,1,0)
    if (stat .ne. 0) write(*,*) rk, ': papi_mpi_record: error=', stat
    
  endif
 
  deallocate(om,im)
  if (cs .gt. 0) deallocate(cf)
end subroutine calc_series_single


subroutine calc_series_double(rk, m, n, lt, id, cs)
  use papi_mpi_lib
  implicit none
    
  integer, intent(in) :: rk, m, n, lt, id
  integer*4, intent(in) :: cs

  integer, parameter :: GS_DOUBLE_PRECISION = selected_real_kind(15,307)
  integer, parameter :: LOOP_TYPE_FLAT = 1
  integer, parameter :: LOOP_TYPE_RECURSIVE = 2
  integer :: m2, i, j, k, stat
  
  real(kind=GS_DOUBLE_PRECISION), dimension(:), pointer :: imm, omm
  real(kind=GS_DOUBLE_PRECISION), dimension(:), pointer :: cff
  character(64) :: label

  if (0 .eq. rk) then
    write(label,'(i4,a1,i2,a1,i1,a1,i1,a1,i6)') m, ',', n, ',', lt, ',', 2, ',', cs
    label = trim(label)
    write(*,*) 'calc_series_double: label=', label
  endif
 
  if (cs .gt. 0) nullify(cff)
  nullify(imm)
  nullify(omm)

  if (cs .gt. 0) allocate(cff(cs))
  m2 = m**2
  allocate(imm(m2),omm(m2))
  
  if (cs .gt. 0) cff = 1.0
  call random_number(imm)
  omm = 1.0
  
  if (lt .eq. LOOP_TYPE_RECURSIVE) then

    call papi_mpi_reset(1)
    do i=1,m2
      do k=1,n
        omm(i) = 1.0 + omm(i)*imm(i)
      enddo   
    enddo
    stat = papi_mpi_record(id,1,1,0)
    if (stat .ne. 0) write(*,*) rk, ': papi_mpi_record: error=', stat
    
  else
    
    ! if (lt .eq. LOOP_TYPE_FLAT) then
    call papi_mpi_reset(1)
    do i=1,m2
      do k=1,n
        omm(i) = omm(i) + imm(i)**k
      enddo
    enddo
    stat = papi_mpi_record(id,1,1,0)
    if (stat .ne. 0) write(*,*) rk, ': papi_mpi_record: error=', stat
    
  endif

  deallocate(omm,imm)
  if (cs .gt. 0) deallocate(cff)
end subroutine calc_series_double

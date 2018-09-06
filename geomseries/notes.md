The `geomseries` code was originally intended to support three types of loop (flat, inline and recursive)<br>
for iterating over the terms in a geometric series, as discussed in [Kwack et al. 2018](https://bluewaters.ncsa.illinois.edu/liferay-content/document-library/content/BWsymposium_2018_CrayPAT_based_Roofline_Analysis_v02.pdf).

The flat and recursive loop implementations are straightforward to implement, although, the former<br>
involves exponentiation whereas the latter does not. This means the number of FLOPs executed per loop<br>
depends on its type: for recursive it is `2n-1` where `n` is the number of terms in the series<br>
(i.e., the number of loop iterations), and for the flat loop, the FLOP count is instead `n*(1+n)/2`<br>
as a result of the exponentiaton.

The so called inline loop is identical to the flat one except the iterations are unrolled.<br>
Previously the `!DIR$ INLINE` compiler directive was placed in the source code just before the loop<br>
in order to indicate that unrolling was required.

However, that directive, athough accepted by the Cray, Intel and GNU compilers, is not known to work for loops<br>
and so should be replaced by `!DIR$ UNROLL n`. Unfortunately, it is now necessary to know the number of iterations<br>
at compile time, which means the geometric series tests can only be run for a specific order rather than over<br>
a range of orders from 1 to 29 as in Kwack et al. 2018. Furthermore, the unroll directive is ignored by the `gfortran`
compiler: this is a problem that can only be solved by rewriting the `geomseries` code in `C` and making use of the<br>
`#pragma GCC unroll n` directive, retaining the `!DIR$ UNROLL n` directive for the Cray and Intel compilers.

All this means that the inline loop will have to be withdrawn from the `Fortran` version of `geomseries`.

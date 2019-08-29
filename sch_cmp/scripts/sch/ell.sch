\ 椭圆型方程算法文件 ell.sch
\ 方程：LU=F
\ 空间离散后矩阵形式为：
\           [S][U]=[F]
\ ---------------------------------------------------
DEFI
STIF s
LOAD f
TYPE e
MDTY l
INIT 0

EQUATION
\............ 线性方程组左端项(分布矩阵) .............../
MATRIX = [s]
\................. 线性方程组右端项 ..................../
FORC = [f]

SOLUTION u
VECT u
$cc // 存储求解的u
WRITE(s,unod) u

END

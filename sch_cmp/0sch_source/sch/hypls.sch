\ 计算双曲型方程的最小二乘法hypls.sch(含耦合系数)
\ 空间离散后矩阵形式为：
\           [M][V]+[S][U]=[F]
\ 其中 V=dU/dt，取 Δt 为时间步长，对时间进行向后差分得到
\           [M]([U]-[ˉU])/Δt+[S][U]=[F]
\ 其中 ˉU 表示 U 的前一时刻值U(t-Δt)，整理后得到
\           ([M]+[S]*Δt)[U]=[M]*ˉU+[F]*Δt
\ ---------------------------------------------------
DEFI
STIF s
LOAD f
TYPE p
MDTY l
INIT 1

COEF u

EQUATION
VECT u
READ(s,unod) u
\..... 线性方程组左端项(分布矩阵S=[M]+[S]*Δt,FDE文件中给出) ........./
MATRIX = [s]
\.... 线性方程组右端项,其中f=[M]*ˉU+[F]*Δt,在FDE文件中给出....../
FORC=[f]

SOLUTION u
VECT u
$cc // 存储求解的u
WRITE(s,unod) u

END

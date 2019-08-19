\ 增量形式显式算法文件exp.sch
\ 空间离散后矩阵形式为：
\           [M][V]+[S][U]=[F]
\ 其中 V=dU/dt，取 Δt 为时间步长，对时间进行向后差分得到
\           [M]([U]-[ˉU])/Δt+[S][ˉU]=[F]
\ 其中 ˉU 表示 U 的前一时刻值U(t-Δt)，整理后得到
\           ([M])[ΔU]=([F]-[S][ˉU])*Δt
\ ---------------------------------------------------
DEFI
STIF s
MASS m
LOAD f
TYPE e
MDTY l

EQUATION
\............ 线性方程组左端项(集中矩阵) .............../
L,MASS = [m]
\.... 线性方程组右端项,其中f=([F]-[S][ˉU])*Δt,在FDE文件中给出....../
FORC = [f]

SOLUTION w
VECT w,u
$cc // 读取上一时间步全量值u
READ(s,unod) u
$cc // 由上一时间步全量值u及本时间步增量值w，得到本时间步的全量值u
[u] = [u]+[w]
$cc // 存储本时间步全量值u
WRITE(o,unod) u

@NBDE
 ntype = nbdetype;

END

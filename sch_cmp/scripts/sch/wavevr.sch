\ 双曲型方程算法文件 wavevr.sch（先求速度再求位移，瑞利阻尼）：
\ 基于先求速度再求位移瑞利阻尼双曲线算法wavev:
\     ([M]+[C]*Δt+[S]*Δt*Δt)[V] = [F]*Δt+[M][ˉV]-[S][ˉU]*Δt
\ 定义 [C] = b1[M]+b2[S] 带入上式并整理得到
\   ([M]*(1+b1*Δt)+[S]*(Δt+b2)*Δt)[V] = [F]*Δt+[M][ˉV]-[S][ˉU]*Δt
\ ---------------------------------------------------------------
DEFI
STIF s
MASS m
DAMP c
LOAD f
TYPE w
MDTY l
INIT 2

EQUATION
VECT u1,v1
\.......... 读取解空间中的 u,v 作为上一时刻的位移和速度 .........../
READ(s,unod) u1,v1
\................... 线性方程组左端项(分布矩阵) .................../
MATRIX = [s]*(b2+dt)*dt+[m]*(1+b1*dt)
\....................... 线性方程组右端项 ........................./
FORC = [f]*dt+[m*v1]-[s*u1]*dt

SOLUTION v
VECT v,u1,v1
$cc // 读取上一时刻位移和速度 u1 v1
READ(s,unod) u1,v1
$cc // 通过 u1 = u1+v*Δt 计算当前位移
[u1] = [u1]+[v]*dt
$cc // 存储求解的当前时刻位移和速度 u1 v
WRITE(o,unod) u1,v

@BEGIN
 double b1,b2;
        b1 = dampalfa;
        b2 = dampbeta; //瑞利阻尼系数

END

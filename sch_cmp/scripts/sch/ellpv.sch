DEFI
STIF s
LOAD f
TYPE e
MDTY l
INIT 1

COEF u1

EQUATION
VECT u1,du
\ === 从unod中读取u1(上一迭代步的位移结果)，du(上一迭代步的位移增量) ===
READ(s,unod) u1,du
\ ================================================================
\ =    L(U(n+1) - U(n)) + F = 0                                  =
\ =--------------------------------------------------------------=
\ =    -(L(U(n+1) - U(n));u) = (F;u)                             =
\ =    S(U(n))*U(n+1) = F + S(U(n))*U(n)                         =
\ ================================================================
\ ==== 按照上面的形式，MATRIX为方程组左端项FORC为方程组右端项 ===
MATRIX = [s]
\ === FORC为方程组右端项 ===
FORC=[f]+[s*u1]

SOLUTION u
VECT u1,u,ue,du,gu
\ === 从unod中读取u1(上一迭代步的位移结果)，du(上一迭代步的位移增量) ===
READ(s,unod) u1,du
$CC // === ue: 当前步位移结果与上一迭代步的差值，即当前迭代步增量 ===
[ue]=[u]-[u1]
$CC aa = 0.0;
$CC ab = 0.0;
$CC bb = 0.0;
$CC // ===============================================================
$CC // =    对所有节点(NOD)和自由度(DOF)循环                         =
$CC // =-------------------------------------------------------------=
$CC // =    aa：当前迭代步增量ue的模的平方的和                       =
$CC // =    ab：当前迭代步增量ue与上一迭代步增量du内积的和           =
$CC // =    bb：上一迭代步增量du的模的平方的和                       =
$CC // ===============================================================
%NOD
%DOF
  aa = aa+[ue]*[ue];
  ab = ab+[ue]*[du];
  bb = bb+[du]*[du];
%DOF
%NOD
#sum double aa ab bb
$CC err = aa;                         // err 为当前迭代步误差
$CC if (itn==1) cc = 1.0;             // 迭代第一步取松弛因子为 1
$CC if (itn>1) {                      // 下面每一迭代步都调整松弛因子
$CC rab = sqrt(aa)*sqrt(bb);          // 当前增量UE与上一增量DU模乘积
$CC if (ab>0.5*rab) cc = cc*2.0;      // 若UE与DU夹角小于60°，松弛因子增倍
$CC if (ab>0.8*rab) cc = cc*2.0;      // 若UE与DU夹角小于37°，松弛因子再次增倍
$CC if (ab<0.0) cc = cc*0.5;          // 若UE与DU夹角大于90°，松弛因子减半
$CC if (ab<-0.40*rab) cc = cc*0.5;    // 若UE与DU夹角大于114°，松弛因子再次减半
$CC if (ab<-0.80*rab) cc = cc*0.5;    // 若UE与DU夹角大于143°，松弛因子再次减半
$CC }                                 //
$CC if (cc>1.0) cc = 1.0;             // 控制松弛因子不能大于1
$CC ul = 0.0;
%NOD
%DOF
$CC // === 根据松弛因子(cc)更新迭代步增量 ===
  [ue] = [ue]*cc;
$CC // === 计算本迭代步松弛后的结果u1 ===
  [u1] = [u1]+[ue];
$CC // === 计算本迭代步松弛后结果u的模平方的和ul ===
   ul = ul + [u1]*[u1];
%DOF
%NOD
#sum double ul
$CC // ===================================================================
$CC // =    收敛判断                                                     =
$CC // =    err足够小，或者err相对于计算结果的模的平方的和足够小         =
$CC // =    或者迭代步数超出最大迭代步，都会被判断为收敛，停止迭代       =
$CC // =    end为迭代收敛标志变量。                                      =
$CC // ===================================================================
$CC if (err<tolerance || err<tolerance*ul || itn>itnmax) end = 1;
#min int end
$CC if (end==1){                      // 如果收敛
$CC for (i=1; i<=knode; ++i)
$CC for (j=1; j<=dim; ++j)
$CC   ^coor[j][i] += ^vectu1[j][i];
$CC if (time_now<1.5*dt) {                // 如果时间步为第一时间步
$CC // === 总位移取初值：0.0 === 
[gu]=0.0
$CC // === 将总位移gu写入unodg中 ===
WRITE(n,unodg) gu
$CC } else {
$CC // === 读取 ===
READ(s,unodg) gu
$CC }
$CC // === 计算当前载荷步总位移 ===
[gu]=[gu]+[u1]
$CC // === 将当前载荷步总位移存储到unodg中 ===
WRITE(o,unodg) gu
$CC itn=1;                            // 将迭代步置为1
$CC // === 将迭代步位移增量置为0 ===
[du] = 0.0;
$CC } else {                          // 若不收敛
$CC // === 更新当前迭代步增量 ===
[du] = [ue]
$CC itn=itn+1;                        // 更新迭代步
$CC }
$CC // === 将本迭代步结果存储到指针数组unod中 === 
WRITE(o,unod) u1,du

@SUBET
 double aa,bb,ab,rab,err,ul;
 static double cc;

@head
 double *unodg;

END

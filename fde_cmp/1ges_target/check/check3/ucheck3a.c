/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = ucheck3a.c
Version:2.2
Time of release:2019-06-18 17:21:30
All rights reserved by ECTEC Corporation, and person or
organization using Original software to generated these code,anyone
else must get written permission from ECTEC Corporation to
copy a part or whole of this code.
The Code GenID is:
22565914_000906E9071008007FFAFBFFBFEBFBFF_005056C00008
Copyright is protected from:2017-2030
**************************************************************/
/*
����������
1�����������䣬��ʩ����ǿ���������ı߽��ϵ����ɶ����䵽�����������Ľ������У�
2�����Ƿ��������⣬��Խ���е����������ǰ�������Ľ����
3���ж��Ƿ��������������������ʶ��end��1��
*/
#include "felac.h"
double *unodg;
/* subroutine */
void ucheck3a(coor0,dof,nodvar,u,f)
int dof,*nodvar;
double *u,*f;
struct coordinates coor0;
{
    /*
    �������ͣ�
     dim��   ����ά��
     knode�� �ڵ�����
     kvar:   �����ɶ�����
     dof��   �ó�ÿ���ڵ�����ɶ�����
    *coor��  �ڵ�����ռ䣻
    *nodvar���ó��ڵ����ɶȶ�Ӧ�Ĺ�������߷��̺ţ�
    */
    int i,j,n,nrw,kvar;
    int dim,knode;
    double *coor;
    double *vectu1,*vectu,*vectue,*vectdu;
    double *vectgu;
    double aa,bb,ab,rab,err,ul;
    static double cc;
    dim   = coor0.dim;
    knode = coor0.knode;
    coor  = coor0.coor;
    kvar  = knode*dof;
    vectu1 = (double *) calloc(kvar,sizeof(double));
    vectu = (double *) calloc(kvar,sizeof(double));
    vectue = (double *) calloc(kvar,sizeof(double));
    vectdu = (double *) calloc(kvar,sizeof(double));
    vectgu = (double *) calloc(kvar,sizeof(double));
    /*  ���������䣬��ʩ����ǿ���������ı߽��ϵ����ɶ����䵽�����������Ľ������У� */
    for (i=1; i<=dof; ++i)
        for (j=1; j<=knode; ++j)
        {
            vectu[(i-1)*(knode)+j-1] = u[(i-1)*(knode)+j-1];
            n = nodvar[(i-1)*(knode)+j-1];
            if (n>0)
                vectu[(i-1)*(knode)+j-1] = f[n];
        }
//mpi_sere(knode,dof,vectu);
    nrw = 0*dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            vectu1[(j-1)*(knode)+i-1] = unoda[(nrw+j-1)*knode+i-1];
    nrw += dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            vectdu[(j-1)*(knode)+i-1] = unoda[(nrw+j-1)*knode+i-1];
    nrw += dof;
// === ue: ��ǰ��λ�ƽ������һ�������Ĳ�ֵ������ǰ���������� ===
    for (inod=1; inod<=knode; ++inod)
        for (idof=1; idof<=dof; ++idof)
            vectue[(idof-1)*(knode)+inod-1]=vectu[(idof-1)*(knode)+inod-1]-vectu1[(idof-1)*(knode)+inod-1];
    aa = 0.0;
    ab = 0.0;
    bb = 0.0;
// ===============================================================
// =    �����нڵ�(nod)�����ɶ�(dof)ѭ��                         =
// =-------------------------------------------------------------=
// =    aa����ǰ����������ue��ģ��ƽ���ĺ�                       =
// =    ab����ǰ����������ue����һ����������du�ڻ��ĺ�           =
// =    bb����һ����������du��ģ��ƽ���ĺ�                       =
// ===============================================================
    for (inod=1; inod<=knode; ++inod)
    {
        for (idof=1; idof<=dof; ++idof)
        {
            aa = aa+vectue[(idof-1)*(knode)+inod-1]*vectue[(idof-1)*(knode)+inod-1];
            ab = ab+vectue[(idof-1)*(knode)+inod-1]*vectdu[(idof-1)*(knode)+inod-1];
            bb = bb+vectdu[(idof-1)*(knode)+inod-1]*vectdu[(idof-1)*(knode)+inod-1];
        }
    }
//mpi_sum_dou(&aa);
//mpi_sum_dou(&ab);
//mpi_sum_dou(&bb);
    err = aa;                         // err Ϊ��ǰ���������
    if (itn==1) cc = 1.0;             // ������һ��ȡ�ɳ�����Ϊ 1
    if (itn>1)                        // ����ÿһ�������������ɳ�����
    {
        rab = sqrt(aa)*sqrt(bb);          // ��ǰ����ue����һ����duģ�˻�
        if (ab>0.5*rab) cc = cc*2.0;      // ��ue��du�н�С��60�㣬�ɳ���������
        if (ab>0.8*rab) cc = cc*2.0;      // ��ue��du�н�С��37�㣬�ɳ������ٴ�����
        if (ab<0.0) cc = cc*0.5;          // ��ue��du�нǴ���90�㣬�ɳ����Ӽ���
        if (ab<-0.40*rab) cc = cc*0.5;    // ��ue��du�нǴ���114�㣬�ɳ������ٴμ���
        if (ab<-0.80*rab) cc = cc*0.5;    // ��ue��du�нǴ���143�㣬�ɳ������ٴμ���
    }                                 //
    if (cc>1.0) cc = 1.0;             // �����ɳ����Ӳ��ܴ���1
    ul = 0.0;
    for (inod=1; inod<=knode; ++inod)
    {
        for (idof=1; idof<=dof; ++idof)
        {
// === �����ɳ�����(cc)���µ��������� ===
            vectue[(idof-1)*(knode)+inod-1] = vectue[(idof-1)*(knode)+inod-1]*cc;
// === ���㱾�������ɳں�Ľ��u1 ===
            vectu1[(idof-1)*(knode)+inod-1] = vectu1[(idof-1)*(knode)+inod-1]+vectue[(idof-1)*(knode)+inod-1];
// === ���㱾�������ɳں���u��ģƽ���ĺ�ul ===
            ul = ul + vectu1[(idof-1)*(knode)+inod-1]*vectu1[(idof-1)*(knode)+inod-1];
        }
    }
//mpi_sum_dou(&ul);
// ===================================================================
// =    �����ж�                                                     =
// =    err�㹻С������err����ڼ�������ģ��ƽ���ĺ��㹻С         =
// =    ���ߵ������������������������ᱻ�ж�Ϊ������ֹͣ����       =
// =    endΪ����������־������                                      =
// ===================================================================
    if (err<tolerance || err<tolerance*ul || itn>itnmax) end = 1;
//mpi_min_int(&end);
    if (end==1)                       // �������
    {
        for (i=1; i<=knode; ++i)
            for (j=1; j<=dim; ++j)
                coor[(j-1)*(knode)+i-1] += vectu1[(j-1)*(knode)+i-1];
        if (time_now<1.5*dt)                  // ���ʱ�䲽Ϊ��һʱ�䲽
        {
// === ��λ��ȡ��ֵ��0.0 ===
            for (inod=1; inod<=knode; ++inod)
                for (idof=1; idof<=dof; ++idof)
                    vectgu[(idof-1)*(knode)+inod-1]=0.0;
// === ����λ��guд��unodg�� ===
            n=0;
            n=n+dof;
            unodg = (double *) calloc(n*knode,sizeof(double));
            nrw = 0*dof;
            for (j=1; j<=dof; ++j)
                for (i=1; i<=knode; ++i)
                    unodg[(nrw+j-1)*knode+i-1] = vectgu[(j-1)*(knode)+i-1];
            nrw += dof;
        }
        else
        {
// === ��ȡ ===
            nrw = 0*dof;
            for (j=1; j<=dof; ++j)
                for (i=1; i<=knode; ++i)
                    vectgu[(j-1)*(knode)+i-1] = unodg[(nrw+j-1)*knode+i-1];
            nrw += dof;
        }
// === ���㵱ǰ�غɲ���λ�� ===
        for (inod=1; inod<=knode; ++inod)
            for (idof=1; idof<=dof; ++idof)
                vectgu[(idof-1)*(knode)+inod-1]=vectgu[(idof-1)*(knode)+inod-1]+vectu1[(idof-1)*(knode)+inod-1];
// === ����ǰ�غɲ���λ�ƴ洢��unodg�� ===
        n=0;
        n=n+dof;
        nrw = 0*dof;
        for (j=1; j<=dof; ++j)
            for (i=1; i<=knode; ++i)
                unodg[(nrw+j-1)*knode+i-1] = vectgu[(j-1)*(knode)+i-1];
        nrw += dof;
        itn=1;                            // ����������Ϊ1
// === ��������λ��������Ϊ0 ===
        for (inod=1; inod<=knode; ++inod)
            for (idof=1; idof<=dof; ++idof)
                vectdu[(idof-1)*(knode)+inod-1] = 0.0;
    }
    else                              // ��������
    {
// === ���µ�ǰ���������� ===
        for (inod=1; inod<=knode; ++inod)
            for (idof=1; idof<=dof; ++idof)
                vectdu[(idof-1)*(knode)+inod-1] = vectue[(idof-1)*(knode)+inod-1];
        itn=itn+1;                        // ���µ�����
    }
// === ��������������洢��ָ������unod�� ===
    n=0;
    n=n+dof;
    n=n+dof;
    nrw = 0*dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            unoda[(nrw+j-1)*knode+i-1] = vectu1[(j-1)*(knode)+i-1];
    nrw += dof;
    for (j=1; j<=dof; ++j)
        for (i=1; i<=knode; ++i)
            unoda[(nrw+j-1)*knode+i-1] = vectdu[(j-1)*(knode)+i-1];
    nrw += dof;
    free(vectu1);
    free(vectu);
    free(vectue);
    free(vectdu);
    free(vectgu);
    return;
}

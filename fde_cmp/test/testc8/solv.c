/**************************************************************
ECTEC Finite Element Language And its Compiler(FELAC)Software
File name = solv.c
Version:2.2
Time of release:2019-08-30 13:14:16
All rights reserved by ECTEC Corporation, and person or
organization using Original software to generated these code,anyone
else must get written permission from ECTEC Corporation to
copy a part or whole of this code.
The Code GenID is:
22565914_000906E9061008007FFAFBFFBFEBFBFF_005056C00001
Copyright is protected from:2017-2030
**************************************************************/
#include "felac.h"
void solvsuperlu(struct matrice,double *,struct solveroptions);
void solvaztec(struct matrice,double *,struct solveroptions);
void solv(matrix,f)
double *f;
struct matrice matrix;
{
    if(solvtag>12)
        solvsuperlu(matrix,f,solvoptions);
    else
        solvaztec(matrix,f,solvoptions);
}
void setsolver(int solv,int solvp)
{
    solvoptions.solver = solv;
    solvoptions.az_tol = 1.0e-8;
    solvoptions.az_max_iter=1000;
    if((6<=solvp&&solvp<=11)||(solvp==17))
    {
        solvoptions.az_precond = az_dom_decomp;
        solvoptions.az_subdomain_solve = solvp;
    }
    else
    {
        solvoptions.az_precond = solvp;
        solvoptions.az_subdomain_solve = az_ilut;
    }
    if(solvp==az_sym_gs || solvp==az_jacobi)
        solvoptions.az_poly_ord = 1;
    else
        solvoptions.az_poly_ord = 3;
    solvoptions.az_scaling = az_none;

    solvoptions.slu_Fact = dofact;
    solvoptions.slu_Equil = yes;
    if(solvp<4) solvoptions.slu_ColPerm = solvp;
    else        solvoptions.slu_ColPerm = natural;
    solvoptions.slu_Trans = notrans;
    solvoptions.slu_IterRefine = norefine;
    solvoptions.slu_DiagPivotThresh = 1.0;
    solvoptions.slu_SymmetricMode = no;
    solvoptions.slu_PivotGrowth = no;
    solvoptions.slu_ConditionNumber = no;
    solvoptions.slu_PrintStat = yes;
}
int print(const char *__format, ...)
{
    register int __retval;
    va_list __local_argv;
    va_start( __local_argv, __format );
    __retval = vprintf( __format, __local_argv );
    va_end( __local_argv );
    return __retval;
}
void adda(na,a,numcol,nd,lm,estif,neq,maxa)
int *na,*numcol,*lm,nd,neq,maxa;
double *a,*estif;
{
    int i,ii,j,jj,k,n0,n1;
    if(solvtag>12)
    {
        for (i=1; i<=nd; ++i)
        {
            /*300*/
            ii = lm[i];
            if (ii<0) goto l300;
            n0 = numcol[ii-1]+1;
            n1 = numcol[ii];
            for (j=1; j<=nd; ++j)
            {
                /*280*/
                jj = lm[j];
                if (jj<0) goto l500;
                for (k=n0; k<=n1; ++k)
                {
                    if (na[k]==jj)  a[k] = a[k] + estif[(i-1)*nd+j-1];
                }
l500:
                continue;
            } /*280*/
l300:
            continue;
        } /*300*/
    }
    else
    {
        for (i=1; i<=nd; ++i)
        {
            /*300*/
            ii = lm[i];
            if (ii<0) goto l400;
            n0 = numcol[ii-1]+1;
            n1 = numcol[ii];
            for (j=1; j<=nd; ++j)
            {
                /*280*/
                jj = lm[j];
                for (k=n0; k<=n1; ++k)
                {
                    if (na[k]==jj)  a[k] = a[k] + estif[(j-1)*nd+i-1];
                }
            } /*280*/
l400:
            continue;
        } /*300*/
    }
    return;
}

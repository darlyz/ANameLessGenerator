#include <math.h>
void mstress6(int,double *,double *);
void getcf(double,double *,double *);
/* subroutine sub1 */
double getyield(x,u,d,shear,ddf,kq,yield,ialpha)
double (*yield)();
int kq,ialpha;
double x[5],u[8],d[9],shear,ddf[7];
{
    int i,j,k;
    double v[8],h[8],df[8];
    double  f1,f2,c,am,a;
    for (k=1; k<=7; ++k)
    {
        v[k]=u[k];
        h[k] = 1.0;
    }
    if (kq==1)  h[7]=1.0e-3;
    if (kq==2)  h[7]=1.0e-6;
    if (kq==3)  h[7]=1.0e-6;
    for (k=1; k<=7; ++k)
    {
        v[k]=u[k]+h[k];
        f2=yield(x,v);
        v[k]=u[k]-h[k];
        f1=yield(x,v);
        df[k]=(f2-f1)/h[k]*0.5;
        v[k]=u[k];
    }
    for (i=4; i<=6; ++i)
    {
        ddf[i]=shear*df[i];
    }
    for (i=1; i<=3; ++i)
    {
        c=0.0;
        for (j=1; j<=3; ++j)
        {
            c=c+d[(i-1)*3+j-1]*df[j];
        }
        ddf[i]=c;
    }
    a=0.0;
    am=0.0;
    for (i=1; i<=6; ++i)
    {
        a=a+df[i]*ddf[i];
        if (kq==1)  am=am+u[i]*df[i];
        if (kq==2  && i<=3)  am=am+df[i];
        if (kq==3)  am=am+df[i]*df[i];
    }
    if (kq==3)  am=sqrt(am);
    am=-am*df[7];
    if (ialpha==0)
    {
        a=a+am;
    }
    else
    {
        if (am>=-a)
        {
            a=a+am+a*3.5;
        }
        else
        {
            a=a+am-a*2.0;
        }
    }
    return a;
}

/* subroutine sub2 */
double prager(x,u)
double x[5],u[8];
{
    double s[7];
    double tgo,q0,c,pv,d,sinf,cosf,sj,alpha,ck,prager;
    tgo=x[1];
    q0=x[4];
    c=x[2]+q0*u[7];
    pv=x[3];
    d=(u[1]+u[2]+u[3])/3.0;
    s[1]=u[1]-d;
    s[2]=u[2]-d;
    s[3]=u[3]-d;
    s[4]=u[4];
    s[5]=u[5];
    s[6]=u[6];
    sj=(s[1]*s[1]+s[2]*s[2]+s[3]*s[3])/2.0+s[4]*s[4];
    sj=sj+s[5]*s[5]+s[6]*s[6];
    cosf=1.0/sqrt(1.0+tgo*tgo);
    sinf=sqrt(1.0-cosf*cosf);
    alpha=2.0*sinf/(1.732*(3.0+sinf));
    ck=6.0*c*cosf/(1.732*(3.0+sinf));
    prager=sqrt(sj)+alpha*d*3.0-ck;
    return prager;
}

/* subroutine sub3 */
double emises(x,u)
double x[5],u[8];
{
    double s[7];
    double tgo,q0,pv,c,d,sj,emises;
    tgo=x[1];
    q0=x[4];
    c=x[2]+q0*u[7];
    pv=x[3];
    d=(u[1]+u[2]+u[3])/3.0;
    s[1]=u[1]-d;
    s[2]=u[2]-d;
    s[3]=u[3]-d;
    s[4]=u[4];
    s[5]=u[5];
    s[6]=u[6];
    sj=(s[1]*s[1]+s[2]*s[2]+s[3]*s[3])/2.0+s[4]*s[4];
    sj=sj+s[5]*s[5]+s[6]*s[6];
    emises=sqrt(sj)-c;
    return emises;
}

/* subroutine sub4 */
double emohrc(x,u)
double x[5],u[8];
{
    double s[7];
    double tgo,q0,cosf,c,emohrc;
    mstress6(6,u,s);
    tgo=x[1];
    q0=x[4];
    c=x[2]+q0*u[7];
    cosf=1.0/sqrt(1.0+tgo*tgo);
    emohrc=s[4]-s[6]-2.0*c*cosf;
    emohrc=emohrc+(s[4]+s[6])*(sqrt(1.0-cosf*cosf));
    return emohrc;
}

/* subroutine sub5 */
double soft(x,u)
double x[5],u[8];
{
    double s[7];
    double epv,sinf,a,b,c,fai,soft;
    mstress6(6,u,s);
    epv=fabs(u[7]);
    getcf(epv,&c,&fai);
    sinf=sin(fai);
    a=(1.0+sinf)/(1.0-sinf);
    b=2.0*c*sqrt(1.0+sinf/(1.0-sinf));
    soft=s[4]-a*s[6]-b;
    return soft;
}

/* subroutine sub6 */
void getcf(s1,c,fai)
double s1,*c,*fai;
{
    int n,m,i;
    double xc[11],yc[11];
    double s,dy,y;
    xc[1]=0.000;
    yc[1]=2.42e7;
    xc[2]=0.001;
    yc[2]=1.9e7;
    xc[3]=0.002;
    yc[3]=1.5e7;
    xc[4]=0.003;
    yc[4]=1.1e7;
    xc[5]=0.004;
    yc[5]=8.5e6;
    xc[6]=0.005;
    yc[6]=6.0e6;
    xc[7]=0.006;
    yc[7]=4.0e6;
    xc[8]=0.007;
    yc[8]=2.0e6;
    xc[9]=0.008;
    yc[9]=1.0e6;
    xc[10]=0.009;
    yc[10]=5.0e5;
    n=10;
    m=0;
    s=fabs(s1);
    for (i=1; i<=n; ++i)
    {
        if (s<xc[i])
        {
            m=i;
        }
    }
    if (m==1)
    {
        dy=(yc[2]-yc[1])/(xc[2]-xc[1]);
        y=yc[1];
    }
    else
    {
        if (m==0)
        {
            dy=(yc[n]-yc[n-1])/(xc[n]-xc[n-1]);
            y=yc[n];
        }
        else
        {
            dy=(yc[m]-yc[m-1])/(xc[m]-xc[m-1]);
            y=yc[m-1]+dy*(s-xc[m-1]);
        }
    }
    *c=y;
    *fai=52.0;
    return;
}

#include <math.h>
void getcf(double,double *,double *);
/* subroutine sub1 */
double getyield(x,u,d,shear,ddf,kq,yield,ialpha)
double (*yield) ();
int kq,ialpha;
double x[5],u[5],d[4],shear,ddf[4];
{
    int i,j,k;
    double v[5],h[5],df[5];
    double f1,f2,c,am,a;
//      external yield
    for (k=1; k<=4; ++k)
    {
        v[k]=u[k];
    }
    for (k=1; k<=3; ++k)
    {
        h[k]=1.0;
    }
    if (kq==1)  h[4]=1.0e-3;
    if (kq==2)  h[4]=1.0e-6;
    if (kq==3)  h[4]=1.0e-6;
    for (k=1; k<=4; ++k)
    {
        v[k]=u[k]+h[k];
        f2=yield(x,v);
        v[k]=u[k]-h[k];
        f1=yield(x,v);
        df[k]=(f2-f1)/h[k]*0.5;
        v[k]=u[k];
    }
    ddf[3]=shear*df[3];
    for (i=1; i<=2; ++i)
    {
        c=0.0;
        for (j=1; j<=2; ++j)
        {
            c=c+d[(i-1)*2+j-1]*df[j];
        }
        ddf[i]=c;
    }
    a=0.0;
    am=0.0;
    for (i=1; i<=3; ++i)
    {
        a=a+df[i]*ddf[i];
        if (kq==1)  am=am+u[i]*df[i];
        if (kq==2  && i<=2)  am=am+df[i];
        if (kq==3)  am=am+df[i]*df[i];
    }
    if (kq==3)  am=sqrt(am);
    am=-am*df[4];
    if (ialpha==0)
    {
        a=a+am;
    }
    else
    {
        a=a+am+a*3.5;
    }
    return a;
}
/* subroutine sub2 */
double prager(x,u)
double x[5],u[5];
{
    double s[4];
    double tgo,q0,c,pv,d,uk,sj,ck,alpha,prager;
    tgo=x[1];
    q0=x[4];
    c=x[2]+q0*u[4];
    pv=x[3];
    d=(u[1]+u[2])*(1.0+pv)/3.0;
    s[1]=u[1]-d;
    s[2]=u[2]-d;
    s[3]=u[3];
    uk=(u[1]+u[2])*pv-d;
    sj=(s[1]*s[1]+s[2]*s[2]+uk*uk)/2.0+s[3]*s[3];
    alpha=tgo/sqrt(9.0+12.0*tgo*tgo);
    ck=3.0*c/sqrt(9.0+12.0*tgo*tgo);
    prager=sqrt(sj)+alpha*d*3.0-ck;
    return prager;
}
/* subroutine sub3 */
double emises(x,u)
double x[5],u[5];
{
    double s[4];
    double tgo,q0,c,pv,d,uk,sj,emises;
    tgo=x[1];
    q0=x[4];
    c=x[2]+q0*u[4];
    pv=x[3];
    d=(u[1]+u[2])*(1+pv)/3.0;
    s[1]=u[1]-d;
    s[2]=u[2]-d;
    s[3]=u[3];
    uk=(u[1]+u[2])*pv-d;
    sj=(s[1]*s[1]+s[2]*s[2]+uk*uk)/2.0+s[3]*s[3];
    emises=sqrt(sj)-c;
    return emises;
}
/* subroutine sub4 */
double emohrc(x,u)
double x[5],u[5];
{
    double s[4];
    double pv,cb,cc,cd,ss,cosf,tgo,q0,c,emohrc;
    pv=x[3];
    s[1]=(u[1]+u[2])*pv;
    cb=-u[1]-u[2];
    cc=u[1]*u[2]-u[3]*u[3];
    cd=cb*cb-4.0*cc;
    if (cd<0.0)  cd=0.0;
    s[2]=((-cb)+sqrt(cd))/2.0;
    s[3]=((-cb)-sqrt(cd))/2.0;
    if (s[1]<s[2])
    {
        ss=s[2];
        s[2]=s[1];
        s[1]=ss;
    }
    if (s[1]<s[3])
    {
        ss=s[3];
        s[3]=s[1];
        s[1]=ss;
    }
    if (s[2]<s[3])
    {
        ss=s[2];
        s[2]=s[3];
        s[3]=ss;
    }
    tgo=x[1];
    q0=x[4];
    c=x[2]+q0*u[4];
    cosf=1.0/sqrt(1.0+tgo*tgo);
    emohrc=s[1]-s[3]-2.0*c*cosf;
    emohrc=emohrc+(s[1]+s[3])*(sqrt(1.0-cosf*cosf));
    return emohrc;
}
/* subroutine sub5 */
double soft(x,u)
double x[5],u[5];
{
    double s[4];
    double pv,cb,cc,cd,ss,epv,sinf,a,b,c,fai,soft;
    pv=x[3];
    s[1]=(u[1]+u[2])*pv;
    cb=-u[1]-u[2];
    cc=u[1]*u[2]-u[3]*u[3];
    cd=cb*cb-4.0*cc;
    if (cd<0.0)  cd=0.0;
    s[2]=((-cb)+sqrt(cd))/2.0;
    s[3]=((-cb)-sqrt(cd))/2.0;
    if (s[1]<s[2])
    {
        ss=s[2];
        s[2]=s[1];
        s[1]=ss;
    }
    if (s[1]<s[3])
    {
        ss=s[3];
        s[3]=s[1];
        s[1]=ss;
    }
    if (s[2]<s[3])
    {
        ss=s[2];
        s[2]=s[3];
        s[3]=ss;
    }
    epv=fabs(u[4]);
    getcf(epv,&c,&fai);
    sinf=sin(fai);
    a=(1.0+sinf)/(1.0-sinf);
    b=2.0*c*sqrt(1.0+sinf/(1.0-sinf));
    soft=s[1]-a*s[3]-b;
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

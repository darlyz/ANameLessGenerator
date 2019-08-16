void samar(double,double *,double,int);

void nsxyt(coorr,coefr,prmt,eqn,emass,edamp,eload,num)
double coefr[6],coorr[6],*prmt,eqn[81];
double emass[10],edamp[10],eload[10];
int num;
{
    int i,j,ncoor,nnode,ncoef,ndisp,ndof;
    double rou,emu,fx,fy,cccc;
    double un[4],vn[4];
    double x[4],y[4];
    double r[4],xm[4],ym[4],um[4],vm[4],flux[4],fluxm[4];
    double xc,yc,uc,vc;
    int mode;
    mode = 1;
    ncoor = 2;
    nnode = 3;
    ncoef = 2;
    ndisp = 3;
    ndof = 9;
    for (i=1; i<=ndof; ++i)
    {
        eload[i]=0.0;
        for (j=1; j<=ndof; ++j)
        {
            eqn[(i-1)*9+j-1]=0.0;
        }
    }
    rou=prmt[1];
    emu=prmt[2];
    fx=prmt[3];
    fy=prmt[4];
    for (j=1; j<=nnode; ++j)
    {
        un[j]=coefr[(1-1)*3+j-1];
        vn[j]=coefr[(2-1)*3+j-1];
        x[j]=coorr[(1-1)*3+j-1];
        y[j]=coorr[(2-1)*3+j-1];
    }
    mode = 1;
    xc=(x[1]+x[2]+x[3])/3;
    yc=(y[1]+y[2]+y[3])/3;
    uc=(un[1]+un[2]+un[3])/3;
    vc=(vn[1]+vn[2]+vn[3])/3;
    xm[3]=(x[1]+x[2])/2;
    ym[3]=(y[1]+y[2])/2;
    um[3]=(un[1]+un[2])/2;
    vm[3]=(vn[1]+vn[2])/2;
    xm[1]=(x[2]+x[3])/2;
    ym[1]=(y[2]+y[3])/2;
    um[1]=(un[2]+un[3])/2;
    vm[1]=(vn[2]+vn[3])/2;
    xm[2]=(x[3]+x[1])/2;
    ym[2]=(y[3]+y[1])/2;
    um[2]=(un[3]+un[1])/2;
    vm[2]=(vn[3]+vn[1])/2;
    flux[2]=0.5*rou*((um[2]+uc)*(yc-ym[2])-(vm[2]+vc)*(xc-xm[2]));
    fluxm[2]=rou*(um[2]*(yc-ym[2])-vm[2]*(xc-xm[2]));
    samar(fluxm[2],&r[2],emu,mode);
    flux[3]=0.5*rou*((um[3]+uc)*(yc-ym[3])-(vm[3]+vc)*(xc-xm[3]));
    fluxm[3]=rou*(um[3]*(yc-ym[3])-vm[3]*(xc-xm[3]));
    samar(fluxm[3],&r[3],emu,mode);
    flux[1]=0.5*rou*((um[1]+uc)*(yc-ym[1])-(vm[1]+vc)*(xc-xm[1]));
    fluxm[1]=rou*(um[1]*(yc-ym[1])-vm[1]*(xc-xm[1]));
    samar(fluxm[1],&r[1],emu,mode);
    eqn[(1-1)*9+1-1]=(r[3]-1.)*flux[3]+r[2]*flux[2];
    eqn[(1-1)*9+4-1]=(1.-r[3])*flux[3];
    eqn[(1-1)*9+7-1]=-(r[2]*flux[2]);
    eload[1]=0.0;
    eqn[(4-1)*9+4-1]=(r[1]-1.)*flux[1]+r[3]*flux[3];
    eqn[(4-1)*9+7-1]=(1.-r[1])*flux[1];
    eqn[(4-1)*9+1-1]=-(r[3]*flux[3]);
    eload[4]=0.0;
    eqn[(7-1)*9+7-1]=(r[2]-1.)*flux[2]+r[1]*flux[1];
    eqn[(7-1)*9+1-1]=(1.-r[2])*flux[2];
    eqn[(7-1)*9+4-1]=-(r[1]*flux[1]);
    eload[7]=0.0;
    eqn[(2-1)*9+2-1]=(r[3]-1.)*flux[3]+r[2]*flux[2];
    eqn[(2-1)*9+5-1]=(1.-r[3])*flux[3];
    eqn[(2-1)*9+8-1]=-(r[2]*flux[2]);
    eload[2]=0.0;
    eqn[(5-1)*9+5-1]=(r[1]-1.)*flux[1]+r[3]*flux[3];
    eqn[(5-1)*9+8-1]=(1.-r[1])*flux[1];
    eqn[(5-1)*9+2-1]=-(r[3]*flux[3]);
    eload[5]=0.0;
    eqn[(8-1)*9+8-1]=(r[2]-1.)*flux[2]+r[1]*flux[1];
    eqn[(8-1)*9+2-1]=(1.-r[2])*flux[2];
    eqn[(8-1)*9+5-1]=-(r[1]*flux[1]);
    eload[8]=0.0;
    for (i=2; i<=ndof; ++i)
        for (j=1; j<=i-1; ++j)
        {
            cccc = eqn[(i-1)*9+j-1];
            eqn[(i-1)*9+j-1] = eqn[(j-1)*9+i-1];
            eqn[(j-1)*9+i-1] = cccc;
        }
    return;
}


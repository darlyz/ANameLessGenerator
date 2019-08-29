void samar(double,double *,double,int);

void nsxyq(coorr,coefr,prmt,eqn,emass,edamp,eload,num)
double coefr[8],coorr[8],*prmt,eqn[144];
double emass[13],edamp[13],eload[13];
int num;
{
    int i,j,ncoor,nnode,ncoef,ndisp,ndof;
    double rou,emu,fx,fy,cccc;
    double un[5],vn[5];
    double x[5],y[5];
    double r[5],xm[5],ym[5],um[5],vm[5],flux[5],fluxm[5];
    double xc,yc,uc,vc;
    int mode;
    mode = 1;
    ncoor = 2;
    nnode = 4;
    ncoef = 2;
    ndisp = 3;
    ndof = 12;
    for (i=1; i<=ndof; ++i)
    {
        eload[i]=0.0;
        for (j=1; j<=ndof; ++j)
        {
            eqn[(i-1)*12+j-1]=0.0;
        }
    }
    rou=prmt[1];
    emu=prmt[2];
    fx=prmt[3];
    fy=prmt[4];
    for (j=1; j<=nnode; ++j)
    {
        un[j]=coefr[(1-1)*4+j-1];
        vn[j]=coefr[(2-1)*4+j-1];
        x[j]=coorr[(1-1)*4+j-1];
        y[j]=coorr[(2-1)*4+j-1];
    }
    mode = 1;
    xc=(x[1]+x[2]+x[3]+x[4])/4;
    yc=(y[1]+y[2]+y[3]+y[4])/4;
    uc=(un[1]+un[2]+un[3]+un[4])/4;
    vc=(vn[1]+vn[2]+vn[3]+vn[4])/4;
    xm[1]=(x[1]+x[2])/2;
    ym[1]=(y[1]+y[2])/2;
    um[1]=(un[1]+un[2])/2;
    vm[1]=(vn[1]+vn[2])/2;
    xm[2]=(x[2]+x[3])/2;
    ym[2]=(y[2]+y[3])/2;
    um[2]=(un[2]+un[3])/2;
    vm[2]=(vn[2]+vn[3])/2;
    xm[3]=(x[3]+x[4])/2;
    ym[3]=(y[3]+y[4])/2;
    um[3]=(un[3]+un[4])/2;
    vm[3]=(vn[3]+vn[4])/2;
    xm[4]=(x[4]+x[1])/2;
    ym[4]=(y[4]+y[1])/2;
    um[4]=(un[4]+un[1])/2;
    vm[4]=(vn[4]+vn[1])/2;
    flux[1]=0.5*rou*((um[1]+uc)*(yc-ym[1])-(vm[1]+vc)*(xc-xm[1]));
    fluxm[1]=rou*(um[1]*(yc-ym[1])-vm[1]*(xc-xm[1]));
    samar(fluxm[1],&r[1],emu,mode);
    flux[2]=0.5*rou*((um[2]+uc)*(yc-ym[2])-(vm[2]+vc)*(xc-xm[2]));
    fluxm[2]=rou*(um[2]*(yc-ym[2])-vm[2]*(xc-xm[2]));
    samar(fluxm[2],&r[2],emu,mode);
    flux[3]=0.5*rou*((um[3]+uc)*(yc-ym[3])-(vm[3]+vc)*(xc-xm[3]));
    fluxm[3]=rou*(um[3]*(yc-ym[3])-vm[3]*(xc-xm[3]));
    samar(fluxm[3],&r[3],emu,mode);
    flux[4]=0.5*rou*((um[4]+uc)*(yc-ym[4])-(vm[4]+vc)*(xc-xm[4]));
    fluxm[4]=rou*(um[4]*(yc-ym[4])-vm[4]*(xc-xm[4]));
    samar(fluxm[4],&r[4],emu,mode);
    eqn[(1-1)*12+1-1]=(r[1]-1.)*flux[1]+r[4]*flux[4];
    eqn[(1-1)*12+4-1]=(1.-r[1])*flux[1];
    eqn[(1-1)*12+10-1]=-(r[4]*flux[4]);
    eload[1]=0.0;
    eqn[(4-1)*12+4-1]=(r[2]-1.)*flux[2]+r[1]*flux[1];
    eqn[(4-1)*12+7-1]=(1.-r[2])*flux[2];
    eqn[(4-1)*12+1-1]=-(r[1]*flux[1]);
    eload[4]=0.0;
    eqn[(7-1)*12+7-1]=(r[3]-1.)*flux[3]+r[2]*flux[2];
    eqn[(7-1)*12+10-1]=(1.-r[3])*flux[3];
    eqn[(7-1)*12+4-1]=-(r[2]*flux[2]);
    eload[7]=0.0;
    eqn[(10-1)*12+10-1]=(r[4]-1.)*flux[4]+r[3]*flux[3];
    eqn[(10-1)*12+1-1]=(1.-r[4])*flux[4];
    eqn[(10-1)*12+7-1]=-(r[3]*flux[3]);
    eload[10]=0.0;
    eqn[(2-1)*12+2-1]=(r[1]-1.)*flux[1]+r[4]*flux[4];
    eqn[(2-1)*12+5-1]=(1.-r[1])*flux[1];
    eqn[(2-1)*12+11-1]=-(r[4]*flux[4]);
    eload[2]=0.0;
    eqn[(5-1)*12+5-1]=(r[2]-1.)*flux[2]+r[1]*flux[1];
    eqn[(5-1)*12+8-1]=(1.-r[2])*flux[2];
    eqn[(5-1)*12+2-1]=-(r[1]*flux[1]);
    eload[5]=0.0;
    eqn[(8-1)*12+8-1]=(r[3]-1.)*flux[3]+r[2]*flux[2];
    eqn[(8-1)*12+11-1]=(1.-r[3])*flux[3];
    eqn[(8-1)*12+5-1]=-(r[2]*flux[2]);
    eload[8]=0.0;
    eqn[(11-1)*12+11-1]=(r[4]-1.)*flux[4]+r[3]*flux[3];
    eqn[(11-1)*12+2-1]=(1.-r[4])*flux[4];
    eqn[(11-1)*12+8-1]=-(r[3]*flux[3]);
    eload[11]=0.0;
    for (i=2; i<=ndof; ++i)
        for (j=1; j<=i-1; ++j)
        {
            cccc = eqn[(i-1)*12+j-1];
            eqn[(i-1)*12+j-1] = eqn[(j-1)*12+i-1];
            eqn[(j-1)*12+i-1] = cccc;
        }
    return;
}


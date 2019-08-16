/* subroutine sub1 */
void squr(xc,xcx1,xmx1,xmx2,uc,ucu1,umu1,umu2,flux,fluxr)
//      implicit real*8 (a-h,o-z)
double xc[4],xcx1[4],xmx1[4],xmx2[4],uc[4],ucu1[4],umu1[4],umu2[4];
double *flux,*fluxr;
{
    int i;
    double ufu1[4],ufu2[4],aa[4],bb[4],cc[4];
    for (i=1; i<=3; ++i)
    {
        ufu1[i]=(uc[i]+ucu1[i]+umu1[i])/3;
        ufu2[i]=(uc[i]+ucu1[i]+umu2[i])/3;
        aa[i]=xmx1[i]-xcx1[i];
        bb[i]=xc[i]-xcx1[i];
        cc[i]=xmx2[i]-xcx1[i];
    }
    *flux=(ufu1[1]*(aa[2]*bb[3]-aa[3]*bb[2])
           -ufu1[2]*(aa[1]*bb[3]-aa[3]*bb[1])
           +ufu1[3]*(aa[1]*bb[2]-aa[2]*bb[1])
           +ufu2[1]*(bb[2]*cc[3]-bb[3]*cc[2])
           -ufu2[2]*(bb[1]*cc[3]-bb[3]*cc[1])
           +ufu2[3]*(bb[1]*cc[2]-bb[2]*cc[1]))/2 ;
    *fluxr=(ucu1[1]*(aa[2]*bb[3]-aa[3]*bb[2])
            -ucu1[2]*(aa[1]*bb[3]-aa[3]*bb[1])
            +ucu1[3]*(aa[1]*bb[2]-aa[2]*bb[1])
            +ucu1[1]*(bb[2]*cc[3]-bb[3]*cc[2])
            -ucu1[2]*(bb[1]*cc[3]-bb[3]*cc[1])
            +ucu1[3]*(bb[1]*cc[2]-bb[2]*cc[1]))/2 ;
    return;
}

disp bx by bz bxr byr bzr bxi byi bzi
coef axr axi ayr ayi azr azi ur ui
coor r s o
shap %1 %2
gaus %3
$cc double omega,sigma;
$cc double curlaxr,curlayr,curlazr,curlaxi,curlayi,curlazi;
$cc double signbx,signby,signbz;
$cc double bbx,bby,bbz;
mass %1 vol vol vol vol vol vol vol vol vol
$i
$cc r0=0.0;
$cc for (i=1; i<=nnode; ++i) r0+=^coorr[1][i];
$cc r0*=1.0e-003/nnode;
$cc for (i=1; i<=nnode; ++i) {
$cc if (^coorr[1][i]<r0) ^coorr[1][i]=r0;
$cc if (^coorr[2][i]<1.0e-003) ^coorr[2][i]=1.0e-003; }

func 
$cc vol = r*r*sin(s);
$cv curlaxr=+{azr/s}/r+ azr /(r*tan(s))-{ayr/o}/(r*sin(s))
$cv curlayr=+{axr/o}/(r*sin(s))-{azr/r}- azr /r
$cv curlazr=+{ayr/r}+ ayr /r-{axr/s}/r
$cv curlaxi=+{azi/s}/r+ azi /(r*tan(s))-{ayi/o}/(r*sin(s))
$cv curlayi=+{axi/o}/(r*sin(s))-{azi/r}- azi /r
$cv curlazi=+{ayi/r}+ ayi /r-{axi/s}/r
 
stif
$cc if(curlaxr>=0)  // bx
$cc    signbx=1.0;
$cc else
$cc    signbx=-1.0;
$cc if(curlayr>=0)  // by
$cc    signby=1.0;
$cc else
$cc    signby=-1.0;
$cc if(curlazr>=0)  // bz
$cc    signbz=1.0;
$cc else
$cc    signbz=-1.0;
$cc bbx=signbx*sqrt(curlaxr*curlaxr+curlaxi*curlaxi);
$cc bby=signby*sqrt(curlayr*curlayr+curlayi*curlayi);
$cc bbz=signbz*sqrt(curlazr*curlazr+curlazi*curlazi);
dist=+[bx;bx]*0
 
load=+[bx]*vol*bbx
+[by]*vol*bby
+[bz]*vol*bbz
+[bxr]*vol*curlaxr
+[byr]*vol*curlayr
+[bzr]*vol*curlazr
+[bxi]*vol*curlaxi
+[byi]*vol*curlayi
+[bzi]*vol*curlazi
 
end
 

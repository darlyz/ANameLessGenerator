disp bx by bz bxr byr bzr bxi byi bzi
coef axr axi ayr ayi azr azi ur ui
coor x y z
shap %1 %2
gaus %3
$cc double omega,sigma;
$cc double curlaxr,curlayr,curlazr,curlaxi,curlayi,curlazi;
$cc double signbx,signby,signbz;
$cc double bbx,bby,bbz;
mass %1 vol vol vol vol vol vol vol vol vol
 
func
$cc vol = 1.0;
$cv curlaxr=+{azr/y}-{ayr/z}
$cv curlayr=+{axr/z}-{azr/x}
$cv curlazr=+{ayr/x}-{axr/y}
$cv curlaxi=+{azi/y}-{ayi/z}
$cv curlayi=+{axi/z}-{azi/x}
$cv curlazi=+{ayi/x}-{axi/y}
 
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
 

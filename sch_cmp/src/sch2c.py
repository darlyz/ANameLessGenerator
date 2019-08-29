'''
 Copyright: Copyright (c) 2019
 Created: 2019-8-30
 Author: Zhang_Licheng
 Title: generate c code file from ges
 All rights reserved
'''

import re

tab = ' '*4

def sch2ec(sch_dict, fieldSN, objname, elem_func_list, cfile):

    # ------------------- write head -----------------------
    cfile.write('#include "felac.h"\n')
    for elem_func in elem_func_list:
        cfile.write(f"void {fieldSN}{elem_func}(double *,double *,double *,double *,double *,double *,double *,int,int);" + '\n')

    # bgn '#head.sub'
    if '@head' in sch_dict:
        cfile.write('\n'.join(sch_dict['@head']) + '\n')
    # end '#head.sub'

    # ------------------- write e-func name and parameters -----------------------
    method = 'normal' # need to improve
    if method == 'normal':
        cfile.write("void adda(int *,double *,int *,int,int *,double *,int,int);"   + '\n')
        cfile.write(f"void e{objname}{fieldSN}(coor0,dof,nodvar,ubf,elem,matrix,f)" + '\n')
    elif method == 'exp':
        cfile.write(f"void e{objname}{fieldSN}(coor0,dof,nodvar,ubf,elem,init)"     + '\n')
    elif method == 'str':
        cfile.write(f"void e{objname}{fieldSN}(coor0,dof,elem)"                     + '\n')

    cfile.write("struct coordinates coor0;"     + '\n')
    cfile.write("struct element elem;"          + '\n')
    cfile.write("int dof;"                      + '\n')
    if method in ['normal', 'exp']:
        cfile.write("int *nodvar;"              + '\n')
        cfile.write("double *ubf;"              + '\n')
    if method == 'exp':
        cfile.write("int init;"                 + '\n')
    if method == 'normal':
        cfile.write("struct matrice matrix;"    + '\n')
        cfile.write("double *f;"                + '\n')
    
    # ------------------- write e-func body -----------------------
    cfile.write("{" + '\n')

    cfile.write(f"{tab}int ntype,nnode,kvar,ibegin;"                                + '\n')
    cfile.write(f"{tab}int i,j,k,l,m,kk,ij,nn,mm,nr,nrw,ne,nne,numel,idof,jdof,"    + '\n')
    cfile.write(f"{tab}    inod,jnod,nodi,nodj,inv,jnv;"                            + '\n')
    cfile.write(f"{tab}int dim,knode,neq;"                                          + '\n')
    cfile.write(f"{tab}int node[500],lm[500];"                                      + '\n')
    cfile.write(f"{tab}double prmt[500],coef[500];"                                 + '\n')
    cfile.write(f"{tab}double *coor,*r,*u;"                                         + '\n')

    if method == 'normal':
        cfile.write(f"{tab}int *numcol,maxa,*na;"       + '\n')
        cfile.write(f"{tab}double *a,*estifn;"          + '\n')
        cfile.write(f"{tab}double mate[500];"           + '\n')
    
    elif method == 'exp':
        cfile.write(f"{tab}double mate[5000];"          + '\n')
        cfile.write(f"{tab}double emmax,emmin,*emass;"  + '\n')

    elif method == 'str':
        cfile.write(f"{tab}int *nodvar;"                + '\n')
        cfile.write(f"{tab}double mate[5000];"          + '\n')
        cfile.write(f"{tab}double emmax,emmin,*emass;"  + '\n')
        cfile.write(f"{tab}int init=0;"                 + '\n')

    # bgn '#struct.sub'
    struct = 0 # need to improve
    if struct == 1:
        cfile.write(f"{tab}int ide[7];" + '\n')
    # end '#struct.sub'

    e_matr_list = []
    for matr in ['stif', 'mass', 'damp', 'load']:
        if matr in sch_dict['defi']:
            e_matr_list.append('*e'+sch_dict['defi'][matr])
    cfile.write(f"{tab}double {','.join(e_matr_list)};"     + '\n')

    vect_dclr_list = []
    for vlist in sch_dict['equation']['vect']:
        for var in vlist:
            vect_dclr_list.append(f'*vect{var}')
    cfile.write(f"{tab}double {','.join(vect_dclr_list)};"  + '\n')

    var_dclr_list = []
    for vlist in sch_dict['equation']['var']:
        for var in vlist:
            var_dclr_list.append(f'*var{var}')
    cfile.write(f"{tab}double {','.join(var_dclr_list)};"   + '\n')

    # bgn '#subet.sub'
    if '@subet' in sch_dict:
        for code_str in sch_dict['@subet']:
            cfile.write(tab + code_str          + '\n')
    # end '#subet.sub'

    # bgn '#begin.sub'
    if method in ['exp', 'str']:
        cfile.write(f"{tab}ibegin=1;"           + '\n')
    # end '#begin.sub'

    cfile.write(f"{tab}dim   = coor0.dim;"      + '\n')
    cfile.write(f"{tab}knode = coor0.knode;"    + '\n')
    cfile.write(f"{tab}coor  = coor0.coor;"     + '\n')
    cfile.write(f"{tab}kvar  = knode*dof;"      + '\n')

    # bgn '#calloc.sub'
    for var in vect_dclr_list:
        cfile.write(f"{tab}{var.lstrip('*')} = (double*) calloc (kvar, sizeof(double));"    + '\n')
    
    for var in var_dclr_list:
        cfile.write(f"{tab}{var.lstrip('*')} = (double*) calloc (knode+1, sizeof(double));" + '\n')
    # end '#calloc.sub'

    cfile.write(f"{tab}a = matrix.a;"                               + '\n')
    cfile.write(f"{tab}na = matrix.na;"                             + '\n')
    cfile.write(f"{tab}neq = matrix.neq;"                           + '\n')
    cfile.write(f"{tab}maxa = matrix.maxa;"                         + '\n')
    cfile.write(f"{tab}numcol = matrix.numcol;"                     + '\n')
    cfile.write(f"{tab}for (i=1; i<=maxa; ++i)"                     + '\n')
    cfile.write(f"{tab}{tab}a[i] = 0.0;"                            + '\n')
    cfile.write(f"{tab}u = (double *) calloc(kvar,sizeof(double));" + '\n')
    cfile.write(f"{tab}r = (double *) calloc(500,sizeof(double));"  + '\n')
    cfile.write(f"{tab}for (i=0; i<kvar; ++i)"                      + '\n')
    cfile.write(f"{tab}{tab}u[i] = ubf[i];"                         + '\n')

    # bgn '#ilump.sub'
    # end '#ilump.sub'

    # bgn '#rfile.sub'
    for read_strs in sch_dict['equation']['read']:

        read_strs = read_strs.replace(' ','')

        read_deed,  read_objs = read_strs.lstrip('(').split(')')

        read_mthd,  read_unod = read_deed.split(',')

        objs_list = read_objs.split(',')

        if read_unod == 'unod':
            read_unod += fieldSN

        if read_mthd == 's':
            cfile.write(f"{tab}nrw = 0;" + '\n')

        elif read_mthd.isnumeric():
            cfile.write(f"{tab}nrw = {int(read_mthd)};" + '\n')

        for var in objs_list:

            if '*vect'+var in vect_dclr_list:

                cfile.write(f"{tab  }for (j=1; j<=dof; ++j)"                                        + '\n')
                cfile.write(f"{tab*2}for (i=1; i<=knode; ++i)"                                      + '\n')
                cfile.write(f"{tab*3}{var}[(j-1)*(knode)+i-1] = {read_unod}[(nrw+j-1)*knode+i-1];"  + '\n')
                cfile.write(f"{tab  }nrw += dof;"                                                   + '\n')

            elif '*var'+var in var_dclr_list:

                cfile.write(f"{tab  }for (i=1; i<=knode; ++i)"              + '\n')
                cfile.write(f"{tab*2}var[i] = {read_unod}[nrw*knode+i-1];"  + '\n')
                cfile.write(f"{tab  }nrw++ ;"                               + '\n')
    # end '#rfile.sub'

    cfile.write(f"{tab}nn = 0;"             + '\n')
    cfile.write(f"{tab}mm = 0;"             + '\n')
    cfile.write(f"{tab}numel = 0;"          + '\n')
    cfile.write(f"{tab}ntype = elem.ntype;" + '\n')

    # bgn '#nbde.sub'
    # end '#nbde.sub'

    cfile.write(f"{tab   }for (ityp=1; ityp<=ntype; ++ityp)"        + '\n')
    cfile.write(   tab  +"{"                                        + '\n')
    cfile.write(f"{tab*2 }ibegin=1;"                                + '\n')
    cfile.write(f"{tab*2 }nmate = elem.nmate[ityp];"                + '\n')
    cfile.write(f"{tab*2 }nprmt = elem.nprmt[ityp];"                + '\n')
    cfile.write(f"{tab*2 }for (i=1; i<=nmate; ++i)"                 + '\n')
    cfile.write(f"{tab*3 }for(j=1; j<=nprmt; ++j)"                  + '\n')
    cfile.write(f"{tab*4 }mate[(i-1)*nprmt+j] = elem.mate[++mm];"   + '\n')
    cfile.write(f"{tab*2 }nelem = elem.nelem[ityp];"                + '\n')
    cfile.write(f"{tab*2 }nnode = elem.nnode[ityp];"                + '\n')
    cfile.write(f"{tab*2 }nne   = nnode-1;"                         + '\n')
    cfile.write(f"{tab*2 }for(ne=1; ne<=nelem; ++ne)"               + '\n')
    cfile.write(   tab*2+"{"                                        + '\n')
    cfile.write(f"{tab*3 }for (j=1; j<=nnode; ++j)"                 + '\n')
    cfile.write(f"{tab*4 }node[j] = elem.node[++nn];"               + '\n')
    cfile.write(f"{tab*3 }if(node[nnode]<0)"                        + '\n')
    cfile.write(   tab*3+"{"                                        + '\n')
    cfile.write(f"{tab*4 }if(ne==ibegin)ibegin=ibegin+1;"           + '\n')
    cfile.write(f"{tab*4 }goto l700;"                               + '\n')
    cfile.write(   tab*3+"}"                                        + '\n')
    cfile.write(f"{tab*3 }if  (ne==ibegin)"                         + '\n')
    cfile.write(   tab*3+"{"                                        + '\n')
    cfile.write(f"{tab*4 }k=0;"                                     + '\n')
    cfile.write(f"{tab*4 }for(j=1; j<=nne; ++j)"                    + '\n')
    cfile.write(   tab*4+"{"                                        + '\n')
    cfile.write(f"{tab*5 }jnod = node[j];"                          + '\n')
    cfile.write(f"{tab*5 }if(jnod>0)"                               + '\n')
    cfile.write(f"{tab*6 }for(l=1; l<=dof; ++l)"                    + '\n')
    cfile.write(f"{tab*7 }if(nodvar[(l-1)*(knode)+jnod-1] !=0 )"    + '\n')
    cfile.write(f"{tab*8 }k++;"                                     + '\n')
    cfile.write(   tab*4+"}"                                        + '\n')
    cfile.write(f"{tab*4 }kk = k*k;"                                + '\n')

    # bgn '#subdim.sub'
    cfile.write(f"{tab*4 }es = (double *) calloc(kk,sizeof(double));"       + '\n')

    if sch_dict['defi']['type'] == 'l':
        cfile.write(f"{tab*4 }em = (double *) calloc(k+1,sizeof(double));"  + '\n')
        cfile.write(f"{tab*4 }ec = (double *) calloc(k+1,sizeof(double));"  + '\n')

    elif sch_dict['defi']['type'] == 'd':
        cfile.write(f"{tab*4 }em = (double *) calloc(kk,sizeof(double));"   + '\n')
        cfile.write(f"{tab*4 }ec = (double *) calloc(kk,sizeof(double));"   + '\n')

    cfile.write(f"{tab*4 }ef = (double *) calloc(k+1,sizeof(double));"      + '\n')
    # end '#subdim.sub'

    if method == 'e':
        cfile.write(f"{tab*4 }estifn = (double *) calloc(kk+1,sizeof(double));" + '\n')

    cfile.write(   tab*3+"}"                                                    + '\n')
    cfile.write(f"{tab*3 }for (j=1; j<=nne; ++j)"                               + '\n')
    cfile.write(   tab*3+"{"                                                    + '\n')
    cfile.write(f"{tab*4 }jnod=node[j];"                                        + '\n')
    cfile.write(f"{tab*4 }if(jnod<0)"                                           + '\n')
    cfile.write(f"{tab*5 }jnod = -jnod;"                                        + '\n')
    cfile.write(f"{tab*4 }prmt[nprmt+j] = jnod;"                                + '\n')

    # bgn '#coef.sub'
    cfile.write(f"{tab*4 }i = 0;" + '\n')

    for var in sch_dict['coef']:

        if '*vect'+var in vect_dclr_list:
            cfile.write(f"{tab*4 }for (l=1; l<=dof; ++l)"                                   + '\n')
            cfile.write(   tab*4+"{"                                                        + '\n')
            cfile.write(f"{tab*4 }    coef[j-1+i*nne]={'vect'+var}[(l-1)*(knode)+jnod-1];"  + '\n')
            cfile.write(f"{tab*4 }    i++;"                                                 + '\n')
            cfile.write(   tab*4+"}"                                                        + '\n')

        elif '*var'+var in var_dclr_list:
            cfile.write(f"{tab*4 }coef[j-1+i*nne]={'var'+var}[jnod];"   + '\n')
            cfile.write(f"{tab*4 }i++;"                                 + '\n')
    # end '#coef.sub'

    cfile.write(f"{tab*4 }for(i=1; i<=dim; ++i)"                            + '\n')
    cfile.write(f"{tab*5 }r[(i-1)*(nne)+j-1] = coor[(i-1)*(knode)+jnod-1];" + '\n')
    cfile.write(   tab*3+"}"                                                + '\n')
    cfile.write(f"{tab*3 }imate = node[nnode];"                             + '\n')
    cfile.write(f"{tab*3 }for (j=1; j<=nprmt; ++j)"                         + '\n')
    cfile.write(f"{tab*4 }prmt[j] = mate[(imate-1)*nprmt+j];"               + '\n')

    # bgn '#subfort.sub'
    # end '#subfort.sub'

    # bgn '#elem.sub'
    cfile.write(f"{tab*3 }switch (ityp)"                                            + '\n')
    cfile.write(   tab*3+"{"                                                        + '\n')
    for efunc_i, efunc in enumerate(elem_func_list):
        cfile.write(f"{tab*3 }case {efunc_i+1} :"                                   + '\n')
        cfile.write(f"{tab*4 }{fieldSN}{efunc}(r,coef,prmt,es,em,ec,ef,ne,ibegin);" + '\n')
        cfile.write(f"{tab*4 }break;"                                               + '\n')
    cfile.write(   tab*3+"}"                                                        + '\n')
    # end '#elem.sub'

    cfile.write(f"{tab*3 }for (i=1; i<=k; ++i)"                         + '\n')
    cfile.write(f"{tab*4 }for (j=1; j<=k; ++j)"                         + '\n')
    cfile.write(f"{tab*5 }estifn[(i-1)*(k)+j-1]=0.0;"                   + '\n')
    cfile.write(f"{tab*3 }for (i=1; i<=k; ++i)"                         + '\n')
    cfile.write(   tab*3+"{"                                            + '\n')
    cfile.write(f"{tab*4 }for (j=1; j<=k; ++j)"                         + '\n')
    cfile.write(   tab*4+"{"                                            + '\n')
    cfile.write(f"{tab*5 }estifn[(i-1)*(k)+j-1]=estifn[(i-1)*(k)+j-1]"  + '\n')

    # bgn '#matrix.sub'
    for insert_str in sch_dict['equation']['matrix']['stif']:
        instead_str = f"[{sch_dict['defi']['stif']}]"
        str_instead = "es[(i-1)*(k)+j-1]"
        cfile.write(f"{tab*5+' '*21}{insert_str.replace(instead_str,str_instead)}")

    if sch_dict['defi']['mdty'] == 'd':

        for matr, smatr in zip( ['mass', 'damp'], ['m', 'c'] ):

            if matr in sch_dict['equation']['matrix']:

                for insert_str in sch_dict['equation']['matrix'][matr]:
                    instead_str = f"[{sch_dict['defi'][matr]}]"
                    str_instead = f"e{smatr}[(i-1)*(k)+j-1]"
                    cfile.write(f"\n{tab*5+' '*21}{insert_str.replace(instead_str,str_instead)}")
    
    cfile.write(';\n')
    # end '#matrix.sub'

    cfile.write(   tab*4+"}"                                            + '\n')
    cfile.write(f"{tab*4 }estifn[(i-1)*(k)+i-1]=estifn[(i-1)*(k)+i-1]")

    # bgn '#addlump.sub'
    if sch_dict['defi']['mdty'] == 'l':

        for matr, smatr in zip( ['mass', 'damp'], ['m', 'c'] ):

            if matr in sch_dict['equation']['matrix']:

                for insert_str in sch_dict['equation']['matrix'][matr]:
                    instead_str = f"[{sch_dict['defi'][matr]}]"
                    str_instead = f"e{smatr}[i]"
                    cfile.write(f"\n{tab*4+' '*21}{insert_str.replace(instead_str,str_instead)}")

    cfile.write(';\n')
    # end '#addlump.sub'

    cfile.write(   tab*3+"}"                                                        + '\n')
    cfile.write(f"{tab*3 }i=0;"                                                     + '\n')
    cfile.write(f"{tab*3 }for (inod=1; inod<=nne; ++inod)"                          + '\n')
    cfile.write(   tab*3+"{"                                                        + '\n')
    cfile.write(f"{tab*4 }nodi = node[inod];"                                       + '\n')
    cfile.write(f"{tab*4 }for (idof=1; idof<=dof; ++idof)"                          + '\n')
    cfile.write(   tab*4+"{"                                                        + '\n')
    cfile.write(f"{tab*5 }inv = nodvar[(idof-1)*(knode)+nodi-1];"                   + '\n')
    cfile.write(f"{tab*5 }if (inv==0)"                                              + '\n')
    cfile.write(f"{tab*6 }goto l600;"                                               + '\n')
    cfile.write(f"{tab*5 }i++;"                                                     + '\n')
    cfile.write(f"{tab*5 }lm[i] = inv;"                                             + '\n')
    cfile.write(f"{tab*5 }if  (inv>0)"                                              + '\n')
    cfile.write(   tab*5+"{"                                                        + '\n')
    cfile.write(f"{tab*6 }u[(idof-1)*(knode)+nodi-1] = u[(idof-1)*(knode)+nodi-1]"  + '\n')

    # bgn '#lvl.sub'
    for insert_str in sch_dict['equation']['forc']['load']:
        instead_str = f"[{sch_dict['defi']['load']}]"
        str_instead = "ef[i]"
        cfile.write(f"{tab*6+' '*27}{insert_str.replace(instead_str,str_instead)}")

    if sch_dict['defi']['mdty'] == 'l':

        for matr, smatr in zip( ['mass', 'damp'], ['m', 'c'] ):

            if matr in sch_dict['equation']['forc']:

                for insert_str in sch_dict['equation']['forc'][matr]:

                    matr_pattern = f"\\[{sch_dict['defi'][matr]}\\*\\w+\\]"
                    matr_pattern = re.compile(matr_pattern)
                    matr_pattern = matr_pattern.search(insert_str)

                    if matr_pattern is not None:
                        instead_str = matr_pattern.group()

                        matr_posx = instead_str.lstrip('[').rstrip(']').split('*')[1]

                        str_instead = f"e{smatr}[i]*vect{matr_posx}[(idof-1)*(knode)+nodi-1]"

                        insert_str = insert_str.replace(instead_str,str_instead)

                    cfile.write(f"\n{tab*6+' '*27}{insert_str}")

    cfile.write(';\n')
    # end '#lvl.sub'

    cfile.write(   tab*5+"}"                                                        + '\n')
    cfile.write(f"{tab*5 }j = 0;"                                                   + '\n')
    cfile.write(f"{tab*5 }for (jnod=1; jnod<=nne; ++jnod)"                          + '\n')
    cfile.write(   tab*5+"{"                                                        + '\n')
    cfile.write(f"{tab*6 }nodj = node[jnod];"                                       + '\n')
    cfile.write(f"{tab*6 }for(jdof=1; jdof<=dof; ++jdof)"                           + '\n')
    cfile.write(   tab*6+"{"                                                        + '\n')
    cfile.write(f"{tab*7 }jnv = nodvar[(jdof-1)*(knode)+nodj-1];"                   + '\n')
    cfile.write(f"{tab*7 }if (jnv==0)"                                              + '\n')
    cfile.write(f"{tab*8 }goto l400;"                                               + '\n')
    cfile.write(f"{tab*7 }j++;"                                                     + '\n')
    cfile.write(f"{tab*7 }if(jnv>0)"                                                + '\n')
    cfile.write(   tab*7+"{"                                                        + '\n')
    cfile.write(f"{tab*8 }u[(jdof-1)*(knode)+nodj-1] = u[(jdof-1)*(knode)+nodj-1]")

    # bgn '#dv.sub'
    for insert_str in sch_dict['equation']['forc']['stif']:

        matr_pattern = f"\\[{sch_dict['defi']['stif']}\\*\\w+\\]"
        matr_pattern = re.compile(matr_pattern)
        matr_pattern = matr_pattern.search(insert_str)

        if matr_pattern is not None:
            instead_str = matr_pattern.group()

            matr_posx = instead_str.lstrip('[').rstrip(']').split('*')[1]

            str_instead = f"es[(i-1)*(k)+j-1]*vect{matr_posx}[(idof-1)*(knode)+nodi-1]"

            insert_str = insert_str.replace(instead_str,str_instead)

        cfile.write(f"\n{tab*8+' '*27}{insert_str}")

    if sch_dict['defi']['mdty'] == 'd':

        for matr, smatr in zip( ['mass', 'damp'], ['m', 'c'] ):

            if matr in sch_dict['equation']['forc']:

                for insert_str in sch_dict['equation']['forc'][matr]:

                    matr_pattern = f"\\[{sch_dict['defi'][matr]}\\*\\w+\\]"
                    matr_pattern = re.compile(matr_pattern)
                    matr_pattern = matr_pattern.search(insert_str)

                    if matr_pattern is not None:
                        instead_str = matr_pattern.group()

                        matr_posx = instead_str.lstrip('[').rstrip(']').split('*')[1]

                        str_instead = f"e{smatr}[(i-1)*(k)+j-1]*vect{matr_posx}[(idof-1)*(knode)+nodi-1]"

                        insert_str = insert_str.replace(instead_str,str_instead)

                    cfile.write(f"\n{tab*8+' '*27}{insert_str}")

    cfile.write(';\n')
    # end '#dv.sub'

    cfile.write(f"{tab*8 }if  (inv<0)"                                                  + '\n')
    cfile.write(f"{tab*9 }u[(jdof-1)*(knode)+nodj-1]=u[(jdof-1)*(knode)+nodj-1]")
    cfile.write(         "-estifn[(i-1)*(k)+j-1]*u[(idof-1)*(knode)+nodi-1];"           + '\n')
    cfile.write(   tab*7+"}"                                                            + '\n')
    cfile.write(         "l400:"                                                        + '\n')
    cfile.write(f"{tab*7 }continue;"                                                    + '\n')
    cfile.write(   tab*6+"}"                                                            + '\n')
    cfile.write(   tab*5+"}"                                                            + '\n')
    cfile.write(         "l600:"                                                        + '\n')
    cfile.write(f"{tab*5 }continue;"                                                    + '\n')
    cfile.write(   tab*4+"}"                                                            + '\n')
    cfile.write(   tab*3+"}"                                                            + '\n')
    cfile.write(f"{tab*3 }adda(na,a,numcol,k,lm,estifn,neq,maxa);"                      + '\n')
    cfile.write(         "l700:"                                                        + '\n')
    cfile.write(f"{tab*3 }if(ne==nelem)"                                                + '\n')
    cfile.write(   tab*3+"{"                                                            + '\n')
    cfile.write(f"{tab*4 }if(es != null)"                                               + '\n')
    cfile.write(   tab*4+"{"                                                            + '\n')

    # bgn '#subfree.sub'
    cfile.write(f"{tab*5 }free(es);"  + '\n')
    cfile.write(f"{tab*5 }free(em);"  + '\n')
    cfile.write(f"{tab*5 }free(ec);"  + '\n')
    cfile.write(f"{tab*5 }free(ef);"  + '\n')
    # end '#subfree.sub'

    cfile.write(f"{tab*5 }free(estifn);"                    + '\n')
    cfile.write(   tab*4+"}"                                + '\n')
    cfile.write(   tab*3+"}"                                + '\n')
    cfile.write(   tab*2+"}"                                + '\n')
    cfile.write(f"{tab*2 }numel += nelem;"                  + '\n')
    cfile.write(   tab  +"}"                                + '\n')
    cfile.write(f"{tab   }free(r);"                         + '\n')
    cfile.write(f"{tab   }for (ij=1; ij<=neq; ++ij)"        + '\n')
    cfile.write(   tab  +"{"                                + '\n')
    cfile.write(f"{tab*2 }f[ij] = 0.0;"                     + '\n')
    cfile.write(   tab  +"}"                                + '\n')
    cfile.write(f"{tab   }for (i=1; i<=dof; ++i)"           + '\n')
    cfile.write(   tab  +"{"                                + '\n')
    cfile.write(f"{tab*2 }for (j=1; j<=knode; ++j)"         + '\n')
    cfile.write(   tab*2+"{"                                + '\n')
    cfile.write(f"{tab*3 }ij = nodvar[(i-1)*(knode)+j-1];"  + '\n')
    cfile.write(f"{tab*3 }if  (ij>0)"                       + '\n')
    cfile.write(f"{tab*4 }f[ij] += u[(i-1)*(knode)+j-1];"   + '\n')
    cfile.write(   tab*2+"}"                                + '\n')
    cfile.write(   tab  +"}"                                + '\n')
    cfile.write(f"{tab   }free(u);"                         + '\n')

    # bgn '#end.sub'
    # end '#end.sub'

    # bgn '#free.sub'
    for var in vect_dclr_list:
        cfile.write(f"{tab}free({var.lstrip('*')});"    + '\n')
    
    for var in var_dclr_list:
        cfile.write(f"{tab}free({var.lstrip('*')});"    + '\n')
    # end '#free.sub'

    cfile.write(f"{tab }return;" + '\n')
    cfile.write(       "}"       + '\n')
# end sch2ec()
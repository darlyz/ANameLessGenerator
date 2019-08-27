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
        cfile.write(f"void {fieldSN}{elem_func}(double *,double *,double *,double *,double *,double *,double *,int,int);\n")

    if '@head' in sch_dict:
        cfile.write('\n'.join(sch_dict['@head']) + '\n')

    # ------------------- write e-func name and parameters -----------------------
    method = 'normal' # need to improve
    if method == 'normal':
        cfile.write("void adda(int *,double *,int *,int,int *,double *,int,int);\n")
        cfile.write(f"void e{objname}{fieldSN}(coor0,dof,nodvar,ubf,elem,matrix,f)\n")
    elif method == 'exp':
        cfile.write(f"void e{objname}{fieldSN}(coor0,dof,nodvar,ubf,elem,init)\n")
    elif method == 'str':
        cfile.write(f"void e{objname}{fieldSN}(coor0,dof,elem)\n")

    cfile.write("struct coordinates coor0;\n")
    cfile.write("struct element elem;\n")
    cfile.write("int dof;\n")
    if method in ['normal', 'exp']:
        cfile.write("int *nodvar;\n")
        cfile.write("double *ubf;\n")
    if method == 'exp':
        cfile.write("int init;\n")
    if method == 'normal':
        cfile.write("struct matrice matrix;\n")
        cfile.write("double *f;\n")
    
    # ------------------- write e-func body -----------------------
    cfile.write("{\n")

    cfile.write(f"{tab}int ntype,nnode,kvar,ibegin;\n")
    cfile.write(f"{tab}int i,j,k,l,m,kk,ij,nn,mm,nr,nrw,ne,nne,numel,idof,jdof,\n")
    cfile.write(f"{tab}    inod,jnod,nodi,nodj,inv,jnv;\n")
    cfile.write(f"{tab}int dim,knode,neq;\n")
    cfile.write(f"{tab}int node[500],lm[500];\n")
    cfile.write(f"{tab}double prmt[500],coef[500];\n")
    cfile.write(f"{tab}double *coor,*r,*u;\n")

    if method == 'normal':
        cfile.write(f"{tab}int *numcol,maxa,*na;\n")
        cfile.write(f"{tab}double *a,*estifn;\n")
        cfile.write(f"{tab}double mate[500];\n")
    
    elif method == 'exp':
        cfile.write(f"{tab}double mate[5000];\n")
        cfile.write(f"{tab}double emmax,emmin,*emass;\n")

    elif method == 'str':
        cfile.write(f"{tab}int *nodvar;\n")
        cfile.write(f"{tab}double mate[5000];\n")
        cfile.write(f"{tab}double emmax,emmin,*emass;\n")
        cfile.write(f"{tab}int init=0;\n")

    struct = 0 # need to improve
    if struct == 1:
        cfile.write(f"{tab}int ide[7];\n")

    e_matr_list = []
    for matr in ['stif', 'mass', 'damp', 'load']:
        if matr in sch_dict['defi']:
            e_matr_list.append('*e'+sch_dict['defi'][matr])
    cfile.write(f"{tab}double {','.join(e_matr_list)};\n")

    vect_dclr_list = []
    for vlist in sch_dict['equation']['vect']:
        for var in vlist:
            vect_dclr_list.append(f'*vect{var}')
    cfile.write(f"{tab}double {','.join(vect_dclr_list)};\n")

    if '@subet' in sch_dict:
        for code_str in sch_dict['@subet']:
            cfile.write(tab + code_str + '\n')

# end sch2ec()
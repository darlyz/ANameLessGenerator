'''
 Copyright: Copyright (c) 2019
 Created: 2019-7-23
 Author: Zhang_Licheng
 Title: generate c code file from ges
 All rights reserved
'''
# need to improve at tag @!
import re

tab = ' '*4
scalar = 0
vector = 1
matrix = 2
def ges2c(ges_info, ges_dict, cfile):

    disp_num = len(ges_dict['disp'])
    var_num  = 0
    for num in ges_dict['var'].values():
        var_num += num
    node_num = int(ges_dict['node'])
    gaus_num = len(ges_dict['gaus']) - 1
    dim      = int(ges_info['dim'])
    refc_num = len(ges_dict['refc'])
    coor_num = len(ges_dict['coor'])
    if 'coef' in ges_dict:
        coef_num = len(ges_dict['coef'])

    # -------------------------------- write head ---------------------------------------
    cfile.write('#include "felac.h"\n')
    cfile.write('double nx,ny,nz;\n')
    cfile.write('int nnode,ngaus,ndisp,nrefc,ncoor,nvar;\n')
    cfile.write('double vol,det,weigh,stif,fact,shear,r0;\n')

    cfile.write(f'int nvard[{disp_num+1}],kdord[{disp_num+1}],kvord[{disp_num*var_num}];\n')

    cfile.write(f'double refc[{dim*node_num}],gaus[{gaus_num+1}];\n')

    cfile.write('/* .... nnode ---- the number of nodes\n')
    cfile.write('   .... ngaus ---- the number of numerical integral points\n')
    cfile.write('   .... ndisp ---- the number of unknown functions\n')
    cfile.write('   .... nrefc ---- the number of reference coordinates\n')
    cfile.write('   .... nvar ---- the number of unknown varibles var\n')
    cfile.write('   .... refc ---- reference coordinates at integral points\n')
    cfile.write('   .... gaus ---- weight number at integral points\n')
    cfile.write('   .... nvard ---- the number of var for each unknown\n')
    cfile.write('   .... kdord ---- the highest differential order for each unknown\n')
    cfile.write('   .... kvord ---- var number at integral points for each unknown */\n')

    cfile.write(f'double coor[{dim+1}];\n')

    cfile.write(f'double coorr[{dim*node_num}];\n')

    if 'coef' in ges_dict:
        cfile.write(f'double coefr[{dim*node_num}];\n')

    cfile.write(f'double rctr[{dim*dim}],crtr[{dim*dim}];\n')

    cfile.write("/*   .... rctr ---- jacobi's matrix\n")
    cfile.write("     .... crtr ---- inverse matrix of jacobi's matrix */\n")

    cfile.write('void dshap(double (*shap)(double *,int),\n')
    cfile.write('           double *,double *,int,int,int);\n')

    cfile.write('void dcoor(double (*shap)(double *,int),\n')
    cfile.write('           double *,double *,double *,int,int,int);\n')

    cfile.write('double invm(int,double *,double *);\n')

    cfile.write('double inver_rc(int,int,double *,double *);\n')

    if 'coef' in ges_dict:
        cfile.write('void dcoef(double (*shap)(double *,int),\n')
        cfile.write('           double *,double *, double *,int,int,int);\n')

    cfile.write('static void initial();\n')

    cfile.write('static void tran_coor(double *,double *,double *,double *);\n')

    cfile.write('static double ftran_coor(double *,int);\n')

    for disp in ges_dict['disp']:
        cfile.write(f'static void shap_{disp}(double *,double *);\n')
        cfile.write(f'static double fshap_{disp}(double *,int);\n')

    if 'coef' in ges_dict:
        cfile.write('static void coef_shap(double *,double *,double *,double *);\n')
        cfile.write('static double fcoef_shap(double *,int);\n')

    cfile.write('void shapn(int,int,int,double *,double *,double *,int,int,int);\n')

    if 'coef' in ges_dict:
        cfile.write('void shapc(int,int,int,double *,double *,double *,int,int,int);\n')

    cfile.write('/* subroutine */\n')

    # ------------------------------------ begin write func -------------------------------------------
    if 'coef' in ges_dict:
        coefa = f'coefa[{dim*node_num}]'
    else:
        coefa = '*coefa'

    cfile.write(f'void {ges_info["name"]}(coora,coefa,prmt,estif,emass,edamp,eload,num,ibegin)\n')
    cfile.write(f'double coora[{dim*node_num}],{coefa},*prmt,estif[{dim*node_num*dim*node_num}],*emass,*edamp,*eload;\n')

    cfile.write('int num,ibegin;\n')

    cfile.write('/* .... coora ---- nodal coordinate value\n')
    cfile.write('   .... coefa ---- nodal coef value\n')
    cfile.write('   .... estif ---- element stiffness\n')
    cfile.write('   .... emass ---- element mass matrix\n')
    cfile.write('   .... edamp ---- element damping matrix\n')
    cfile.write('   .... eload ---- element load vector\n')
    cfile.write('   .... num   ---- element no. */\n')

    # ------------------------------------- func body -----------------------------------------------
    cfile.write('{\n')

    cfile.write(tab+'double refcoor[4]= {0.0,0.0,0.0,0.0};\n')

    if 'coef' in ges_dict:
        cfile.write(f'{tab}double coef[{coef_num+1}];\n')
        cfile.write(f"{tab}double {','.join(ges_dict['coef'])};\n")
        cfile.write(f'{tab}double coefd[{coef_num*dim*dim}],coefc[{coef_num*dim*dim}];\n')

    cfile.write(f'{tab}double ')
    cfile.write(','.join([f'e{strs}[{dim*node_num+1}]' for strs in ges_dict['func']]) + ';\n')

    cfile.write(f'{tab}double ')
    cfile.write(','.join(ges_dict['coor']) + ',' + ','.join(ges_dict['refc']) + ';\n')

    cfile.write(f'{tab}double elump[{dim*node_num+1}];\n')

    cfile.write(f'{tab}static double ')
    cfile.write(','.join([f'r{disp}[{gaus_num*(dim+1)*node_num}]' for disp in ges_dict['disp']]) + ',')
    cfile.write(','.join([f'c{disp}[{(dim+1)*node_num}]' for disp in ges_dict['disp']]) + ';\n')

    cfile.write(f'{tab}/* .... store shape functions and their partial derivatives\n')
    cfile.write(f'{tab}     .... for all integral points */\n')

    cfile.write(f'{tab}int i,j,igaus;\n')

    cfile.write(f'{tab}int ')
    cfile.write(','.join(['ig_'+disp for disp in ges_dict['disp']]) + ',iv,jv;\n')

    # ----------------------------------- write code before mate -------------------------------------------
    if 'BFmate' in ges_dict['code']:
        release_code(tab, 'BFmate', ges_dict, ges_info, cfile)

    # --------------------------------------- write initialize ---------------------------------------------
    cfile.write(tab+ f"// .... initialize the basic data\n")
    cfile.write(tab+ f"if (num==ibegin) initial();\n")

    cfile.write(tab+ f"for (i=1; i<={dim}; ++i)\n")
    cfile.write(tab+ f"    for (j=1; j<={node_num}; ++j)\n")
    cfile.write(tab+ f"        coorr[(i-1)*({node_num})+j-1]=coora[(i-1)*({node_num})+j-1];\n")

    if 'coef' in ges_dict:
        cfile.write(tab+ f"for (i=1; i<={dim}; ++i)\n")
        cfile.write(tab+ f"    for (j=1; j<={node_num}; ++j)\n")
        cfile.write(tab+ f"        coefr[(i-1)*({node_num})+j-1]=coefa[(i-1)*({node_num})+j-1];\n")

    cfile.write(tab+ f"for (i=1; i<={disp_num*node_num}; ++i)\n")
    cfile.write(tab+  "{\n")

    if 'mass' in ges_dict:
        cfile.write(tab+ f"    emass[i]=0.0;\n")

    if 'damp' in ges_dict:
        cfile.write(tab+ f"    edamp[i]=0.0;\n")

    if 'mass' in ges_dict and ges_dict['mass'][0] == 'lump' \
    or 'damp' in ges_dict and ges_dict['damp'][0] == 'lump' :
        cfile.write(tab+ f"    elump[i]=0.0;\n")

    cfile.write(tab+ f"    eload[i]=0.0;\n")

    cfile.write(tab+ f"    for (j=1; j<={disp_num*node_num}; ++j)\n")
    cfile.write(tab+  "    {\n")
    cfile.write(tab+ f"        estif[(i-1)*({disp_num*node_num})+j-1]=0.0;\n")
    cfile.write(tab+  "    }\n")

    cfile.write(tab+  "}\n")

    # -------------------------------------- write $I code ------------------------------------------------
    init_find = 0
    for code_strs in ges_dict['code']['BFmate']:
        if re.match(r'\$I', code_strs, re.I) != None:
            init_find = 1 
            continue
        if init_find == 1:
            cfile.write(tab+code_strs.replace('$cc','').lstrip())

    # -------------------------------------- write material -----------------------------------------------
    if 'mate' in ges_dict:
        for i,mate in enumerate(ges_dict['mate']['default'].keys()):
            cfile.write(f'{tab}{mate}=prmt[{i+1}];\n')

    # ----------------------------------- write code after mate -------------------------------------------
    if 'AFmate' in ges_dict['code']:
        release_code(tab, 'AFmate', ges_dict, ges_info, cfile)

    # --------------------------------- begin loop gaussain node ------------------------------------------
    cfile.write(f'{tab}for (igaus=1; igaus<=ngaus; ++igaus)\n')
    cfile.write(tab +'{\n')
    cfile.write(f'{tab}{tab}for (i=1; i<=nrefc; ++i)\n{tab*3}refcoor[i]=refc[(i-1)*({node_num})+igaus-1];\n')

    cfile.write(f'{tab}{tab}tran_coor(refcoor,coor,coorr,rctr);\n')
    cfile.write(f'{tab}{tab}// .... coordinate caculation by reference coordinates\n')
    cfile.write(f'{tab}{tab}// det = invm(ncoor,rctr,crtr);\n')
    cfile.write(f'{tab}{tab}det = inver_rc(nrefc,ncoor,rctr,crtr);\n')

    cfile.write(f"{tab}{tab}/* .... coordinate transfer from reference to original system\n")
    cfile.write(f"{tab}{tab}   .... rctr ---- jacobi's matrix\n")
    cfile.write(f"{tab}{tab}   .... crtr ---- inverse matrix of jacobi's matrix */\n")

    for i,coor in enumerate(ges_dict['coor']):
        cfile.write(f'{tab}{tab}{coor}=coor[{i+1}];\n')

    for i,refc in enumerate(ges_dict['refc']):
        cfile.write(f'{tab}{tab}{refc}=refcoor[{i+1}];\n')

    if 'coef' in ges_dict:
        cfile.write(f'{tab}{tab}coef_shap(refcoor,coef,coefr,coefd);\n')
        cfile.write(f"{tab}{tab}// .... compute coef functions and their partial derivatives\n")
        for i,coef in enumerate(ges_dict['coef']):
            cfile.write(f'{tab}{tab}{coef}=coef[{i+1}];\n')

    for disp in ges_dict['disp']:
        cfile.write(f'{tab}{tab}ig_{disp}=(igaus-1)*{node_num}*{dim+1};\n')

    cfile.write(f'{tab}{tab}if (num>ibegin)\n{tab}{tab}{tab}goto l2;\n')

    cfile.write(f"{tab}{tab}// .... the following is the shape function caculation\n")
    for disp in ges_dict['disp']:
        cfile.write(f'{tab}{tab}shap_{disp}(refcoor,&r{disp}[ig_{disp}]);\n')

    cfile.write('l2:\n')

    cfile.write(f'{tab}{tab}/* .... the following is the shape function transformation\n')
    cfile.write(f'{tab}{tab}      .... from reference coordinates to original coordinates */\n')
    for disp in ges_dict['disp']:
        cfile.write(f'{tab}{tab}shapn(nrefc,ncoor,{node_num},&r{disp}[ig_{disp}],c{disp},crtr,{1},{4},{4});\n') # need to certify '1 4 4' means @!

    if 'coef' in ges_dict:
        cfile.write(f'{tab}{tab}/* .... the coef function transformation\n')
        cfile.write(f'{tab}{tab}  .... from reference coordinates to original coordinates */\n')
        cfile.write(f'{tab}{tab}shapc(nrefc,ncoor,{coef_num},coefd,coefc,crtr,{2},{9},{9});\n') # need to certify '2 9 9' means @!

    cfile.write( f'{tab}{tab}weigh=det*gaus[igaus];\n')

    cfile.write(f'{tab}{tab}for (i=1; i<={disp_num*node_num}; ++i)\n')
    cfile.write( tab*2 + '{\n')
    for func in ges_dict['func']:
        cfile.write(f'{tab}{tab}{tab}e{func}[i] = 0.0;\n')
    cfile.write( tab*2 + '}\n')

    # write func paragraph
    if 'vol' in ges_dict:
        cfile.write(tab*2 + re.sub(r'\$cc', '', ges_dict['vol'], 0, re.I).lstrip())

    if 'func' in ges_dict['code']:
        release_code(tab*2, 'func', ges_dict, ges_info, cfile)

    # write stif, mass, damp paragraph
    for key_word in ges_dict.keys():

        if key_word in ['stif', 'mass', 'damp']:

            cfile.write(f'{tab}{tab}// the following is the {key_word} matrix computation\n')

            if key_word in ges_dict['code'].keys():

                release_code(tab*2, key_word, ges_dict, ges_info, cfile)

            release_weak(tab*2, key_word, ges_dict, ges_info, cfile)

    # write load paragraph
    cfile.write(tab*2 +'// the following is the load vector computation\n')
    if 'load' in ges_dict:
        release_weak(tab*2, 'load', ges_dict, ges_info, cfile)

    # end of element sub function
    cfile.write('l999:\n')
    cfile.write(f'{tab}return;\n')
    cfile.write('}\n\n')

    # write initial()
    cfile.write(f'static void initial()\n')
    cfile.write('{\n')
    cfile.write(f'{tab}ngaus = {gaus_num};\n')
    cfile.write(f'{tab}ndisp = {disp_num};\n')
    cfile.write(f'{tab}nrefc = {refc_num};\n')
    cfile.write(f'{tab}ncoor = {coor_num};\n')
    cfile.write(f'{tab}nvar  = {var_num};\n')
    cfile.write(f'{tab}nnode = {node_num};\n')

    for i,disp in enumerate(ges_dict['disp']):
        cfile.write(f'{tab}kdord[{i+1}]={ges_dict["disp_driv_order"][disp]};\n')
        cfile.write(f'{tab}nvard[{i+1}]={ges_dict["var"][disp]};\n')
        for j in range(ges_dict['var'][disp]):
            gaus_order = ges_dict['shap'][disp][j].split('=')[0].strip().replace(disp,'')
            kvord = (int(gaus_order)-1)*disp_num + i+1
            cfile.write(f'{tab}kvord[({j+1}-1)*{disp_num}+{i+1}-1]={kvord};\n')

    for i in range(gaus_num):
        for j in range(dim):
            cfile.write(f'{tab}refc[({j+1}-1)*{gaus_num}+{i+1}-1]={ges_dict["gaus"][i+1][j]};\n')
        cfile.write(f'{tab}gaus[{i+1}]={ges_dict["gaus"][i+1][dim]};\n')

    cfile.write(tab+'return;\n')
    cfile.write('}\n')

    # write shap functions
    for shap in ges_dict['shap'].keys():
        cfile.write(f"static void shap_{shap}(refc,shpr)\n")
        cfile.write(f"double *refc,shpr[{(dim+1)*gaus_num}];\n")
        cfile.write("{\n")
        cfile.write(f"    double (*shap)(double *,int)=&fshap_{shap};\n")
        cfile.write(f"    dshap(shap,refc,shpr,{dim},{gaus_num},{1});\n") # 1 maybe the derivative order @!
        cfile.write(f"    return;\n")
        cfile.write("}\n")

        cfile.write(f"static double fshap_{shap}(double *refc,int n)\n")
        cfile.write("{\n")
        cfile.write(f"// extern double *coor;\n")
        cfile.write(f"{tab}double ")
        cfile.write(f"{','.join(ges_dict['refc'])};\n")
        cfile.write(f"{tab}double fval,")
        cfile.write(f"{','.join(ges_dict['coor'])};\n")
        for i,coor in enumerate(ges_dict['coor']):
            cfile.write(f"{tab}{coor}=coor[{i+1}];\n")

        for i,refc in enumerate(ges_dict['refc']):
            cfile.write(f"{tab}{refc}=refc[{i+1}];\n")
        cfile.write(f"{tab}switch (n)\n")
        cfile.write(tab+"{\n")

        for i,expr in enumerate(ges_dict['shap'][shap]):
            cfile.write(f"{tab}case {i+1}:\n")
            cfile.write(f"{tab}{tab}fval={expr.split('=')[1].strip()};\n")
            cfile.write(f"{tab}{tab}break;\n")

        cfile.write(f"//{tab}default:\n")
        cfile.write(tab+"}\n")
        cfile.write(f"{tab}return fval;\n")
        cfile.write("}\n")

    # write transcoor functions
    cfile.write(f"static void tran_coor(double *refc,double *coor,double *coorr,double *rc)\n")
    cfile.write("{\n")
    cfile.write(f"{tab}double (*shap)(double *,int)=&ftran_coor;\n")
    cfile.write(f"{tab}dcoor(shap,refc,coor,rc,{dim},{dim},{1});\n") # 1 maybe the derivative order @!
    cfile.write(f"{tab}return;\n")
    cfile.write("}\n")

    cfile.write(f"static double ftran_coor(double *refc,int n)\n")
    cfile.write("{\n")
    cfile.write(f"{tab}double fval,")
    cfile.write(f"{','.join(ges_dict['refc'])};\n")
    cfile.write(f"{tab}double ")
    cfile.write(f"{','.join(map(lambda x: x+f'[{gaus_num+1}]',ges_dict['coor']))};\n")
    cfile.write(f"{tab}int j;\n")
    cfile.write(f"{tab}for (j=1; j<={gaus_num}; ++j)\n")
    cfile.write(tab+"{\n")
    for i,coor in enumerate(ges_dict['coor']):
        cfile.write(f"{tab}{tab}{coor}[j]=coorr[{i}*{gaus_num}+j-1];\n")
    cfile.write(tab+"}\n")
    for i,refc in enumerate(ges_dict['refc']):
        cfile.write(f"{tab}{refc}=refc[{i+1}];\n")
    cfile.write(f"{tab}switch (n)\n")
    cfile.write(tab+"{\n")
    for i,coor in enumerate(ges_dict['coor']):
        cfile.write(f"{tab}case {i+1}:\n")
        cfile.write(f"{tab}{tab}fval=\n")
        for j,tran_expr in enumerate(ges_dict['tran'][coor]):
            var, expr = tran_expr.split('=')
            var = var.strip().replace('(','[').replace(')',']')
            cfile.write(f"{tab}{tab}{tab}+({expr.strip()})*{var}")
            if j == node_num-1:
                cfile.write(';\n')
            else:
                cfile.write('\n')
        cfile.write(f"{tab}{tab}break;\n")
    cfile.write(f"{tab}{tab}//default:\n")
    cfile.write(tab+"}\n")
    cfile.write(f"{tab}return fval;\n")
    cfile.write("}\n")

    # write coef functions
    if 'coef' in ges_dict:
        cfile.write(f"static void coef_shap(double *refc,double *coef,double *coefr,double *coefd)\n")
        cfile.write("{\n")
        cfile.write(f"{tab}double (*shap)(double *,int)=&fcoef_shap;\n")
        cfile.write(f"{tab}dcoef(shap,refc,coef,coefd,{3},{3},{2});\n")
        cfile.write(f"{tab}return;\n")
        cfile.write("}\n")

        cfile.write(f"static double fcoef_shap(double *refc,int n)\n")
        cfile.write("{\n")
        cfile.write(f"{tab}double {','.join(ges_dict['refc'])};\n")
        cfile.write(f"{tab}double {','.join(ges_dict['coor'])},fval;\n")
        cfile.write(f"{tab}double {','.join(map(lambda x: f'{x}[{coor_num*disp_num}]',ges_dict['coef']))};\n")
        cfile.write(f"{tab}int j;\n")
        cfile.write(f"{tab}for (j=1; j<={node_num}; ++j)\n")
        cfile.write(tab+"{\n")
        for i,coef in enumerate(ges_dict['coef']) :
            cfile.write(f"{tab}{tab}{coef}[j]=coefr[{i}*{node_num}+j-1];\n")
        cfile.write(tab+"}\n")
        for i,coor in enumerate(ges_dict['coor']):
            cfile.write(f"{tab}{coor}=coor[{i+1}];\n")
        for i,refc in enumerate(ges_dict['refc']):
            cfile.write(f"{tab}{refc}=refc[{i+1}];\n")

        cfile.write(f"{tab}switch (n)\n")
        cfile.write(tab+"{\n")
        for i,coef in enumerate(ges_dict['coef_shap'].keys()) :
            cfile.write(f"{tab}case {i+1}:\n")
            cfile.write(f"{tab}{tab}fval=\n")
            for j,coef_expr in enumerate(ges_dict['coef_shap'][coef]):
                var, expr = coef_expr.split('=')
                var = var.strip().replace('(','[').replace(')',']')
                cfile.write(f"{tab}{tab}{tab}+({expr.strip()})*{var}")
                if j == node_num-1:
                    cfile.write(';\n')
                else:
                    cfile.write('\n')
            cfile.write(f"{tab}{tab}break;\n")
        cfile.write(f"{tab}{tab}//default:\n")
        cfile.write(tab+"}\n")
        cfile.write(f"{tab}return fval;\n")
        cfile.write("}\n")
        

from src.expr import split_bracket_expr
def release_code(indentation, keywd, ges_dict, ges_info, cfile):

    disp_num = len(ges_dict['disp'])
    node_num = int(ges_dict['node'])
    coor_num = len(ges_dict['coor'])
    dim      = int(ges_info['dim'])
    ges_coor = ges_dict["coor"]
    ges_disp = ges_dict["disp"]

    for code_strs in ges_dict['code'][keywd]:

        if keywd == 'BFmate' \
        and re.match(r'\$I', code_strs, re.I) != None :
            break

        if re.match(r'\$c[cv]', code_strs, re.I) != None:

            code_strs = re.sub(r'^\$c[cv]', '', code_strs, 0, re.I).lstrip()

            insteed_str = ''

            if re.match(r'array', code_strs, re.I) != None:

                code_strs = code_strs.replace('array','').lstrip()

                array_list = re.findall(r'\^\w+(?:\[\d+\]){2}', code_strs)

                for array in array_list:

                    idx_list = list(map(lambda x: int(x.lstrip('[').rstrip(']')), \
                                        re.findall(r'\[\d+\]',array)))

                    tensor_name = array.split('[')[0].lstrip('^')

                    insteed_str = f"{tensor_name}[{idx_list[0]*idx_list[1]}]"

                    code_strs = code_strs.replace(array, insteed_str)

            else:

                array_list = re.findall(r'\^\w+(?:\[\d+\]){2}', code_strs)

                for array in array_list:

                    idx_list = list(map(lambda x: int(x.lstrip('[').rstrip(']')), \
                                        re.findall(r'\[\d+\]',array)))

                    tensor_name = array.split('[')[0]

                    insteed_str = tensor_name.lstrip('^') \
                        + f"[({idx_list[0]}-1)*({ges_dict['array_matrix'][tensor_name][1]})+{idx_list[1]}-1]"

                    code_strs = code_strs.replace(array, insteed_str)

            if re.search(r"\{\w+/\w+\}",code_strs) != None:

                driv_list = re.findall(r"\{\w+/\w+\}",code_strs)
                for coef_driv in driv_list:
                    coef_var, driv_coor = coef_driv.lstrip('{').rstrip('}').split('/')
                    insteed_str = f"coefc[{ges_dict['coef'].index(coef_var)}*{disp_num*coor_num}+{ges_dict['coor'].index(driv_coor)}]"

                    code_strs = code_strs.replace(coef_driv, insteed_str)

            cfile.write(indentation + code_strs)

        elif re.match(r'common', code_strs, re.I) != None:
            pass

        else:

            left_var, righ_exp = code_strs.split('=')
            left_var = left_var.strip()
            righ_exp = righ_exp.strip().rstrip('\n')

            disp, coor = '', ''
            func_exp_list = list(map(lambda x: x.lstrip('[').rstrip(']'), \
                                     re.findall(r'\[\w+(?:/\w+)?\]', righ_exp)))

            for func_exp in func_exp_list:

                if func_exp.isnumeric():
                    continue

                if func_exp.find('/') != -1:
                    disp, coor = func_exp.split('/')

                else:
                    disp = func_exp
                    coor = ''

                if coor == '':
                    insteed_str = f'c{disp}[(i-1)*({dim+1})+{1}-1]'

                else:
                    insteed_str = f'c{disp}[(i-1)*({dim+1})+{ges_coor.index(coor)+2}-1]'

                righ_exp = righ_exp.replace(f'[{func_exp}]',insteed_str)

            cfile.write(indentation + f'for (i=1; i<={node_num}; ++i)\n')
            cfile.write(indentation +  '{\n')
            cfile.write(indentation + f'{tab}iv=kvord[(i-1)*({disp_num})+{ges_disp.index(disp)+1}-1];\n')
            cfile.write(indentation + f'{tab}stif={righ_exp};\n')
            cfile.write(indentation + f'{tab}e{left_var}[iv]+=stif;\n')
            cfile.write(indentation +  '}\n')
# end release_code()

def release_weak(indentation, key_word, ges_dict, ges_info, cfile):

    dim = int(ges_info['dim'])

    disp_num = len(ges_dict['disp'])
    node_num = int(ges_dict['node'])


    if   ges_dict[key_word][0] == 'lump':

        for strs in ges_dict[key_word][1:]:

            parameter, variable = strs.split(']')
            parameter = parameter.replace('[','')
            parameter = re.sub(r'^\+{1,2}','',parameter)
            parameter = re.sub(r'^\+?\-','-',parameter)
            var_order = int(re.search(r'\d+',variable).group())
            variable  = variable.replace(str(var_order),'')

            cfile.write(f"{indentation}stif={parameter};\n")
            cfile.write(f"{indentation}elump[{(var_order-1)*disp_num+ges_dict['disp'].index(variable)+1}]=stif*weigh;\n")

        for i,var in enumerate(ges_dict['disp']):
            cfile.write(f"{indentation}for (i=1; i<=nvard[{i+1}]; ++i)\n")
            cfile.write(indentation+"{\n")
            cfile.write(f"{indentation}{tab}iv = kvord[(i-1)*({disp_num})+{i+1}-1];\n")
            cfile.write(f"{indentation}{tab}e{key_word}[iv]+=elump[iv]*c{var}[(i-1)*({dim+1})+1-1];\n")
            cfile.write(indentation+"}\n")

    
    elif ges_dict[key_word][0] == 'dist':

        # four type of weak form: 
        #   d-d: [disp;disp]
        #   d-f: [disp;func]
        #   f-d: [func;disp]
        #   f-f: [func;func]
        weak_type = {}
        
        # classify by weak type
        left_char, righ_char = '',''
        for strs in ges_dict[key_word][1:]:

            array_list = re.findall(r'\^\w+(?:\[\d+\]){2}', strs)

            for array in array_list:

                idx_list = list(map(lambda x: int(x.lstrip('[').rstrip(']')), \
                                    re.findall(r'\[\d+\]',array)))

                tensor_name = array.split('[')[0]

                insteed_str = tensor_name.lstrip('^') \
                    + f"[({idx_list[0]}-1)*({ges_dict['array_matrix'][tensor_name][1]})+{idx_list[1]}-1]"

                strs = strs.replace(array, insteed_str)

            weak_item = re.search(r'\w+(/\w+)?;\w+(/\w+)?',strs)
            if weak_item != None:
                weak_item = weak_item.group()
            else: 
                continue
            
            left_weak, righ_weak = weak_item.split(';')

            if left_weak.find('/') != -1:
                left_var = left_weak.split('/')[0]
            else: 
                left_var = left_weak

            if righ_weak.find('/') != -1:
                righ_var = righ_weak.split('/')[0]
            else: 
                righ_var = righ_weak
                
            if   left_var in ges_dict['disp']:
                left_char = 'd'
            elif left_var in ges_dict['func']:
                left_char = 'f'

            if   righ_var in ges_dict['disp']:
                righ_char = 'd'
            elif righ_var in ges_dict['func']:
                righ_char = 'f'

            wtype = left_char + '-' + righ_char
            if wtype not in weak_type:
                if  wtype == 'f-f':
                    weak_type[wtype] = []
                else:
                    weak_type[wtype] = {}

            if   wtype == 'f-f':
                weak_type[wtype].append(strs)

            # classify by left and righ disp
            elif wtype == 'd-d':

                disp_type = left_var + '-' + righ_var

                if disp_type not in weak_type[wtype]:
                    weak_type[wtype][disp_type] = []

                weak_type[wtype][disp_type].append(strs)

            # classify by left disp
            elif wtype == 'd-f':

                if left_var not in weak_type[wtype]:
                    weak_type[wtype][left_var] = []

                weak_type[wtype][left_var].append(strs)

            # classify by righ disp
            elif wtype == 'f-d':

                if righ_var not in weak_type[wtype]:
                    weak_type[wtype][righ_var] = []

                weak_type[wtype][righ_var].append(strs)

        # write by weak type
        for wtype in weak_type.keys():

            # write by left and righ disp
            if   wtype == 'd-d':

                for disp_type in weak_type[wtype].keys():

                    left_var, righ_var = disp_type.split('-')

                    cfile.write(f"{indentation}for (i=1; i<={disp_num*node_num}; ++i)\n")
                    cfile.write(indentation+"{\n")
                    cfile.write(f"{indentation}{tab}iv=kvord[(i-1)*{disp_num}+{ges_dict['disp'].index(left_var)+1}-1];\n")
                    cfile.write(f"{indentation}{tab}for (j=1; j<={disp_num*node_num}; ++j)\n")
                    cfile.write(indentation+tab+"{\n")
                    cfile.write(f"{indentation}{tab}{tab}jv=kvord[(j-1)*{disp_num}+{ges_dict['disp'].index(righ_var)+1}-1];\n")
                    cfile.write(f"{indentation}{tab}{tab}stif=")

                    weak_len = len(weak_type[wtype][disp_type])

                    for i,weak_item in enumerate(weak_type[wtype][disp_type]):

                        left_weak, righ_weak = re.search(r'\w+(/\w+)?;\w+(/\w+)?',weak_item).group().split(';')

                        be_insteed = f"[{left_weak};{righ_weak}]"
                        
                        if left_weak.find('/') == -1:
                            left_coor_order = 1
                        else:
                            left_coor_order = ges_dict['coor'].index(left_weak.split('/')[1]) + 2

                        left_insteed = f"c{left_var}[(i-1)*{disp_num}+{left_coor_order}-1]"

                        if righ_weak.find('/') == -1:
                            righ_coor_order = 1
                        else:
                            righ_coor_order = ges_dict['coor'].index(righ_weak.split('/')[1]) + 2

                        righ_insteed = f"c{righ_var}[(i-1)*{disp_num}+{righ_coor_order}-1]"

                        insteed_str = f"{left_insteed}*{righ_insteed}"

                        to_be_write_str = weak_item.replace(be_insteed,insteed_str)

                        if weak_len == 1:
                            cfile.write(f"{to_be_write_str};\n")
                        else:
                            if i == 0:
                                cfile.write(f"{to_be_write_str}\n")
                            elif i == weak_len - 1:
                                cfile.write(f"{indentation}             {to_be_write_str};\n")
                            else:
                                cfile.write(f"{indentation}             {to_be_write_str}\n")

                    cfile.write(f"{indentation}{tab}{tab}e{key_word}[(iv-1)*{disp_num*node_num}+jv-1]+=stif*weigh;\n")
                    cfile.write(indentation+tab+"}\n")
                    cfile.write(indentation+"}\n")

            # write by left disp
            elif wtype == 'd-f':

                for disp_type in weak_type[wtype].keys():

                    left_var = disp_type

                    cfile.write(f"{indentation}for (i=1; i<={disp_num*node_num}; ++i)\n")
                    cfile.write(indentation+"\n")
                    cfile.write(f"{indentation}{tab}iv=kvord[(i-1)*{disp_num}+{ges_dict['disp'].index(left_var)+1}-1];\n")
                    cfile.write(f"{indentation}{tab}for (jv=1; jv<={disp_num*node_num}; ++jv)\n")
                    cfile.write(indentation+tab+"{\n")
                    cfile.write(f"{indentation}{tab}{tab}stif=")

                    weak_len = len(weak_type[wtype][disp_type])

                    for i,weak_item in enumerate(weak_type[wtype][disp_type]):

                        left_weak, righ_func = re.search(r'\w+(/\w+)?;\w+',weak_item).group().split(';')

                        be_insteed = f"[{left_weak};{righ_func}]"

                        if left_weak.find('/') == -1:
                            left_coor_order = 1
                        else:
                            left_coor_order = ges_dict['coor'].index(left_weak.split('/')[1]) + 2

                        left_insteed = f"c{left_var}[(i-1)*{disp_num}+{left_coor_order}-1]"

                        righ_insteed = f"e{righ_func}[jv]"

                        insteed_str = f"{left_insteed}*{righ_insteed}"

                        to_be_write_str = weak_item.replace(be_insteed,insteed_str)

                        if weak_len == 1:
                            cfile.write(f"{to_be_write_str};\n")
                        else:
                            if i == 0:
                                cfile.write(f"{to_be_write_str}\n")
                            elif i == weak_len - 1:
                                cfile.write(f"{indentation}{tab}{tab}{tab} {to_be_write_str};\n")
                            else:
                                cfile.write(f"{indentation}{tab}{tab}{tab} {to_be_write_str}\n")

                    cfile.write(f"{indentation}{tab}{tab}e{key_word}[(iv-1)*{disp_num*node_num}+jv-1]+=stif*weigh;\n")
                    cfile.write(indentation+tab+"}\n")
                    cfile.write(indentation+"}\n")
            
            # write by righ disp
            elif wtype == 'f-d':

                for disp_type in weak_type[wtype].keys():

                    righ_var = disp_type

                    cfile.write(f"{indentation}for (iv=1; iv<={disp_num*node_num}; ++iv)\n")
                    cfile.write(indentation+"{\n")
                    cfile.write(f"{indentation}{tab}for (j=1; j<={disp_num*node_num}; ++j)\n")
                    cfile.write(indentation+tab+"{\n")
                    cfile.write(f"{indentation}{tab}{tab}jv=kvord[(j-1)*{disp_num}+{ges_dict['disp'].index(righ_var)+1}-1];\n")
                    cfile.write(f"{indentation}{tab}{tab}stif=")

                    weak_len = len(weak_type[wtype][disp_type])

                    for i,weak_item in enumerate(weak_type[wtype][disp_type]):

                        left_func, righ_weak = re.search(r'\w+;\w+(/\w+)?',weak_item).group().split(';')

                        be_insteed = f"[{left_func};{righ_weak}]"

                        left_insteed = f"e{left_func}[iv]"

                        if righ_weak.find('/') == -1:
                            righ_coor_order = 1
                        else:
                            righ_coor_order = ges_dict['coor'].index(righ_weak.split('/')[1]) + 2

                        righ_insteed = f"c{righ_var}[(i-1)*{disp_num}+{righ_coor_order}-1]"



                        insteed_str = f"{left_insteed}*{righ_insteed}"

                        to_be_write_str = weak_item.replace(be_insteed,insteed_str)

                        if weak_len == 1:
                            cfile.write(f"{to_be_write_str};\n")
                        else:
                            if i == 0:
                                cfile.write(f"{to_be_write_str}\n")
                            elif i == weak_len - 1:
                                cfile.write(f"{indentation}{tab}{tab}{tab} {to_be_write_str};\n")
                            else:
                                cfile.write(f"{indentation}{tab}{tab}{tab} {to_be_write_str}\n")

                    cfile.write(f"{indentation}{tab}{tab}e{key_word}[(iv-1)*{disp_num*node_num}+jv-1]+=stif*weigh;\n")
                    cfile.write(indentation+tab+"}\n")
                    cfile.write(indentation+"}\n")
            
            elif wtype == 'f-f':

                cfile.write(f"{indentation}for (iv=1; iv<={disp_num*node_num}; ++iv)\n")
                cfile.write(indentation+"{\n")
                cfile.write(f"{indentation}{tab}for (jv=1; jv<={disp_num*node_num}; ++jv)\n")
                cfile.write(indentation+tab+"{\n")
                cfile.write(f"{indentation}{tab}{tab}stif=")

                weak_len = len(weak_type[wtype])

                for i,weak_item in enumerate(weak_type[wtype]):

                    left_func, righ_func = re.search(r'\w+;\w+',weak_item).group().split(';')

                    be_insteed = f"[{left_func};{righ_func}]"

                    left_insteed = f"e{left_func}[iv]"

                    righ_insteed = f"e{righ_func}[jv]"

                    insteed_str = f"{left_insteed}*{righ_insteed}"

                    to_be_write_str = weak_item.replace(be_insteed,insteed_str)

                    if weak_len == 1:
                        cfile.write(f"{to_be_write_str};\n")
                    else:
                        if i == 0:
                            cfile.write(f"{to_be_write_str}\n")
                        elif i == weak_len - 1:
                            cfile.write(f"{indentation}{tab}{tab}{tab} {to_be_write_str};\n")
                        else:
                            cfile.write(f"{indentation}{tab}{tab}{tab} {to_be_write_str}\n")

                cfile.write(f"{indentation}{tab}{tab}e{key_word}[(iv-1)*{disp_num*node_num}+jv-1]+=stif*weigh;\n")
                cfile.write(indentation+tab+"}\n")
                cfile.write(indentation+"}\n")

    if key_word == 'load':

        # two type of weak form:
        # d: [disp]*parameter
        # f: [func]*parameter
        weak_type = {}

        # classify by weak type
        for strs in ges_dict[key_word]:

            array_list = re.findall(r'\^\w+(?:\[\d+\]){2}', strs)

            for array in array_list:

                idx_list = list(map(lambda x: int(x.lstrip('[').rstrip(']')), \
                                    re.findall(r'\[\d+\]',array)))

                tensor_name = array.split('[')[0]

                insteed_str = tensor_name.lstrip('^') \
                    + f"[({idx_list[0]}-1)*({ges_dict['array_matrix'][tensor_name][1]})+{idx_list[1]}-1]"

                strs = strs.replace(array, insteed_str)

            weak_item = re.search(r'\[\w+(/\w+)?\]',strs)
            if weak_item != None:
                weak_item = weak_item.group().lstrip('[').rstrip(']')
            else: 
                continue

            if weak_item.find('/') != -1:
                weak_var = weak_item.split('/')[0]
            else: 
                weak_var = weak_item

            if   weak_var in ges_dict['disp']:
                weak_char = 'd'
            elif weak_var in ges_dict['func']:
                weak_char = 'f'

            if weak_char not in weak_type:
                if  weak_char == 'f':
                    weak_type[weak_char] = []
                else:
                    weak_type[weak_char] = {}

            if   weak_char == 'f':
                weak_type[weak_char].append(strs)

            elif weak_char == 'd':

                if weak_var not in weak_type[weak_char]:
                    weak_type[weak_char][weak_var] = []

                weak_type[weak_char][weak_var].append(strs)

        # write by weak type
        for wtype in weak_type.keys():

            # write by disp
            if   wtype == 'd':

                for weak_var in weak_type[wtype].keys():

                    cfile.write(f"{indentation}for (i=1; i<={node_num}; ++i)\n")
                    cfile.write(indentation+"{\n")
                    cfile.write(f"{indentation}{tab}iv=kvord[(i-1)*({disp_num})+{ges_dict['disp'].index(weak_var)+1}-1];\n")
                    cfile.write(f"{indentation}{tab}stif=")

                    weak_len = len(weak_type[wtype][weak_var])

                    for i,weak_item in enumerate(weak_type[wtype][weak_var]):

                        be_insteed = re.search(r'\[\w+(/\w+)?\]',weak_item).group()

                        weak = be_insteed.lstrip('[').rstrip(']')

                        if weak.find('/') == -1:
                            coor_order = 1
                        else:
                            coor_order = ges_dict['coor'].index(weak.split('/')[1]) + 2

                        insteed_str = f"c{weak_var}[(i-1)*({dim+1})+{coor_order}-1]"

                        to_be_write_str = weak_item.replace(be_insteed,insteed_str)

                        if weak_len == 1:
                            cfile.write(f"{to_be_write_str};\n")
                        else:
                            if i == 0:
                                cfile.write(f"{to_be_write_str}\n")
                            elif i == weak_len - 1:
                                cfile.write(f"{indentation}{tab}{tab} {to_be_write_str};\n")
                            else:
                                cfile.write(f"{indentation}{tab}{tab} {to_be_write_str}\n")

                    cfile.write(f"{indentation}{tab}eload[iv]+=stif*weigh;\n")
                    cfile.write(indentation+"}\n")

            elif wtype == 'f':
                cfile.write(f"{indentation}for (iv=1; iv<={dim*node_num}; ++iv)\n")
                cfile.write(indentation+"{\n")
                cfile.write(f"{indentation}{tab}stif=")

                weak_len = len(weak_type[wtype])

                for i,weak_item in enumerate(weak_type[wtype]):

                    be_insteed = re.search(r'\[\w+\]',weak_item).group()

                    func = be_insteed.lstrip('[').rstrip(']')

                    insteed_str = f"e{func}[iv]"

                    to_be_write_str = weak_item.replace(be_insteed,insteed_str)

                    if weak_len == 1:
                        cfile.write(f"{to_be_write_str};\n")
                    else:
                        if i == 0:
                            cfile.write(f"{to_be_write_str}\n")
                        elif i == weak_len - 1:
                            cfile.write(f"{indentation}{tab}{tab} {to_be_write_str};\n")
                        else:
                            cfile.write(f"{indentation}{tab}{tab} {to_be_write_str}\n")

                cfile.write(f"{indentation}{tab}eload[iv]+=stif*weigh;\n")
                cfile.write(indentation+"}\n")

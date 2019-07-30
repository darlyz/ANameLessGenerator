'''
 Copyright: Copyright (c) 2019
 Created: 2019-7-23
 Author: Zhang_Licheng
 Title: generate c code file from ges
 All rights reserved
'''
import re

def ges2c(ges_info, ges_dict, cfile):

    disp_num = len(ges_dict['disp'])
    var_num  = 0
    for num in ges_dict['var'].values():
        var_num += num
    node_num = int(ges_dict['node'])
    gaus_num = len(ges_dict['gaus']) - 1
    dim      = int(ges_info['dim'])
    if 'coef' in ges_dict:
        coef_num = len(ges_dict['coef'])

    cfile.write('#include "felac.h"\n')
    cfile.write('double nx,ny,nz;\n')
    cfile.write('int nnode,ngaus,ndisp,nrefc,ncoor,nvar;\n')
    cfile.write('double vol,det,weigh,stif,fact,shear,r0;\n')

    cfile.write(f'int nvard[{disp_num+1}],kdord[{disp_num+1}],kvord[{disp_num*var_num}];\n')

    cfile.write(f'double refc[{dim*node_num}],gaus[{gaus_num+1}];\n')

    cfile.write(f'double coor[{dim+1}];\n')

    cfile.write(f'double coorr[{dim*node_num}];\n')

    cfile.write(f'double rctr[{dim*dim}],crtr[{dim*dim}];\n')

    cfile.write('void dshap(double (*shap)(double *,int),\n')
    cfile.write('       double *,double *,int,int,int);\n')
    cfile.write('void dcoor(double (*shap)(double *,int),\n')
    cfile.write('           double *,double *,double *,int,int,int);\n')
    cfile.write('double invm(int,double *,double *);\n')
    cfile.write('double inver_rc(int,int,double *,double *);\n')
    if 'coef' in ges_dict:
        cfile.write('void dcoef(double (*shap)(double *,int),\n')
        cfile.write('       double *,double *, double *,int,int,int);\n')
    cfile.write('static void initial();\n')
    cfile.write('static void tran_coor(double *,double *,double *,double *);\n')
    cfile.write('static double ftran_coor(double *,int);\n')
    for disp in ges_dict['disp']:
        cfile.write(f'static void shap_{disp}(double *,double *);\n')
        cfile.write(f'static double fshap_{disp}(double *,int);\n')
    cfile.write('void shapn(int,int,int,double *,double *,double *,int,int,int);\n')
    if 'coef' in ges_dict:
        cfile.write('void shapc(int,int,int,double *,double *,double *,int,int,int);\n')

    cfile.write(f'void {ges_info["name"]}(coora,coefa,prmt,estif,emass,edamp,eload,num,ibegin)\n')
    cfile.write(f'double coora[{dim*node_num}],*coefa,*prmt,estif[{dim*node_num*dim*node_num}],*emass,*edamp,*eload;\n')

    cfile.write('int num,ibegin;\n')
    cfile.write('{\n')

    cfile.write('\tdouble refcoor[4]= {0.0,0.0,0.0,0.0};\n')

    if 'coef' in ges_dict:
        cfile.write(f'\tdouble coef[{coef_num+1}];\n')

    cfile.write('\tdouble ')
    cfile.write(','.join([f'e{func}[{dim*node_num+1}]' for func in ges_dict['func']]) + ';\n')

    if 'coef' in ges_dict:
        cfile.write(f'\tdouble coefd[{node_num}],coefc[{node_num}];\n')

    cfile.write('\tdouble ')
    cfile.write(','.join(ges_dict['coor']) + ',' + ','.join(ges_dict['refc']) + ';\n')

    cfile.write(f'\tdouble elump[{dim*node_num+1}];\n')

    cfile.write('\tstatic double ')
    cfile.write(','.join([f'r{disp}[{gaus_num*(dim+1)*node_num}]' for disp in ges_dict['disp']]) + ',')
    cfile.write(','.join([f'c{disp}[{(dim+1)*node_num}]' for disp in ges_dict['disp']]) + ';\n')

    cfile.write('\tint i,j,igaus;\n')

    cfile.write('\tint ')
    cfile.write(','.join(['ig_'+disp for disp in ges_dict['disp']]) + ',iv,jv;\n')

    if 'BFmate' in ges_dict['code']:
        release_code('\t', 'BFmate', ges_dict, ges_info, cfile)

    if 'mate' in ges_dict:
        for i,mate in enumerate(ges_dict['mate']['default'].keys()):
            cfile.write(f'\t{mate}=prmt[{i+1}];\n')

    cfile.write(f'\tif (num==ibegin) initial();\n')

    cfile.write(f'\tfor (i=1; i<={dim}; ++i)\n')
    cfile.write(f'\t    for (j=1; j<={node_num}; ++j)\n')
    cfile.write(f'\t        coorr[(i-1)*({node_num})+j-1]=coora[(i-1)*({node_num})+j-1];\n')

    cfile.write(f'\tfor (i=1; i<={disp_num*node_num}; ++i)\n')
    cfile.write( '\t{\n')
    cfile.write(f'\t    eload[i]=0.0;\n')
    cfile.write(f'\t    for (j=1; j<={disp_num*node_num}; ++j)\n')
    cfile.write( '\t    {\n')
    cfile.write(f'\t        estif[(i-1)*({disp_num*node_num})+j-1]=0.0;\n')
    cfile.write( '\t    }\n')
    cfile.write( '\t}\n')

    if 'AFmate' in ges_dict['code']:
        release_code('\t', 'AFmate', ges_dict, ges_info, cfile)

    # to release $I

    cfile.write( '\tfor (igaus=1; igaus<=ngaus; ++igaus)\n')
    cfile.write( '\t{\n')
    cfile.write(f'\t    for (i=1; i<=nrefc; ++i)\n\t\t\trefcoor[i]=refc[(i-1)*({node_num})+igaus-1];\n')

    cfile.write( '\t    tran_coor(refcoor,coor,coorr,rctr);\n')
    cfile.write( '\t\t// det = invm(ncoor,rctr,crtr);\n')
    cfile.write( '\t\tdet = inver_rc(nrefc,ncoor,rctr,crtr);\n')

    for i,coor in enumerate(ges_dict['coor']):
        cfile.write(f'\t\t{coor}=coor[{i+1}];\n')

    for i,refc in enumerate(ges_dict['refc']):
        cfile.write(f'\t\t{refc}=refcoor[{i+1}];\n')

    if 'coef' in ges_dict:
        cfile.write('\t\tcoef_shap(refcoor,coef,coefr,coefd);\n')
        for i,coef in enumerate(ges_dict['coef']):
            cfile.write(f'\t\t{coef}=coef[{i+1}];\n')

    for disp in ges_dict['disp']:
        cfile.write(f'\t\tig_{disp}=(igaus-1)*{node_num}*{dim+1};\n')

    cfile.write('\t\tif (num>ibegin)\n\t\t\tgoto l2;\n')

    for disp in ges_dict['disp']:
        cfile.write(f'\t\tshap_{disp}(refcoor,&r{disp}[ig_{disp}]);\n')

    cfile.write('l2:')

    for disp in ges_dict['disp']:
        cfile.write(f'\t\tshapn(nrefc,ncoor,{node_num},&r{disp}[ig_{disp}],c{disp},crtr,{1},{4},{4});\n') # need to certify '1 4 4' means

    if 'coef' in ges_dict:
        cfile.write(f'\t\tshapc(nrefc,ncoor,{coef_num},coefd,coefc,crtr,{2},{9},{9});\n') # need to certify '2 9 9' means

    cfile.write( '\t\tweigh=det*gaus[igaus];\n')

    cfile.write(f'\t\tfor (i=1; i<={disp_num*node_num}; ++i)\n')
    cfile.write( '\t\t{\n')
    for func in ges_dict['func']:
        cfile.write(f'\t\t\te{func}[i] = 0.0;\n')
    cfile.write( '\t\t}\n')

    if 'vol' in ges_dict:
        cfile.write('\t\t' + re.sub(r'\$cc', '', ges_dict['vol'], 0, re.I).lstrip())

    if 'func' in ges_dict['code']:
        release_code('\t\t', 'func', ges_dict, ges_info, cfile)

    for key_word in ges_dict.keys():

        if key_word in ['stif', 'mass', 'damp']:

            if key_word in ges_dict['code'].keys():

                release_code('\t\t', key_word, ges_dict, ges_info, cfile)

            release_weak('\t\t', key_word, ges_dict, ges_info, cfile)

from expr import split_bracket_expr
def release_code(indentation, keywd, ges_dict, ges_info, cfile):

    disp_num = len(ges_dict['disp'])
    node_num = int(ges_dict['node'])
    coor_num = len(ges_dict['coor'])
    dim      = int(ges_info['dim'])
    ges_coor = ges_dict["coor"]
    ges_disp = ges_dict["disp"]

    for code_strs in ges_dict['code'][keywd]:

        if re.match(r'\$c[cv]', code_strs, re.I) != None:

            code_strs = re.sub(r'\$c[cv]', '', code_strs, 0, re.I).lstrip()

            if re.search(r'\^\w+(?:\[\d+\]){1,2}',code_strs) != None:
                array_list = re.findall(r'\^\w+(?:\[\d+\]){1,2}',code_strs)

                for array in array_list:
                    idx_list = re.findall(r'\[\d+\]',array)
                    var_name = array.split('[')[0].lstrip('^')

                    if re.match(r'double', code_strs, re.I) != None:

                        # it mey be necessary or error for parsing '^xx[d]'
                        if   len(idx_list) == 1:
                            insteed_str = var_name + f"[{int(idx_list[0].lstrip('[').rstrip(']'))-1}]"

                        elif len(idx_list) == 2:
                            array_len = int(idx_list[0].lstrip('[').rstrip(']')) \
                                      * int(idx_list[1].lstrip('[').rstrip(']'))
                            insteed_str = var_name +f'[{array_len}]'

                    else:

                        # it mey be necessary or error for parsing '^xx[d]'
                        if   len(idx_list) == 1:
                            insteed_str = var_name + f"[{int(idx_list[0].lstrip('[').rstrip(']'))}]"

                        elif len(idx_list) == 2:
                            index_str = f"[({idx_list[0].lstrip('[').rstrip(']')}-1)*{ges_dict['array'][var_name][1]} " \
                                      + f"+ {idx_list[1].lstrip('[').rstrip(']')}-1]"
                            insteed_str = var_name + index_str

                    code_strs = code_strs.replace(array, insteed_str)

            if re.search(r"\{\w+/\w+\}",code_strs) != None:

                driv_list = re.findall(r"\{\w+/\w+\}",code_strs)
                for coef_driv in driv_list:
                    coef_var, driv_coor = coef_driv.lstrip('{').rstrip('}').split('/')
                    insteed_str = f"coefc[{ges_dict['coef'].index(coef_var)}*{disp_num*coor_num}+{ges_dict['coor'].index(driv_coor)}]"

                    code_strs = code_strs.replace(coef_driv, insteed_str)

            cfile.write(indentation + code_strs)

        elif re.search(r'\[.*\]', code_strs, re.I) != None:
            left_var = code_strs.split('=')[0].strip()
            exp_list = split_bracket_expr(code_strs.split('=')[1].strip().rstrip('\n'))

            for exp_str in exp_list:
                disp, coor = '', ''
                func_exp = re.search(r'\[.*\]', exp_str, re.I).group()

                if func_exp.find('/') != -1:
                    disp, coor = func_exp.lstrip('[').rstrip(']').split('/')

                else:
                    disp = func_exp.lstrip('[').rstrip(']')

                if coor == '':
                    insteed_str = f'c{disp}[(i-1)*({dim+1})+{1}-1]'

                else:
                    insteed_str = f'c{disp}[(i-1)*({dim+1})+{ges_coor.index(coor)+2}-1]'

                cfile.write(indentation + f'for (i=1; i<={node_num}; ++i)\n')
                cfile.write(indentation +  '{\n')
                cfile.write(indentation + f'    iv=kvord[(i-1)*({disp_num})+{ges_disp.index(disp)+1}-1];\n')
                cfile.write(indentation + f'    stif={exp_str.replace(func_exp,insteed_str)};\n')
                cfile.write(indentation + f'    e{left_var}[iv]+=stif;\n')
                cfile.write(indentation +  '}\n')
# end release_code()

def release_weak(indentation, key_word, ges_dict, ges_info, cfile):

    dim = int(ges_info['dim'])

    disp_len = len(ges_dict['disp'])

    if   ges_dict[key_word][0] == 'lump':

        for strs in ges_dict[key_word][1:]:

            parameter, variable = strs.split(']')
            parameter = parameter.replace('[','')
            parameter = re.sub(r'^\+{1,2}','',parameter)
            parameter = re.sub(r'^\+?\-','-',parameter)
            var_order = int(re.search(r'\d+',variable).group())
            variable  = variable.replace(str(var_order),'')

            cfile.write(f"{indentation}stif={parameter};\n")
            cfile.write(f"{indentation}elump[{(var_order-1)*disp_len+ges_dict['disp'].index(variable)+1}]=stif*weight;\n")

        for i,var in enumerate(ges_dict['disp']):
            cfile.write(f"{indentation}for (i=1; i<=nvard[{i+1}]; ++i)\n")
            cfile.write(indentation+"{\n")
            cfile.write(f"{indentation}    iv = kvord[(i-1)*(3)+{i+1}-1];\n")
            cfile.write(f"{indentation}    e{key_word}[iv]+=elump[iv]*c{var}[(i-1)*({dim+1})+1-1];\n")
            cfile.write(indentation+"}\n")

    
    elif ges_dict[key_word][0] == 'dist':

        # four type of weak form: 
        #   d-d: [disp;disp]
        #   d-f: [disp;func]
        #   f-d: [func;disp]
        #   f-f: [func;func]
        weak_type = {}
        
        for strs in ges_dict[key_word][1:]:
            
            left_weak, righ_weak = re.search(r'\w+(/\w+)?;\w+(/\w+)?',strs).group().split(';')
            print(left_weak, righ_weak)
'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: generate the dict data to ges gesfile
 All rights reserved
'''
import re
import os
import math
from expr import split_bracket_expr, \
                 idx_summation, \
                 cmplx_expr, \
                 expr
from felac_data import operator_data, \
                       shapfunc_data, \
                       gaussian_data

from genxde import gen_obj, ifo_folder

ges_dict_check = 1

scalar = 0
vector = 1
matrix = 2

def xde2ges_dict(ges_info, xde_dict, xde_addr, ges_dict):

    pfelacpath = os.environ['pfelacpath']

    if 'disp' in xde_dict:
        ges_dict['disp_driv_order'] = {}
        for disp in xde_dict['disp']:
            ges_dict['disp_driv_order'][disp] = 1

    # use to deal with @L, @A, vol, singular, ...
    ges_dict['code'] = {}
    for code_key in ['BFmate','AFmate','func','stif','mass','damp']:
        if code_key in xde_dict['code']:
            ges_dict['code'][code_key] = []
            release_code(xde_dict, code_key, pfelacpath, ges_info, ges_dict)

    for key_word in xde_dict.keys():

        if key_word in ['array', 'array_vect', 'array_matrix']:
            ges_dict[key_word] = xde_dict[key_word].copy()

        # parse disp and var declare
        # parse dord and node declare
        elif 'disp' == key_word:
            parse_disp_var(ges_info, xde_dict, ges_dict)

            ges_dict['dord'] = ''
            for strs in xde_dict['disp']: 
                ges_dict['dord'] += '1'+','
    
            ges_dict['node'] = str(ges_info['shap_nodn'])

        # parse refc, coor and coef declare
        elif 'coor' == key_word:
            ges_dict['coor'] =  xde_dict['coor'].copy()

            ges_dict['refc'] = []
            for strs in xde_dict['coor']: 
                ges_dict['refc'].append('r'+strs)

        elif 'coef' == key_word:
            ges_dict['coef'] =  xde_dict['coef'].copy()

        # parse func declare
        elif 'vol' == key_word:
            ges_dict['vol'] =  xde_dict['vol']

        elif 'func' == key_word:
            ges_dict['func'] = []
            for func_list in xde_dict['func']:
                ges_dict['func'] += func_list.copy()

        # 5 parse mate line
        elif 'mate' == key_word:
            ges_dict['mate'] = xde_dict['mate'].copy()

        # parse shap and tran paragraph
        elif 'shap' == key_word:
            parse_shap_tran(pfelacpath, ges_info, xde_dict, ges_dict)

        # parse coef shap
        elif 'coef_shap' == key_word:
            parse_coefshap(pfelacpath, ges_info, xde_dict, ges_dict)

        # parse gaus paragraph
        elif 'gaus' == key_word:
            parse_gaus(pfelacpath, ges_info, xde_dict, ges_dict)

        # parse stif, mass, damp paragraph
        elif key_word in ['stif', 'mass', 'damp']:
            parse_weak(key_word, xde_dict, ges_dict)

        # parse load paragraph
        elif 'load' == key_word:
            parse_load(xde_dict, ges_dict)

    if ges_dict_check != 0:
        import json
        file = open(ifo_folder+'ges_dict.json',mode='w')
        file.write(json.dumps(ges_dict,indent=4))
        file.close()

    return False
# end xde2ges()

def release_code(xde_dict, code_place, pfelacpath, ges_info, ges_dict):
    
    for code_strs in xde_dict['code'][code_place]:

        code_regx = re.match(r'Insr|Tnsr|Cplx|Oprt|Func|ARRAY',code_strs,re.I)

        if code_regx == None:
            if code_strs.find('%') != -1:
                code_strs = code_strs \
                            .replace('%1', ges_info['shap_form']) \
                            .replace('%2', ges_info['shap_nodn'])
            ges_dict['code'][code_place].append(code_strs+'\n')
            continue

        code_key = code_regx.group()

        # Insert C code
        if  code_key == 'Insr':
            if code_strs.find('%') != -1:
                code_strs = code_strs \
                            .replace('%1', ges_info['shap_form']) \
                            .replace('%2', ges_info['shap_nodn'])
            ges_dict['code'][code_place].append(code_strs.replace('Insr_Code:','$cc')+'\n')

        # Tensor expres summation
        elif code_key == 'Tnsr':
            release_tensor_code(code_strs, code_place, xde_dict, ges_dict)

        # complex expres expansion
        elif code_key == 'Cplx':
            release_complex_code(code_strs, code_place, xde_dict, ges_dict)

        # the operator resault assignment
        elif code_key == 'Oprt':
            release_operator_code(code_strs, code_place, pfelacpath, xde_dict, ges_dict)

        elif code_key == 'Func':
            release_funcasgn_code(code_strs, code_place, xde_dict, ges_dict)
        
        elif code_key == 'ARRAY':
            release_array_code(code_strs, code_place, ges_dict)
# end release_code()

def release_tensor_code(code_strs, code_place, xde_dict, ges_dict):

    vect_expr = code_strs.replace('Tnsr_Asgn: ','')

    left_var, righ_expr = vect_expr.split('=')[:2]
    left_var, righ_expr = left_var.strip(), righ_expr.strip().strip(';')

    expr_list = idx_summation(left_var, righ_expr, xde_dict)

    for expres in expr_list:
        if  expres.find('{') != -1 \
        and expres.find('}') != -1:
            ges_dict['code'][code_place].append('$cv '+expres+';\n')
        else:
            ges_dict['code'][code_place].append('$cc '+expres+';\n')
# end release_tensor_code()

def release_complex_code(code_strs, code_place, xde_dict, ges_dict):

    cplx_expr = code_strs.replace('Cplx_Asgn: ','')
    left_var, righ_expr = cplx_expr.split('=')[:2]
    left_var, righ_expr = left_var.strip(), righ_expr.strip().strip(';')

    # if complex expres is a tensor expres, make summation first
    if left_var.find('_') != -1 \
    or righ_expr.find('_') != -1 :

        expr_list = idx_summation(left_var, righ_expr, xde_dict)

        for expres in expr_list:

            cplx_list = expres.split('=')
            cplx_objt = cmplx_expr(cplx_list[1])

            for ri,cmplexpr in zip(['r','i'], cplx_objt.complex_list):
                ges_dict['code'][code_place] \
                    .append(f'$cc {cplx_list[0]}{ri}={cmplexpr};\n')

    else:
        cplx_objt = cmplx_expr(righ_expr)

        for ri,cmplexpr in zip(['r','i'], cplx_objt.complex_list):
            ges_dict['code'][code_place] \
                .append(f'$cc {left_var}{ri}={cmplexpr};\n')
# end release_complex_code()

def release_operator_code(code_strs, code_place, pfelacpath, xde_dict, ges_dict):

    oprt_expr = code_strs.replace('Oprt_Asgn: ','')
    oprt_name, oprt_axis = oprt_expr.split('.')

    # singularity and volume operators
    for oprt_key in ['singular','vol']:
        if oprt_expr.find(oprt_key) != -1:
            xde_dict[oprt_key] = operator_data[oprt_name][oprt_axis]['expr']

    # other operators as grad, div, curl...
    if  oprt_expr.find('singular') == -1 \
    and oprt_expr.find('vol') == -1 :

        # split aa=grad.xy(x,y,u) to aa, grad.xy, [x,y,u]
        left_var,  righ_expr = oprt_expr.split('=')[:2]
        oprt_name, oprt_vars = righ_expr.split('(')[:2]
        oprt_name, oprt_axis = oprt_name.split('.')
        oprt_vars = oprt_vars.replace(' ','')

        if oprt_vars == ')':
            oprt_vars = []

        else:
            oprt_vars = oprt_vars.rstrip(')').split(',')

        # expand vector variable list [x_i,a_i...] --> [x,y,z,a1,a2,...]
        if len(oprt_vars) != 0:

            temp_vars = []
            for var in oprt_vars:
                var_type = var.count('_')

                if var_type == scalar:
                    temp_vars.append(var)

                elif var_type == vector:
                    vect_name = var.split('_')[0]
                    temp_vars += xde_dict['vect'][vect_name]

                elif var_type == matrix:
                    matr_name = var.split('_')[0]
                    for matr_row in xde_dict['matrix'][matr_name][2:]:
                        temp_vars += matr_row

            oprt_vars = temp_vars.copy()

        # replenish default variables
        else:

            # to deal with oprt_axis of [oz、so、s]
            if   'disp' in xde_dict and left_var[0] == '[' and left_var[-1] == ']':
                oprt_vars += xde_dict['coor'] \
                    + xde_dict['disp'][:len(operator_data[oprt_name][oprt_axis]['disp'])]

            elif 'coef' in xde_dict and left_var[0] != '[' and left_var[-1] != ']':
                oprt_vars += xde_dict['coor'] \
                    + xde_dict['coef'][:len(operator_data[oprt_name][oprt_axis]['disp'])]

        oprt_strs = operator_data[oprt_name][oprt_axis]['expr']
        oprt_dfvr = operator_data[oprt_name][oprt_axis]['vars']

        # replace default variable by operator variable
        if len(oprt_vars) == len(oprt_dfvr):
            for oprt_var, dflt_var in zip(oprt_vars, oprt_dfvr):
                oprt_strs = oprt_strs.replace(dflt_var,oprt_var)

        left_vara_type = left_var.count('_')
        left_vara_name = left_var.lstrip('[').rstrip(']').split('_')[0]
        # assign to a temporary list type of 'fvect' or 'fmatr' 
        # used for derivative of 'disp' variables in Func_Asgn step
        # Oprt_Asgn: [a] = opr(*,*) ----------- @L opr f a * *
        if  left_var[0]  == '[' and left_var[-1] == ']' :
            expr_list = oprt_strs.rstrip().split('\n')

            if left_vara_type == scalar: # may be fault tackle
                expres = left_vara_name + '=' + ''.join(expr_list)
                ges_dict['code'][code_place].append(expres)

            elif left_vara_type == vector:
                for ii in range(len(expr_list)):
                    xde_dict['fvect'][left_vara_name][ii+1] = expr_list[ii]

            elif left_vara_type == matrix:
                row, clm = xde_dict['fmatr'][left_vara_name][:2]
                for ii in range(row):
                    for jj in range(clm):
                        xde_dict['fmatr'][left_vara_name][ii+2][jj] = expr_list[ii*row+jj]

        # assign to derivative of distributed known variables such as last step 'disp' resault
        # Oprt_Asgn: a = opr(*,*) ----------- @L opr [svm] a * *
        elif left_var[0]  != '[' and  left_var[-1] != ']' :
            oprt_strs = oprt_strs.replace('[','{').replace(']','}')
            expr_list = oprt_strs.rstrip().split('\n')

            if left_vara_type == scalar:
                expres = left_vara_name + '=' + ''.join(expr_list)
                ges_dict['code'][code_place].append('$cv '+expres)

            elif left_vara_type == vector:
                for keyword in ['vect','array_vect']:
                    if keyword in xde_dict and left_vara_name in xde_dict[keyword]:
                        if len(xde_dict[keyword][left_vara_name]) == len(expr_list):
                            for ii in range(len(expr_list)):
                                ges_dict['code'][code_place] \
                                    .append(f"$cv {xde_dict[keyword][left_vara_name][ii]}={expr_list[ii]}")

            elif left_vara_type == matrix:
                for keyword in ['matrix','array_matrix']:
                    if keyword in xde_dict and left_vara_name in xde_dict[keyword]:
                        matr_len = xde_dict[keyword][left_vara_name][0] \
                                 * xde_dict[keyword][left_vara_name][1]
                        if matr_len == len(expr_list):
                            ii = 0
                            for lists in xde_dict[keyword][left_vara_name][2:]:
                                for strs in lists:
                                    ges_dict['code'][code_place].append(f'$cv {strs}={expr_list[ii]}\n')
                                    ii += 1
# end release_operator_code()

def release_funcasgn_code(code_strs, code_place, xde_dict, ges_dict):

    tnsr_expr = code_strs.replace('Func_Asgn: ','')
    left_var, righ_expr = tnsr_expr.split('=')[:2]
    left_var, righ_expr = left_var.strip(), righ_expr.strip()

    left_var_type = left_var.count('_')

    # assign the temporary list type of 'fvect' or 'fmatr'
    # to the list type of 'vect' or 'matrix'
    if  left_var[0]  != '[' \
    and left_var[-1] != ']' :

        left_var_name = left_var.split('_')[0]

        # Func_Asgn: a = b[*,*] --------- @W a b * *
        if re.search(r'[a-z]+[0-9a-z]*\[([0-9],)*[0-9]?\]$',righ_expr,re.I) != None:

            # read right variable index list
            righ_var = righ_expr.split('[')[0]

            if  righ_expr[-1] == ']' \
            and righ_expr[-2] == '[':
                
                if   'fvect' in xde_dict \
                and righ_var in xde_dict['fvect']:
                    righ_idxs = list(range(len(xde_dict['fvect'][righ_var])))
                
                elif 'fmatr' in xde_dict \
                and righ_var in xde_dict['fmatr']:
                    righ_idxs = list(range(xde_dict['fvect'][righ_var][0] \
                                          *xde_dict['fvect'][righ_var][1]))
                
            else:
                righ_idxs = list(map(lambda x: int(x)-1 , \
                                    righ_expr.split('[')[1].rstrip(']').split(',') ))

            if left_var_type == scalar:
                expres = left_var + '='

                if   'fvect' in xde_dict \
                and righ_var in xde_dict['fvect']:
                    for idx in righ_idxs:
                        expres += xde_dict['fvect'][righ_var][idx]
                
                elif 'fmatr' in xde_dict \
                and righ_var in xde_dict['fmatr']:

                    row, clm = xde_dict['fmatr'][righ_var][:2]
                    fmatr    = xde_dict['fmatr'][righ_var][2:]

                    for idx in righ_idxs:
                        expres += fmatr[int(idx/clm)][idx%clm]
                
                ges_dict['code'][code_place].append(expres+'\n\n')
            
            elif left_var_type == vector:

                expr_list = []

                for keyword in ['vect', 'array_vect']:
                    if keyword in xde_dict and left_var_name in xde_dict[keyword]:
                        temp_list = xde_dict[keyword][left_var_name]

                if len(temp_list) == len(righ_idxs):

                    if   'fvect' in xde_dict and righ_var in xde_dict['fvect']:
                        for var, idx in zip(temp_list, righ_idxs):
                            expr_list.append( var + '=' + \
                                xde_dict['fvect'][righ_var][idx] + '\n\n')
                    
                    elif 'fmatr' in xde_dict and righ_var in xde_dict['fmatr']:

                        row,clm = xde_dict['fmatr'][righ_var][:2]
                        fmatr   = xde_dict['fmatr'][righ_var][2:]

                        for var,idx in zip(temp_list,righ_idxs):
                            expr_list.append(var + '=' + \
                                fmatr[int(idx/clm)][idx%clm] + '\n\n')
                
                ges_dict['code'][code_place] += expr_list

            elif left_var_type == matrix:

                expr_list = []
                for keyword in ['matrix', 'array_matrix']:
                    if keyword in xde_dict and left_var_name in xde_dict[keyword]:
                        matr_len = xde_dict[keyword][left_var_name][0] \
                                 * xde_dict[keyword][left_var_name][1]

                temp_list = xde_dict['matrix'][left_var_name][2:]

                if matr_len == len(righ_idxs):

                    if 'fvect' in xde_dict \
                        and righ_var in xde_dict['fvect']:

                        idx = 0
                        for lists in temp_list:
                            for var in lists:
                                idx+=1
                                expr_list.append( var + '=' + \
                                    xde_dict['fvect'][righ_var][idx] + '\n\n')

                elif 'fmatr' in xde_dict and righ_var in xde_dict['fmatr']:

                    row,clm = xde_dict['fmatr'][righ_var][:2]
                    fmatr   = xde_dict['fmatr'][righ_var][2:]

                    i = 0
                    for matr_row in temp_list:
                        for matr_vara in matr_row:
                            idx = righ_idxs[i]
                            expr_list.append( matr_vara + '=' + \
                                fmatr[int(idx/clm)][idx%clm] + '\n\n')
                            i += 1

                ges_dict['code'][code_place] += expr_list

    # assign the temporary list type of 'fvect' or 'fmatr'
    # to the list type of 'fvect' or 'fmatr'
    elif left_var[0]  == '[' \
    and  left_var[-1] == ']' :

        left_var = left_var.lstrip('[').rstrip(']')
        left_var_name = left_var.split('_')[0]

        # Func_Asgn: [a] = b[*,*] --------- @S a b * *
        if re.search(r'[a-z]+[0-9a-z]*\[([0-9],)*[0-9]?\]$',righ_expr,re.I) != None:

            # read right variable index list
            righ_var = righ_expr.split('[')[0]

            if  righ_expr[-1] == ']' \
            and righ_expr[-2] == '[':

                if 'fvect' in xde_dict \
                and righ_var in xde_dict['fvect']:
                    righ_idxs = list(range(len(xde_dict['fvect'][righ_var])))

                elif 'fmatr' in xde_dict \
                and righ_var in xde_dict['fmatr']:
                    righ_idxs = list(range(xde_dict['fvect'][righ_var][0] \
                                          *xde_dict['fvect'][righ_var][1]))

            else:
                righ_idxs = list(map(lambda x: int(x)-1 , \
                                    righ_expr.split('[')[1].rstrip(']').split(',') ))

            if left_var_type == scalar:       
                expres = left_var_name + '='

                if   'fvect' in xde_dict \
                and righ_var in xde_dict['fvect']:
                    for idx in righ_idxs:
                        expres += xde_dict['fvect'][righ_var][idx]

                elif 'fmatr' in xde_dict \
                and righ_var in xde_dict['fmatr']:

                    row, clm = xde_dict['fmatr'][righ_var][:2]
                    fmatr    = xde_dict['fmatr'][righ_var][2:]

                    for idx in righ_idxs:
                        expres += fmatr[int(idx/clm)][idx%clm]

                ges_dict['code'][code_place].append(expres+'\n\n')

            elif left_var_type == vector:

                vect_len  = len(xde_dict['fvect'][left_var_name])

                if vect_len == len(righ_idxs):

                    if   'fvect' in xde_dict \
                    and righ_var in xde_dict['fvect']:

                        for idx,ii in zip(righ_idxs,range(vect_len)):
                            xde_dict['fvect'][left_var_name][ii] = \
                            xde_dict['fvect'][left_var_name][idx]

                    elif 'fmatr' in xde_dict \
                    and righ_var in xde_dict['fmatr']:

                        row, clm = xde_dict['fmatr'][righ_var][:2]
                        for idx,ii in zip(righ_idxs,range(vect_len)):
                            xde_dict['fvect'][left_var_name][ii] = \
                            xde_dict['fmatr'][righ_var][2:][int(idx/clm)][idx%clm]
            
            elif left_var_type == matrix:

                matr_len = xde_dict['fmatr'][left_var_name][0] \
                         * xde_dict['fmatr'][left_var_name][1]
                lclm     = xde_dict['fmatr'][left_var_name][1]

                if matr_len == len(righ_idxs):
                    if   'fvect' in xde_dict \
                    and righ_var in xde_dict['fvect']:

                        for ii,idx in zip(range(matr_len),righ_idxs):
                            xde_dict['fmatr'][left_var_name][2:][int(idx/clm)][ii%lclm] = \
                                xde_dict['fvect'][righ_var][idx]

                    elif 'fmatr' in xde_dict \
                    and righ_var in xde_dict['fmatr']:

                        row, clm = xde_dict['fmatr'][righ_var][:2]
                        for ii,idx in zip(range(matr_len),righ_idxs):
                            xde_dict['fmatr'][left_var_name][2:][int(idx/clm)][ii%lclm-1] = \
                                xde_dict['fmatr'][righ_var][2:][int(idx/clm)][idx%clm]

        else:
            righ_expr = righ_expr.replace('[','').replace(']','')

            expr_list = idx_summation(left_var,righ_expr,xde_dict)

            left_var_name = left_var.split('_')[0]

            if left_var_type == vector:

                row = len(xde_dict['fvect'][left_var_name])

                for ii in range(row):
                    xde_dict['fvect'][left_var_name][ii] = \
                        expr_list[ii].split('=')[1].replace('++','+').replace('-+','-')

            elif left_var_type == matrix:

                row,clm = xde_dict['fmatr'][left_var_name][:2]

                for ii in range(row):
                    for jj in range(clm):
                        xde_dict['fmatr'][left_var_name][ii+2][jj] = \
                            expr_list[ii*row+jj].split('=')[1].replace('++','+').replace('-+','-')
# end release_funcasgn_code()

def release_array_code(code_strs, code_place, ges_dict):

    def mdfy_indx(matched):
        vect = matched.group('index')
        vect_name,  vect_indx = vect.split('[')
        vect_indx = vect_indx.rstrip(']')
        return f"{vect_name}[{int(vect_indx)+1}]"

    code_strs = re.sub(r'(?P<index>\w+\[\d+\](?!\[\d+\]))', mdfy_indx, code_strs)

    ges_dict['code'][code_place].append(code_strs.replace('ARRAY', '$cc array double') + ';\n')
# end release_array_code()

def parse_disp_var(ges_info, xde_dict, ges_dict):

    # 1.1 parse disp
    ges_dict['disp'] = xde_dict['disp'].copy()

    # 1.2 parse var
    ges_dict['var'] = {}
    var_dict = {}
    pan_vars = set()

    for shap in xde_dict['shap'].keys():

        if shap[-1] == 'c':
            continue

        nodn = int(re.search(r'[1-9]+', shap, re.I).group())
        
        for var in xde_dict['shap'][shap]:
            ges_dict['var'][var] = nodn
# end parse_disp_var()

def parse_shap_tran(pfelacpath, ges_info, xde_dict, ges_dict):

    geslib_coor = ['x','y','z']
    base_shap_strs = ''
    base_shap_type = list(xde_dict['shap'].keys())[0]
    #base_shap_nodn = re.search(r'[1-9]+',base_shap_type,re.I).group()
    #base_shap_form = base_shap_type[0]

    # 9.1 push shap
    ges_dict['shap'] = {}
    for shap in xde_dict['shap'].keys():

        shap_func = 'd' + ges_info['dim'] + shap
        shap_strs = shapfunc_data['sub'][shap_func]['expr']

        # note: save the base shap function for mix element when push tran
        if shap == base_shap_type:
            base_shap_strs = shap_strs

        # 9.1.2 replace shap func's coor by xde's coor
        for coor_i, coor_str in enumerate(xde_dict['coor']):
            shap_strs = shap_strs.replace(geslib_coor[coor_i],'r'+coor_str)

        # 9.1.3 replace shap func's disp by xde's disp and push
        for shap_var in xde_dict['shap'][shap]:

            if shap[-1].lower() == 'c':
                temp_strs = shap_strs.replace('u',xde_dict['shap'][shap][shap_var])

            else:
                temp_strs = shap_strs.replace('u',shap_var)

            ges_dict['shap'][shap_var] = temp_strs.rstrip('\n').split('\n')

    # 9.2 push tran
    ges_dict['tran'] = {}
    shap_expr_list = base_shap_strs.split('\n')
    shap_expr_list.remove('')
    tran_expr_list = []

    # 9.2.1 add '()'
    for shap_expr in shap_expr_list:
        shap_var,shap_exp = shap_expr.split('=')[:2]
        shap_num = re.search(r'[0-9]+', shap_var, re.I).group()
        shap_var = shap_var.replace(shap_num, '('+shap_num+')')
        tran_expr_list.append(shap_var + '=' + shap_exp)

    # 9.2.2 replace shap func's coor by xde's coor
    for coor_i, coor_str in enumerate(xde_dict['coor']) :
        for ii in range(len(tran_expr_list)):
            tran_expr_list[ii] = \
                tran_expr_list[ii].replace(geslib_coor[coor_i],'r'+coor_str)

    # 9.2.3 replace shap func's disp by by xde's coor and write
    for coor_str in xde_dict['coor']:
        ges_dict['tran'][coor_str] = []

        for tran_expr in tran_expr_list:
            ges_dict['tran'][coor_str].append(tran_expr.replace('u', coor_str))
# end parse_shap_tran()

def parse_coefshap(pfelacpath, ges_info, xde_dict, ges_dict):

    ges_dict['coef_shap'] = {}
    geslib_coor = ['x','y','z']

    for shap in xde_dict['coef_shap'].keys():

        shap_func = 'd' + ges_info['dim'] + shap
        shap_strs = shapfunc_data['sub'][shap_func]['expr']

        # 9.2.1 add '()'
        shap_expr_list = shap_strs.rstrip().split('\n')
        coef_expr_list = []

        for shap_expr in shap_expr_list:

            shap_var, shap_exp  = shap_expr.split('=')[:2]
            shap_num  = re.search(r'[0-9]+', shap_var, re.I).group()
            shap_var  = shap_var.replace(shap_num, '('+shap_num+')')
            coef_expr_list.append(shap_var + '=' + shap_exp)

        shap_strs = '\n'.join(coef_expr_list)+'\n'

        # 9.3.2 replace shap func's coor by xde's coor
        for coor_i,coor_str in enumerate(xde_dict['coor']):
            shap_strs = shap_strs.replace(geslib_coor[coor_i],'r'+coor_str)

        # 9.3.3 replace shap func's disp by xde's disp and write
        for shap_var in xde_dict['coef_shap'][shap]:
            temp_string = shap_strs.replace('u', shap_var)
            ges_dict['coef_shap'][shap_var] = temp_string.rstrip('\n').split('\n')
# end parse_coefshap()

def parse_gaus(pfelacpath, ges_info, xde_dict, ges_dict):

    ges_dict['gaus'] = []

    # 9.1 Gaussian integral
    if xde_dict['gaus'][0] == 'g':

        gaus_degree = re.search(r'[0-9]+',xde_dict['gaus'],re.I).group()

        # 9.1.1 line square or cube shap
        if ges_info['shap_form'].lower() in ['l','q','c']:

            gaus_axis = []
            gaus_weit = []

            for line in gaussian_data['line'][gaus_degree].rstrip().split('\n'):
                gaus_strs = line.split()

                gaus_axis.append(gaus_strs[0])
                gaus_weit.append(gaus_strs[1])

            # 9.1.1.2 write line square or cube's gaussian integra
            ges_dict['gaus'].append( 'gaus = ' \
                             + str(len(gaus_weit)**int(ges_info['dim'])) )

            if  ges_info['shap_form'].lower()=='l':
                for axis_i in range(len(gaus_axis)):
                    ges_dict['gaus'].append([])
                    ges_dict['gaus'][axis_i+1].append(gaus_axis[axis_i])
                    ges_dict['gaus'][axis_i+1].append(gaus_weit[axis_i])

            elif ges_info['shap_form'].lower()=='q':
                gaus_i = 0
                for axis_i in range(len(gaus_axis)):
                    for axis_j in range(len(gaus_axis)):
                        weight = float(gaus_weit[axis_i]) \
                                *float(gaus_weit[axis_j])

                        gaus_i += 1
                        ges_dict['gaus'].append([])

                        ges_dict['gaus'][gaus_i].append(gaus_axis[axis_i])
                        ges_dict['gaus'][gaus_i].append(gaus_axis[axis_j])
                        ges_dict['gaus'][gaus_i].append(str(weight))
                                        
            elif ges_info['shap_form'].lower()=='c':
                gaus_i = 0
                for axis_i in range(len(gaus_axis)):
                    for axis_j in range(len(gaus_axis)):
                        for axis_k in range(len(gaus_axis)):
                            weight = float(gaus_weit[axis_i]) \
                                    *float(gaus_weit[axis_j]) \
                                    *float(gaus_weit[axis_k])

                            gaus_i += 1
                            ges_dict['gaus'].append([])

                            ges_dict['gaus'][gaus_i].append(gaus_axis[axis_i])
                            ges_dict['gaus'][gaus_i].append(gaus_axis[axis_j])
                            ges_dict['gaus'][gaus_i].append(gaus_axis[axis_k])
                            ges_dict['gaus'][gaus_i].append(str(weight))

        # 9.1.2 triangle shap
        elif ges_info['shap_form'].lower()=='t':

            # 9.1.2.1 tackle the gaussian degree
            if gaus_degree == '6':
                gaus_degree = '5'

            elif int(gaus_degree) > 12 and int(gaus_degree) < 17:
                gaus_degree = '12'

            elif int(gaus_degree) > 17:
                gaus_degree = '17'

            gaus_list = gaussian_data['triangle'][gaus_degree].rstrip('\n').strip().split('\n')

            ges_dict['gaus'].append(gaus_list[0].strip())
            for gaus_str in gaus_list[1:]:
                ges_dict['gaus'].append(re.split(r'[ \t]+', gaus_str.strip()))

        # 9.1.3 tetrahedron shap
        elif ges_info['shap_form'].lower()=='w':

            # 9.1.3.1 tackle the gaussian degree
            if gaus_degree == '4':
                gaus_degree = '3'

            elif gaus_degree == '6':
                gaus_degree = '5'

            elif int(gaus_degree) > 7:
                gaus_degree = '7'

            gaus_list = gaussian_data['tetrahedron'][gaus_degree].rstrip('\n').strip().split('\n')

            ges_dict['gaus'].append(gaus_list[0].strip())
            for gaus_str in gaus_list[1:]:
                ges_dict['gaus'].append(re.split(r'[ \t]+', gaus_str.strip()))

        else:
            pass

    # 9.2 node integral
    else:
        shap_name = 'd'+ges_info['dim']+ges_info['shap_form']+ges_info['shap_nodn']
        gaus_list = shapfunc_data['gau'][shap_name]['expr'].rstrip('\n').split('\n')

        ges_dict['gaus'].append(gaus_list[0].strip())
        
        for gaus_str in gaus_list[1:]:
            ges_dict['gaus'].append(re.split(r'[ \t]+', gaus_str.strip()))
# end parse_gaus()

def write_func(ges_dict, xde_dict, gesfile):

    gesfile.write('\nfunc\n')

    if 'vol'  in ges_dict :
        gesfile.write(ges_dict['vol'])

    if 'func' in ges_dict['code']:
        for strs in ges_dict['code']['func']:

            if re.match(r'array', strs, re.I) != None:
                strs = strs.replace('array','').lstrip()

            if strs[0] == '$':
                gesfile.write(strs)

            else:
                if strs.find('(') != -1:
                    strs = strs.rstrip('\n')
                    
                    # save derivative in driv_list[] and replace by rplc_list[]
                    driv_list = set(re.findall(r'\[[a-z][a-z0-9]*/[xyzros]\]', strs, re.I))
                    rplc_list = ['driv'+str(i) for i in range(len(driv_list))]

                    for rplc, driv in zip(rplc_list, driv_list):
                        strs = strs.replace(driv, rplc)
                    
                    # expand the bracket
                    expr_objt = expr(strs.split('=')[1])
                    expr_strs = expr_objt.bracket_expand(expr_objt.expr_head)
                    
                    # replace rplc_list[] back from driv_list[]
                    for rplc, driv in zip(rplc_list, driv_list):
                        expr_strs = expr_strs.replace(rplc, driv)

                    strs = strs.split('=')[0] + '=' + expr_strs+'\n\n'

                if strs[-2:] != '\n\n': 
                    strs += '\n'
                
                if 'cmplx_tag' in xde_dict and xde_dict['cmplx_tag'] == 1:

                    left_var, righ_expr = strs.rstrip('\n').split('=')
                    cmplx_var = []
                    cmplx_var.append(left_var.strip())
                    vara_list = re.findall(r'\[\w+/?\w*\]', righ_expr, re.I)

                    for var in vara_list:

                        if var.find('/') != -1:
                            cmplx_var.append(var.lstrip('[').rstrip(']').split('/')[0].strip())

                        else:
                            cmplx_var.append(var.lstrip('[').rstrip(']').strip())

                    real_expr, imag_expr = strs, strs

                    for var in cmplx_var:
                        if var in xde_dict['cmplx_disp'] + xde_dict['cmplx_func']:
                            real_expr = real_expr.replace(var,var+'r')
                            imag_expr = imag_expr.replace(var,var+'i')

                    strs = real_expr + imag_expr

                gesfile.write(strs)
# end write_func()

def parse_weak(weak, xde_dict, ges_dict):

    if xde_dict[weak][0].lower() != 'null' \
    or weak in ges_dict['code']:
        ges_dict[weak] = []

    else: 
        return

    if xde_dict[weak][0] == 'dist':

        left_var = xde_dict[weak][0]
        righ_expr = ''

        for weak_strs in xde_dict[weak][1:]:
            righ_expr += weak_strs

        expr_list = idx_summation(left_var,righ_expr,xde_dict)
        expr_list = split_bracket_expr(expr_list[0])
        ges_dict[weak].append(expr_list[0].replace('=',''))

        for strs in expr_list[1:]:

            if 'cmplx_tag' in xde_dict and xde_dict['cmplx_tag'] == 1:

                weak_item = re.search(r'\[\w+\;\w+\]', strs, re.I)
                cplx_item = re.search(r'\(?\|[+-]?\w+\;[+-]?\w+\|\)?', strs, re.I)

                if weak_item != None: 
                    weak_item = weak_item.group()
                if cplx_item != None: 
                    cplx_item = cplx_item.group()

                weak_left_var, weak_righ_var = weak_item.lstrip('[').rstrip(']').split(';')
                cplx_real_var, cplx_imag_var = cplx_item.lstrip('(').rstrip(')').strip('|').split(';')

                weak_left_list = [weak_left_var+'r', weak_left_var+'i', weak_left_var+'r', weak_left_var+'i']
                weak_righ_list = [weak_righ_var+'r', weak_righ_var+'i', weak_righ_var+'i', weak_righ_var+'r']
                cplx_list      = [cplx_real_var,     cplx_real_var,     cplx_imag_var,     cplx_imag_var]

                if   cplx_list[2][0] == '+' : 
                    cplx_list[2] = cplx_list[2].replace('+','-')

                elif cplx_list[2][0] == '-' : 
                    cplx_list[2] = cplx_list[2].replace('-','+')

                else :  
                    cplx_list[2]  = '-' + cplx_list[2]

                for i in range(4):
                    if re.match(r'[+-]?0(?:\.0*)?|[+-]?\.0+', cplx_list[i] ,re.I) != None \
                    and cplx_list[i][-1] == '0' : 
                        continue

                    ges_dict[weak].append(strs.replace(weak_item, f'[{weak_left_list[i]};{weak_righ_list[i]}]') \
                                               .replace(cplx_item, f'({cplx_list[i]})') )
                
            else: 
                ges_dict[weak].append(strs)

    elif xde_dict[weak][0] == 'lump':

        if len(xde_dict[weak]) == 1:
            xde_dict[weak].append('1.0')

        if len(xde_dict[weak]) == 2: pass

        ges_dict[weak].append('lump')
        for shaps in xde_dict['shap']:
            nodn = re.search(r'\d+',shaps,re.I).group()

            for var in xde_dict['shap'][shaps]:
                for ii in range(int(nodn)):
                    ges_dict[weak].append(f'+[{xde_dict[weak][1]}]{var}{ii+1}')
# end parse_weak()

def parse_load(xde_dict, ges_dict):

    ges_dict['load'] = []

    left_var = 'load'
    righ_expr = ''.join(xde_dict['load'])
    expr_list = idx_summation(left_var,righ_expr,xde_dict)
    expr_list = split_bracket_expr(expr_list[0])

    for strs in expr_list[1:]:

        if 'cmplx_tag' in xde_dict and xde_dict['cmplx_tag'] == 1:

            weak_item = re.search(r'\[\w+\]', strs, re.I)
            cplx_item = re.search(r'\(?\|[+-]?\w+\;[+-]?\w+\|\)?', strs, re.I)

            if weak_item != None: 
                weak_item = weak_item.group()

            if cplx_item != None: 
                cplx_item = cplx_item.group()

            weak_var = weak_item.lstrip('[').rstrip(']')
            cplx_real_var, cplx_imag_var = cplx_item.lstrip('(').rstrip(')').strip('|').split(';')

            weak_list = [weak_var+'r',  weak_var+'i']
            cplx_list = [cplx_real_var, cplx_imag_var]

            for i in range(2):

                if re.match(r'[+-]?0(?:\.0*)?|[+-]?\.0+', cplx_list[i] ,re.I) != None \
                and cplx_list[i][-1] == '0' :
                    continue

                ges_dict['load'].append(strs.replace(weak_item, f'[{weak_list[i]}]') \
                                            .replace(cplx_item, f'({cplx_list[i]})') )

        else: 
            ges_dict['load'].append(strs)
# end parse_load() 

def xde2ges(ges_info, xde_dict, ges_dict, gesfile):

    gesfile.write(ges_info['name']+'\ndefi\n')
        
    # 1 write disp and var declare
    if 'disp' in ges_dict:
        write_disp_var(ges_info, ges_dict, gesfile)

    # 2 write refc, coor and coef declare
    if 'coor' in ges_dict:
        gesfile.write('\nrefc ')
        for strs in ges_dict['refc']: 
            gesfile.write(strs+',')

        gesfile.write('\ncoor ')
        for strs in ges_dict['coor']: 
            gesfile.write(strs+',')

    if 'coef' in ges_dict:
        gesfile.write('\ncoef ')
        for strs in ges_dict['coef']: 
            gesfile.write(strs+',')

    # 3 write func declare
    if 'func' in ges_dict:
        gesfile.write('\nfunc = ')
        for lists in ges_dict['func']:
            for strs in lists:
                gesfile.write(strs+',')

    # 4 write dord and node declare
    if 'dord' in ges_dict:
        gesfile.write('\ndord ')
        gesfile.write(ges_dict['dord'])
        gesfile.write('\nnode '+ges_dict['node']+'\n')

    # 5 write code before mate declaration
    if 'BFmate' in ges_dict['code']:
        for strs in ges_dict['code']['BFmate']: 
            gesfile.write(strs)

    # 6 write mate line
    if 'mate' in ges_dict:
        gesfile.write('mate')

        for var in ges_dict['mate']['default'].keys():
            gesfile.write(' '+var)
            
        for var in ges_dict['mate']['default'].keys():
            gesfile.write(' '+ges_dict['mate']['default'][var])

        gesfile.write('\n')

    # 7 write code after mate declaration
    if 'AFmate' in ges_dict['code']:
        for strs in ges_dict['code']['AFmate']: 
            if re.match(r'array', strs, re.I) != None:
                strs = strs.replace('array','').lstrip()
            gesfile.write(strs)

    if 'singular' in xde_dict:
        gesfile.write(xde_dict['singular'])

    # 8 write shap and tran paragraph
    if 'shap' in ges_dict:
        gesfile.write('\nshap\n')

        for disp_var in ges_dict['shap'].keys():
            gesfile.write(disp_var+'=\n')

            for strs in ges_dict['shap'][disp_var]:
                gesfile.write(strs+'\n')

            gesfile.write('\n')

    if 'tran' in ges_dict:
        gesfile.write('tran\n')

        for coor_str in ges_dict['tran'].keys():
            gesfile.write(coor_str+'=\n')

            for strs in ges_dict['tran'][coor_str]:
                gesfile.write(strs+'\n')

            gesfile.write('\n')

    # 9 write coef shap paragraph
    if 'coef_shap' in ges_dict:
        gesfile.write('coef\n')
        for disp_var in ges_dict['coef_shap'].keys():

            gesfile.write(disp_var+'=\n')

            for strs in ges_dict['coef_shap'][disp_var]:
                gesfile.write(strs+'\n')

            gesfile.write('\n')

    # 10 write gaus paragraph
    if 'gaus' in ges_dict:
        gesfile.write(ges_dict['gaus'][0]+'\n')

        for gaus_pt in ges_dict['gaus'][1:]:
            for val in gaus_pt:

                if val[0] in ['-','+']:
                    gesfile.write(' '+val)

                else:
                    gesfile.write('  '+val)

            gesfile.write('\n')
        gesfile.write('\n')

    # 11 write func paragraph
    if 'func' in ges_dict['code'] \
    or 'vol'  in xde_dict :
        write_func(ges_dict, xde_dict, gesfile)

    # 12 write stif, mass, damp paragraph
    for key_word in ges_dict.keys():

        if key_word in ['stif', 'mass', 'damp']:

            gesfile.write(f'\n{key_word}\n')

            if key_word in ges_dict['code']:
                for strs in ges_dict['code'][key_word]:
                    if re.match(r'array', strs, re.I) != None:
                        strs = strs.replace('array','').lstrip()
                    gesfile.write(strs)
            
            if   ges_dict[key_word][0] == 'dist':
                gesfile.write(ges_dict[key_word][0]+'=')

            elif ges_dict[key_word][0] == 'lump':
                gesfile.write(ges_dict[key_word][0]+'=\n')

            for weak_item in ges_dict[key_word][1:]:
                gesfile.write(weak_item + '\n')

    # 13 write load paragraph
    if 'load' in ges_dict:

        gesfile.write('\n')
        gesfile.write('load=')

        for weak_item in ges_dict['load']:
                gesfile.write(weak_item + '\n')

    gesfile.write('\nend')

    gesfile.close()
# end xde2ges()

def write_disp_var(ges_info, ges_dict, gesfile):

    # 1.1 write disp declare
    gesfile.write('disp ')
    for strs in ges_dict['disp']:
        gesfile.write(strs+',')
    gesfile.write('\n')

    # 1.2 write var declare
    max_nodn = 0
    for var in ges_dict['var']:
        if max_nodn < ges_dict['var'][var]:
            max_nodn = ges_dict['var'][var]
            
    gesfile.write('var')

    i = 0
    for nodi in range(max_nodn):
    
        for strs in ges_dict['var'].keys():
            if nodi >= ges_dict['var'][strs]:
                continue

            gesfile.write(' '+strs+str(nodi+1))
            i += 1
    
            if i == 10:
                gesfile.write('\nvar')
                i = 0
# end parse_disp_var()
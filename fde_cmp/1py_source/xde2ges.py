'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-15
 Author: Zhang_Licheng
 Title: generate the dict data to ges gesfile
 All rights reserved
'''
import re as regx
import os,math
from expr import split_bracket_expr, \
                 idx_summation, \
                 cmplx_expr, \
                 expr
from felac_data import operator_data, \
                       shapfunc_data, \
                       gaussian_data

ges_dict = {}

def xde2ges_dict(ges_info, xde_dict, xde_addr, gesfile):

    pfelacpath = os.environ['pfelacpath']

    # use to deal with @L, @A, vol, singular, ...
    ges_dict['code'] = {}
    for code_key in ['BFmate','AFmate','func','stif','mass','damp']:
        if code_key in xde_dict['code']:
            ges_dict['code'][code_key] = []
            release_code(xde_dict, code_key, pfelacpath, ges_dict)

    # 1 parse disp and var declare
    if 'disp' in xde_dict:
        parse_disp_var(ges_info, xde_dict, ges_dict)

    # 2 parse refc, coor and coef declare
    if 'coor' in xde_dict:
        ges_dict['refc'] = []
        for strs in xde_dict['coor']: 
            ges_dict['refc'].append('r'+strs)

        ges_dict['coor'] =  xde_dict['coor'].copy()

    if 'coef' in xde_dict:
        ges_dict['coef'] =  xde_dict['coef'].copy()

    # 3 parse func declare
    if 'func' in xde_dict:
        ges_dict['func'] =  xde_dict['func'].copy()

    # 4 parse dord and node declare
    if 'disp' in xde_dict:
        ges_dict['dord'] = ''
        for strs in xde_dict['disp']: 
            ges_dict['dord'] += '1'+','

        ges_dict['node'] = str(ges_info['shap_nodn'])

    # 5 parse mate line
    if 'mate' in xde_dict:
        ges_dict['mate'] = xde_dict['mate'].copy()

    # 9 parse shap and tran paragraph
    if 'shap' in xde_dict:
        parse_shap_tran(pfelacpath, ges_info, xde_dict, ges_dict)

    # 9 parse coef shap
    if 'coef_shap' in xde_dict:
        parse_coefshap(pfelacpath, ges_info, xde_dict, ges_dict)

    # 10 parse gaus paragraph
    if 'gaus' in xde_dict:
        parse_gaus(pfelacpath, ges_info, xde_dict, ges_dict)

    # 11 parse stif, mass, damp paragraph
    for weak in ['stif', 'mass', 'damp']:
        if weak in xde_dict:
            parse_weak(weak, xde_dict, ges_dict)

    # 12 parse load paragraph
    if 'load' in xde_dict:
        parse_load(xde_dict, ges_dict)

    return False
# end xde2ges()

def release_code(xde_dict, code_place, pfelacpath, ges_dict):
    
    for code_strs in xde_dict['code'][code_place]:

        code_regx = regx.match(r'Insr|Tnsr|Cplx|Oprt|Func',code_strs,regx.I)

        if code_regx == None: 
            ges_dict['code'][code_place].append(code_strs+'\n')
            continue

        code_key = code_regx.group()

        # Insert C code
        if  code_key == 'Insr':
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
# end release_code()

def release_tensor_code(code_strs, code_place, xde_dict, ges_dict):

    vect_expr = code_strs.replace('Tnsr_Asgn: ','')

    left_vara, righ_expr = vect_expr.split('=')[:2]
    left_vara, righ_expr = left_vara.strip(), righ_expr.strip().strip(';')

    expr_list = idx_summation(left_vara, righ_expr, xde_dict)

    for expres in expr_list:
        ges_dict['code'][code_place].append('$cc '+expres+';\n')
# end release_tensor_code()

def release_complex_code(code_strs, code_place, xde_dict, ges_dict):

    cplx_expr = code_strs.replace('Cplx_Asgn: ','')
    left_vara, righ_expr = cplx_expr.split('=')[:2]
    left_vara, righ_expr = left_vara.strip(), righ_expr.strip().strip(';')

    # if complex expres is a tensor expres, make summation first
    if left_vara.find('_') != -1 \
    or righ_expr.find('_') != -1 :

        expr_list = idx_summation(left_vara, righ_expr, xde_dict)

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
                .append(f'$cc {left_vara}{ri}={cmplexpr};\n')
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
        left_vara, righ_expr = oprt_expr.split('=')[:2]
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
            for vara in oprt_vars:
                if vara.count('_') == 0:
                    temp_vars.append(vara)
                elif vara.count('_') == 1:
                    vect_name = vara.split('_')[0]
                    temp_vars += xde_dict['vect'][vect_name][1:]
                elif vara.count('_') == 2:
                    matr_name = vara.split('_')[0]
                    for matr_row in xde_dict['matrix'][matr_name][2:]:
                        temp_vars += matr_row
            oprt_vars = temp_vars.copy()

        # replenish default variables
        else:
            # to deal with oprt_axis of [oz、so、s]
            if   'disp' in xde_dict and left_vara[0] == '[' and left_vara[-1] == ']':
                oprt_vars += xde_dict['coor'] \
                    + xde_dict['disp'][:len(operator_data[oprt_name][oprt_axis]['disp'])]
            elif 'coef' in xde_dict and left_vara[0] != '[' and left_vara[-1] != ']':
                oprt_vars += xde_dict['coor'] \
                    + xde_dict['coef'][:len(operator_data[oprt_name][oprt_axis]['disp'])]

        oprt_strs = operator_data[oprt_name][oprt_axis]['expr']
        oprt_dfvr = operator_data[oprt_name][oprt_axis]['vars']

        # replace default variable by operator variable
        if len(oprt_vars) == len(oprt_dfvr):
            for oprt_var, dflt_var in zip(oprt_vars, oprt_dfvr):
                oprt_strs = oprt_strs.replace(dflt_var,oprt_var)

        # assign to a temporary list type of 'fvect' or 'fmatr' 
        # used for derivative of 'disp' variables in Func_Asgn step
        # Oprt_Asgn: [a] = opr(*,*) ----------- @L opr f a * *
        if  left_vara[0]  == '[' and left_vara[-1] == ']' :
            expr_list = oprt_strs.rstrip().split('\n')

            if left_vara.count('_') == 0: # may be fault tackle
                expres = left_vara.lstrip('[').rstrip(']') + '=' + ''.join(expr_list)
                ges_dict['code'][code_place].append(expres)

            elif left_vara.count('_') == 1:
                var = left_vara.lstrip('[').rstrip(']').split('_')[0]
                for ii in range(len(expr_list)):
                    xde_dict['fvect'][var][ii+1] = expr_list[ii]

            elif left_vara.count('_') == 2:
                var = left_vara.lstrip('[').rstrip(']').split('_')[0]
                row, clm = list(map(int,xde_dict['fmatr'][var][:2]))
                for ii in range(row):
                    for jj in range(clm):
                        xde_dict['fmatr'][var][ii+2][jj] = expr_list[ii*row+jj]

        # assign to derivative of distributed known variables such as last step 'disp' resault
        # Oprt_Asgn: a = opr(*,*) ----------- @L opr [svm] a * *
        elif left_vara[0]  != '[' and  left_vara[-1] != ']' :
            oprt_strs = oprt_strs.replace('[','{').replace(']','}')
            expr_list = oprt_strs.rstrip().split('\n')

            if left_vara.count('_') == 0:
                expres = left_vara.lstrip('[').rstrip(']') + '=' + ''.join(expr_list)
                ges_dict['code'][code_place].append('$cv '+expres)

            elif left_vara.count('_') == 1:
                expres = left_vara.lstrip('[').rstrip(']').split('_')[0]
                if len(xde_dict['vect'][expres]) == len(expr_list)+1:
                    for ii in range(len(expr_list)):
                        ges_dict['code'][code_place] \
                            .append(f"$cv {xde_dict['vect'][expres][ii+1]}={expr_list[ii]}")

            elif left_vara.count('_') == 2:
                expres = left_vara.lstrip('[').rstrip(']').split('_')[0]
                matr_len = int(xde_dict['matrix'][expres][0]) \
                         * int(xde_dict['matrix'][expres][1])
                if matr_len == len(expr_list):
                    ii = 0
                    for lists in xde_dict['matrix'][expres][2:]:
                        for strs in lists:
                            ges_dict['code'][code_place].append(f'$cv {strs}={expr_list[ii]}\n')
                            ii += 1
# end release_operator_code()

def release_funcasgn_code(code_strs, code_place, xde_dict, ges_dict):

    tnsr_expr = code_strs.replace('Func_Asgn: ','')
    left_vara, righ_expr = tnsr_expr.split('=')[:2]
    left_vara, righ_expr = left_vara.strip(), righ_expr.strip()

    # assign the temporary list type of 'fvect' or 'fmatr'
    # to the list type of 'vect' or 'matrix'
    if  left_vara[0]  != '[' and left_vara[-1] != ']' :

        # Func_Asgn: a = b[*,*] --------- @W a b * *
        if regx.search(r'[a-z]+[0-9a-z]*\[([0-9],)*[0-9]?\]',righ_expr,regx.I) != None \
        and righ_expr[-1] == ']':

            # read right variable index list
            righ_vara = righ_expr.split('[')[0]

            if righ_expr[-1] == ']' and righ_expr[-2] == '[':
                
                if   'fvect' in xde_dict \
                and righ_vara in xde_dict['fvect']:
                    righ_idxs = list(range(int(xde_dict['fvect'][righ_vara][0])))
                
                elif 'fmatr' in xde_dict \
                and righ_vara in xde_dict['fmatr']:
                    righ_idxs = list(range(int(xde_dict['fvect'][righ_vara][0]) \
                                          *int(xde_dict['fvect'][righ_vara][1])))
                
                righ_idxs = [x + 1 for x in righ_idxs]
            else:
                righ_idxs = righ_expr.split('[')[1].rstrip(']').split(',')

            if left_vara.count('_') == 0:
                expres = left_vara + '='

                if   'fvect' in xde_dict \
                and righ_vara in xde_dict['fvect']:
                    for idx in righ_idxs:
                        expres += xde_dict['fvect'][righ_vara][int(idx)]
                
                elif 'fmatr' in xde_dict \
                and righ_vara in xde_dict['fmatr']:

                    row, clm = list(map(int,xde_dict['fmatr'][righ_vara][:2]))
                    fmatr = xde_dict['fmatr'][righ_vara][2:]

                    for idx in righ_idxs:
                        expres += fmatr[math.ceil(int(idx)/clm)-1][int(idx)%clm-1]
                
                ges_dict['code'][code_place].append(expres+'\n\n')
            
            elif left_vara.count('_') == 1: 

                left_name = left_vara.split('_')[0]
                expr_list = []
                temp_list = xde_dict['vect'][left_name][1:].copy()

                if len(temp_list) == len(righ_idxs):

                    if   'fvect' in xde_dict and righ_vara in xde_dict['fvect']:
                        for vara, idx in zip(temp_list, righ_idxs):
                            expr_list.append( vara + '=' + \
                                xde_dict['fvect'][righ_vara][int(idx)] + '\n\n')
                    
                    elif 'fmatr' in xde_dict and righ_vara in xde_dict['fmatr']:

                        row,clm = list(map(int,xde_dict['fmatr'][righ_vara][:2]))
                        fmatr   = xde_dict['fmatr'][righ_vara][2:]

                        for vara,idx in zip(temp_list,righ_idxs):
                            expr_list.append(vara + '=' + \
                                fmatr[math.ceil(int(idx)/clm)-1][int(idx)%clm-1] + '\n\n')
                
                ges_dict['code'][code_place] += expr_list

            elif left_vara.count('_') == 2:

                left_name = left_vara.split('_')[0]
                expr_list = []
                matr_len = int(xde_dict['matrix'][left_name][0]) \
                         * int(xde_dict['matrix'][left_name][1])

                temp_list = xde_dict['matrix'][left_name][2:].copy()

                if matr_len == len(righ_idxs):

                    if 'fvect' in xde_dict \
                        and righ_vara in xde_dict['fvect']:

                        idx = 0
                        for lists in temp_list:
                            for vara in lists:
                                idx+=1
                                expr_list.append( vara + '=' + \
                                    xde_dict['fvect'][righ_vara][idx] + '\n\n')

                elif 'fmatr' in xde_dict and righ_vara in xde_dict['fmatr']:

                    row,clm = list(map(int,xde_dict['fmatr'][righ_vara][:2]))
                    fmatr = xde_dict['fmatr'][righ_vara][2:]

                    i = 0
                    for matr_row in temp_list:
                        for matr_vara in matr_row:
                            idx = righ_idxs[i]
                            expr_list.append( matr_vara + '=' + \
                                fmatr[math.ceil(int(idx)/clm)-1][int(idx)%clm-1] + '\n\n')
                            i += 1

                ges_dict['code'][code_place] += expr_list

    # assign the temporary list type of 'fvect' or 'fmatr'
    # to the list type of 'fvect' or 'fmatr'
    elif left_vara[0]  == '[' \
    and  left_vara[-1] == ']' :

        left_vara = left_vara.lstrip('[').rstrip(']')

        # Func_Asgn: [a] = b[*,*] --------- @S a b * *
        if regx.search(r'[a-z]+[0-9a-z]*\[([0-9],)*[0-9]?\]',righ_expr,regx.I) != None \
        and righ_expr[-1] == ']':

            # read right variable index list
            righ_vara = righ_expr.split('[')[0]

            if righ_expr[-1] == ']' \
            and righ_expr[-2] == '[':

                if 'fvect' in xde_dict \
                and righ_vara in xde_dict['fvect']:
                    righ_idxs = list(range(int(xde_dict['fvect'][righ_vara][0])))

                elif 'fmatr' in xde_dict \
                and righ_vara in xde_dict['fmatr']:
                    righ_idxs = list(range(int(xde_dict['fvect'][righ_vara][0]) \
                                          *int(xde_dict['fvect'][righ_vara][1])))

                righ_idxs = [x + 1 for x in righ_idxs]

            else:
                righ_idxs = righ_expr.split('[')[1].rstrip(']').split(',')

            if left_vara.count('_') == 0:       
                expres = left_vara + '='

                if   'fvect' in xde_dict \
                and righ_vara in xde_dict['fvect']:
                    for idx in righ_idxs:
                        expres += xde_dict['fvect'][righ_vara][int(idx)]

                elif 'fmatr' in xde_dict \
                and righ_vara in xde_dict['fmatr']:

                    row, clm = list(map(int,xde_dict['fmatr'][righ_vara][:2]))
                    fmatr = xde_dict['fmatr'][righ_vara][2:]

                    for idx in righ_idxs:
                        expres += fmatr[math.ceil(int(idx)/clm)-1][int(idx)%clm-1]

                ges_dict['code'][code_place].append(expres+'\n\n')

            elif left_vara.count('_') == 1: 
                left_name = left_vara.split('_')[0]
                vect_len  = len(xde_dict['fvect'][left_name])

                if vect_len == len(righ_idxs) + 1:

                    if   'fvect' in xde_dict \
                    and righ_vara in xde_dict['fvect']:

                        for idx,ii in zip(righ_idxs,range(vect_len)):
                            xde_dict['fvect'][left_name][ii+1] = \
                            xde_dict['fvect'][righ_vara][int(idx)]

                    elif 'fmatr' in xde_dict \
                    and righ_vara in xde_dict['fmatr']:

                        row, clm = list(map(int,xde_dict['fmatr'][righ_vara][:2]))
                        for idx,ii in zip(righ_idxs,range(vect_len)):
                            xde_dict['fvect'][left_name][ii+1] = \
                            xde_dict['fmatr'][righ_vara][math.ceil(int(idx)/clm)+1][int(idx)%clm-1]
            
            elif left_vara.count('_') == 2:

                left_name = left_vara.split('_')[0]
                expr_list = []
                matr_len = int(xde_dict['fmatr'][left_name][0]) \
                         * int(xde_dict['fmatr'][left_name][1])
                lrow, lclm = list(map(int,xde_dict['fmatr'][left_name][:2]))

                if matr_len == len(righ_idxs):
                    if   'fvect' in xde_dict \
                    and righ_vara in xde_dict['fvect']:

                        for ii,idx in zip(range(matr_len),righ_idxs):
                            xde_dict['fmatr'][left_name][math.ceil(ii/lclm)+1][ii%lclm-1] = \
                                xde_dict['fvect'][righ_vara][int(idx)]

                    elif 'fmatr' in xde_dict \
                    and righ_vara in xde_dict['fmatr']:

                        row, clm = list(map(int,xde_dict['fmatr'][righ_vara][:2]))
                        for ii,idx in zip(range(matr_len),righ_idxs):
                            xde_dict['fmatr'][left_name][math.ceil(ii/lclm)+1][ii%lclm-1] = \
                                xde_dict['fmatr'][righ_vara][math.ceil(int(idx)/clm)+1][int(idx)%clm-1]

        else:
            righ_expr = righ_expr.replace('[','').replace(']','')

            expr_list = idx_summation(left_vara,righ_expr,xde_dict)

            if left_vara.count('_') == 1:

                left_vara = left_vara.split('_')[0]
                row = int(xde_dict['fvect'][left_vara][0])

                for ii in range(row):
                    xde_dict['fvect'][left_vara][ii+1] = \
                        expr_list[ii].split('=')[1].replace('++','+').replace('-+','-')

            elif left_vara.count('_') == 2:

                left_vara = left_vara.split('_')[0]
                row,clm = list(map(int,xde_dict['fmatr'][left_vara][:2]))

                for ii in range(row):
                    for jj in range(clm):
                        xde_dict['fmatr'][left_vara][ii+2][jj] = \
                            expr_list[ii*row+jj].split('=')[1].replace('++','+').replace('-+','-')
# end release_funcasgn_code()

def parse_disp_var(ges_info, xde_dict, ges_dict):

    # 1.1 parse disp
    ges_dict['disp'] = xde_dict['disp'].copy()

    # 1.2 parse var
    ges_dict['var'] = []
    var_dict = {}
    pan_vars = set()

    for shap in xde_dict['shap'].keys():

        if shap[-1] == 'c':
            pan_vars |= set(xde_dict['shap'][shap])
            continue

        nodn = int(regx.search(r'[1-9]+', shap, regx.I).group())
        
        for var in xde_dict['shap'][shap]:
            var_dict[var] = [var+str(ii+1) for ii in range(nodn)]

    disp_vars = xde_dict['disp'].copy()

    for pan_var in pan_vars:
        disp_vars.remove(pan_var)

    for nodi in range(int(ges_info['shap_nodn'])):

        for strs in disp_vars:
            if nodi >= len(var_dict[strs]):
                continue

            ges_dict['var'].append(var_dict[strs][nodi])
# end parse_disp_var()

def parse_shap_tran(pfelacpath, ges_info, xde_dict, ges_dict):

    geslib_coor = ['x','y','z']
    base_shap_strs = ''
    base_shap_type = list(xde_dict['shap'].keys())[0]
    #base_shap_nodn = regx.search(r'[1-9]+',base_shap_type,regx.I).group()
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

            ges_dict['shap'][shap_var] = temp_strs+'\n'

    # 9.2 push tran
    ges_dict['tran'] = {}
    shap_expr_list = base_shap_strs.split('\n')
    shap_expr_list.remove('')
    tran_expr_list = []

    # 9.2.1 add '()'
    for shap_expr in shap_expr_list:
        shap_var,shap_exp = shap_expr.split('=')[:2]
        shap_num = regx.search(r'[0-9]+', shap_var, regx.I).group()
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
            ges_dict['tran'][coor_str].append(tran_expr.replace('u', coor_str) + '\n')
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
            shap_num  = regx.search(r'[0-9]+', shap_var, regx.I).group()
            shap_var  = shap_var.replace(shap_num, '('+shap_num+')')
            coef_expr_list.append(shap_var + '=' + shap_exp)

        shap_strs = '\n'.join(coef_expr_list)+'\n'

        # 9.3.2 replace shap func's coor by xde's coor
        for coor_i,coor_str in enumerate(xde_dict['coor']):
            shap_strs = shap_strs.replace(geslib_coor[coor_i],'r'+coor_str)

        # 9.3.3 replace shap func's disp by xde's disp and write
        for shap_var in xde_dict['coef_shap'][shap]:
            temp_string = shap_strs.replace('u', shap_var)
            ges_dict['coef_shap'][shap_var] = temp_string+'\n'
# end parse_coefshap()

def parse_gaus(pfelacpath, ges_info, xde_dict, ges_dict):

    ges_dict['gaus'] = ''
    # 9.1 Gaussian integral
    if xde_dict['gaus'][0] == 'g':

        gaus_degree = regx.search(r'[0-9]+',xde_dict['gaus'],regx.I).group()

        # 9.1.1 line square or cube shap
        if ges_info['shap_form'].lower() in ['l','q','c']:

            gaus_axis = []
            gaus_weit = []

            for line in gaussian_data['line'][gaus_degree].rstrip().split('\n'):
                gaus_strs = line.split()

                if  gaus_strs[0][0] not in ['-' ,'+'] :
                    gaus_strs[0] = ' '+gaus_strs[0]

                gaus_axis.append(gaus_strs[0])
                gaus_weit.append(gaus_strs[1])

            # 9.1.1.2 write line square or cube's gaussian integra
            ges_dict['gaus'] += 'gaus = ' \
                             + str(len(gaus_weit)**int(ges_info['dim'])) + '\n'

            if  ges_info['shap_form'].lower()=='l':
                for axis_i in range(len(gaus_axis)):
                    ges_dict['gaus'] += gaus_axis[axis_i]+' ' \
                                     +  gaus_weit[axis_i]+'\n'

            elif ges_info['shap_form'].lower()=='q':
                for axis_i in range(len(gaus_axis)):
                    for axis_j in range(len(gaus_axis)):
                        weight = float(gaus_weit[axis_i]) \
                                *float(gaus_weit[axis_j])
                        ges_dict['gaus'] += gaus_axis[axis_i]+' ' \
                                         +  gaus_axis[axis_j]+' ' \
                                         +  str(weight)+'\n'
                                        
            elif ges_info['shap_form'].lower()=='c':
                for axis_i in range(len(gaus_axis)):
                    for axis_j in range(len(gaus_axis)):
                        for axis_k in range(len(gaus_axis)):
                            weight = float(gaus_weit[axis_i]) \
                                    *float(gaus_weit[axis_j]) \
                                    *float(gaus_weit[axis_k])
                            ges_dict['gaus'] += gaus_axis[axis_i]+' ' \
                                             +  gaus_axis[axis_j]+' ' \
                                             +  gaus_axis[axis_k]+' ' \
                                             +  str(weight)+'\n'

        # 9.1.2 triangle shap
        elif ges_info['shap_form'].lower()=='t':

            # 9.1.2.1 tackle the gaussian degree
            if gaus_degree == '6':
                gaus_degree = '5'

            elif int(gaus_degree) > 12 and int(gaus_degree) < 17:
                gaus_degree = '12'

            elif int(gaus_degree) > 17:
                gaus_degree = '17'

            ges_dict['gaus'] += gaussian_data['triangle'][gaus_degree]

        # 9.1.3 tetrahedron shap
        elif ges_info['shap_form'].lower()=='w':

            # 9.1.3.1 tackle the gaussian degree
            if gaus_degree == '4':
                gaus_degree = '3'

            elif gaus_degree == '6':
                gaus_degree = '5'

            elif int(gaus_degree) > 7:
                gaus_degree = '7'

            ges_dict['gaus'] += gaussian_data['tetrahedron'][gaus_degree]

        else: pass

    # 9.2 node integral
    else:
        shap_name = 'd'+ges_info['dim']+ges_info['shap_form']+ges_info['shap_nodn']
        ges_dict['gaus'] += shapfunc_data['gau'][shap_name]['expr']
# end parse_gaus()

def write_func(ges_dict, xde_dict, gesfile):

    gesfile.write('\nfunc\n')

    if 'vol'  in xde_dict :
        gesfile.write(xde_dict['vol'])

    if 'func' in ges_dict['code']:
        for strs in ges_dict['code']['func']:

            if strs[0] == '$':
                gesfile.write(strs)

            else:
                if strs.find('(') != -1:
                    strs = strs.rstrip('\n')
                    
                    # save derivative in driv_list[] and replace by rplc_list[]
                    driv_list = set(regx.findall(r'\[[a-z][a-z0-9]*/[xyzros]\]', strs, regx.I))
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

                    left_vara, righ_expr = strs.rstrip('\n').split('=')
                    cmplx_var = []
                    cmplx_var.append(left_vara.strip())
                    vara_list = regx.findall(r'\[\w+/?\w*\]', righ_expr, regx.I)

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
        ges_dict[weak] = ''

    else: 
        return

    if xde_dict[weak][0] == 'dist':

        left_vara = xde_dict[weak][0]
        righ_expr = ''

        for weak_strs in xde_dict[weak][1:]:
            righ_expr += weak_strs

        expr_list = idx_summation(left_vara,righ_expr,xde_dict)
        expr_list = split_bracket_expr(expr_list[0])
        ges_dict[weak] += expr_list[0]

        for strs in expr_list[1:]:

            if 'cmplx_tag' in xde_dict and xde_dict['cmplx_tag'] == 1:

                weak_item = regx.search(r'\[\w+\;\w+\]', strs, regx.I)
                cplx_item = regx.search(r'\(?\|[+-]?\w+\;[+-]?\w+\|\)?', strs, regx.I)

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
                    if regx.match(r'[+-]?0(?:\.0*)?|[+-]?\.0+', cplx_list[i] ,regx.I) != None \
                    and cplx_list[i][-1] == '0' : 
                        continue

                    ges_dict[weak] += strs.replace(weak_item, f'[{weak_left_list[i]};{weak_righ_list[i]}]') \
                                          .replace(cplx_item, f'({cplx_list[i]})') + '\n'
                
            else: ges_dict[weak] += strs+'\n'

    elif xde_dict[weak][0] == 'lump':

        if len(xde_dict[weak]) == 1:
            xde_dict[weak].append('1.0')

        if len(xde_dict[weak]) == 2: pass

        ges_dict[weak] += 'lump =\n'
        for shaps in xde_dict['shap']:
            nodn = regx.search(r'\d+',shaps,regx.I).group()

            for vara in xde_dict['shap'][shaps]:
                for ii in range(int(nodn)):
                    ges_dict[weak] += f'+[{xde_dict[weak][1]}]{vara}{ii+1}\n'
# end parse_weak()

def parse_load(xde_dict, ges_dict):

    ges_dict['load'] = ''

    left_vara = 'load'
    righ_expr = ''.join(xde_dict['load'])
    expr_list = idx_summation(left_vara,righ_expr,xde_dict)
    expr_list = split_bracket_expr(expr_list[0])
    ges_dict['load'] += expr_list[0]

    for strs in expr_list[1:]:

        if 'cmplx_tag' in xde_dict and xde_dict['cmplx_tag'] == 1:

            weak_item = regx.search(r'\[\w+\]', strs, regx.I)
            cplx_item = regx.search(r'\(?\|[+-]?\w+\;[+-]?\w+\|\)?', strs, regx.I)

            if weak_item != None: 
                weak_item = weak_item.group()

            if cplx_item != None: 
                cplx_item = cplx_item.group()

            weak_var = weak_item.lstrip('[').rstrip(']')
            cplx_real_var, cplx_imag_var = cplx_item.lstrip('(').rstrip(')').strip('|').split(';')

            weak_list = [weak_var+'r',  weak_var+'i']
            cplx_list = [cplx_real_var, cplx_imag_var]

            for i in range(2):

                if regx.match(r'[+-]?0(?:\.0*)?|[+-]?\.0+', cplx_list[i] ,regx.I) != None \
                and cplx_list[i][-1] == '0' :
                    continue

                ges_dict['load'] += strs.replace(weak_item, f'[{weak_list[i]}]') \
                                        .replace(cplx_item, f'({cplx_list[i]})') + '\n'

        else: ges_dict['load'] += strs + '\n'
# end parse_load() 

def xde2ges(ges_info, xde_dict, xde_addr, gesfile):

    error = xde2ges_dict(ges_info, xde_dict, xde_addr, gesfile)

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
        for strs in ges_dict['func']: 
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
            gesfile.write(strs)

    if 'singular' in xde_dict:
        gesfile.write(xde_dict['singular'])

    # 8 write shap and tran paragraph
    if 'shap' in ges_dict:
        gesfile.write('\nshap\n')
        for disp_var in ges_dict['shap'].keys():
            gesfile.write(disp_var+'=\n')
            gesfile.write(ges_dict['shap'][disp_var])

    if 'tran' in ges_dict:
        gesfile.write('tran\n')
        for coor_str in ges_dict['tran'].keys():
            gesfile.write(coor_str+'=\n')
            for strs in ges_dict['tran'][coor_str]:
                gesfile.write(strs)
            gesfile.write('\n')

    # 9 write coef shap paragraph
    if 'coef_shap' in ges_dict:
        gesfile.write('coef\n')
        for disp_var in ges_dict['coef_shap'].keys():
            gesfile.write(disp_var+'=\n')
            gesfile.write(ges_dict['coef_shap'][disp_var])

    # 10 write gaus paragraph
    if 'gaus' in ges_dict:
        gesfile.write(ges_dict['gaus'])

    # 11 write func paragraph
    if 'func' in ges_dict['code'] \
    or 'vol'  in xde_dict :
        write_func(ges_dict, xde_dict, gesfile)

    # 12 write stif, mass, damp paragraph
    for weak in ['stif', 'mass', 'damp']:
        if weak in ges_dict:

            gesfile.write(f'\n{weak}\n')

            if weak in ges_dict['code']:
                for strs in ges_dict['code'][weak]:
                    gesfile.write(strs)
            
            gesfile.write(ges_dict[weak])

    # 13 write load paragraph
    if 'load' in ges_dict:
        gesfile.write('\n')
        gesfile.write(ges_dict['load'])

    gesfile.write('\nend')

    gesfile.close()

    return error
# end xde2ges()

def write_disp_var(ges_info, ges_dict, gesfile):

    # 1.1 write disp declare
    gesfile.write('disp ')
    for strs in ges_dict['disp']:
        gesfile.write(strs+',')
    gesfile.write('\n')

    # 1.2 write var declare
    gesfile.write('var')
    i = 0
    for strs in ges_dict['var']:

        gesfile.write(' '+strs)
        i += 1
 
        if i == 10:
            gesfile.write('\nvar')
            i = 0
# end parse_disp_var()
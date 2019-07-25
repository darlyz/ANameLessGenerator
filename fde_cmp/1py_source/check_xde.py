'''
 Copyright: Copyright (c) 2019
 Created: 2019-4-28
 Author: Zhang_Licheng
 Title: check the xde file
 All rights reserved
'''
from colorama import init, Fore, Back, Style
init(autoreset=True)
Error_color = Fore.MAGENTA
Warnn_color = Fore.CYAN
Empha_color = Fore.GREEN
color = {'Error': Error_color, \
         'Warn' : Warnn_color, \
         'Empha': Empha_color}

import re
import os

from felac_data import operator_data, oprt_name_list,\
                       shapfunc_data, shap_name_list

from expr import split_bracket_expr

error = False

def check_xde(ges_info, xde_dict, xde_addr):

    # check disp
    if 'disp' in xde_dict:
        pass
    else:
        error_type  = not_declared('DISP', 'Error')
        sgest_info  = "May be declared as 'DISP * *' in the first garaph, " \
                    + "and '* *' could be referened in 'mdi' file.\n"
        report_error('DND01', '*', error_type + sgest_info)

    # check coor
    if 'coor' in xde_dict: pass
        #xde_axi       =  ''.join(xde_dict['coor'])
        #xde_coor_strs = ' '.join(xde_dict['coor'])
        #if ext_name not in ['fde','cde','vde',pde'] and xde_axi != axi :
        #    addon_info    = "'{}' is not consistent with '{}' " \
        #                  .format(xde_coor_strs,axi)
        #    addon_info += "declared by mdi file.\n"
        #    error_form(line_num, '', addon_info)
    else:
        error_type  = not_declared('COOR', 'Error')
        sgest_info  = "May be declared as 'COOR {}' " \
                      .format(' '.join(list(ges_info['axi']))) \
                    + "in the first garaph.\n"
        report_error('CND01', '*', error_type + sgest_info)

    # check shap
    if 'shap' in xde_dict:
        check_shap(ges_info, xde_dict, xde_addr)
    else:
        error_type  = not_declared('SHAP', 'Error')
        sgest_info  = "Shap function may be declared as " \
                    + "'SHAP %1 %2' in the first garaph."
        report_error('SND01', '*', error_type + sgest_info)

    # check gaus
    if 'gaus' in xde_dict:
        pass
    else:
        error_type  = not_declared('GAUS', 'Error')
        sgest_info  = "gauss integral may be declared as " \
                    + "'GAUS %3' in the first garaph."
        report_error('GND01', '*', error_type + sgest_info)

    # check insert code
    c_declares = {}
    check_code(ges_info, xde_dict, xde_addr, c_declares)

    # check mate
    if 'mate' in xde_dict:
        for var in xde_dict['mate']:
            if re.match(r'\^?[a-z]\w*(?:\[\d\])*', var, re.I) != None :
                if check_variable_declared(var, 'BFmate', c_declares, xde_addr):
                    continue
                line_num   = xde_addr['mate']
                error_type = not_declared(var, 'Error')
                report_error('MND01', line_num, error_type + '\n')

    # check vect
    if 'vect' in xde_dict:
        for vect in xde_dict['vect'].keys():
            for strs in xde_dict['vect'][vect]:
                for var in re.findall(r'\^?[a-z]\w*(?:\[\d\])*', strs, re.I):
                    if check_variable_declared(var, 'all', c_declares, xde_addr):
                        continue
                    line_num   = xde_addr['vect'][vect]
                    error_type = not_declared(var, 'Error')
                    report_error('VND01', line_num, error_type + '\n')

    # check matrix
    if 'matrix' in xde_dict:
        check_matrix(xde_dict, xde_addr, c_declares)

    # check fvect
    if 'fvect' in xde_dict:
        for name, lists in xde_dict['fvect'].items():
            if len(lists) != 1:
                line_num   = xde_addr['fvect'][name]
                error_type = faultly_declared(name, 'Error')
                sgest_info = f'sugest declare as \'FVECT {name} [len]\'.\n'
                report_error('VFD01', line_num,  error_type + sgest_info)

    # check fmatr
    if 'fmatr' in xde_dict:
        for name, lists in xde_dict['fmatr'].items():
            if len(lists) != 2:
                line_num   = xde_addr['fmatr'][name]
                error_type = faultly_declared(name, 'Error')
                sgest_info = f'sugest declare as \'FMATR {name} [row] [clm]\'.\n'
                report_error('MFD01', line_num, error_type + sgest_info)

    # check stif, mass, damp
    for weak in ['stif','mass','damp']:
        if weak in xde_dict:
            check_weak(xde_dict, xde_addr, weak)

    # check load
    if 'load' in xde_dict:
        check_load(xde_dict, xde_addr)

    print('Error=',error)
    return error
# end check_xde()

def check_shap(ges_info, xde_dict, xde_addr):

    base_shap_dclr_times = 0
    base_shap_line = 0
    shap_node = [['%2','2','3'], \
                 ['%2','3','6'], \
                 ['%2','4','8','9'], \
                 ['%2','4','6','10','18'], \
                 ['%2','8','20','27'] ]
    shap_forms    = ['l','t','q','w','c']
    node_dgree1   = ['2','3','4','4','8']
    node_dgree2   = ['3','6','9','10','27']
    #node_dgree1_5 = ['' ,'' ,'8','' ,'20']

    for shap_list, line_num in zip(xde_dict['shap'], xde_addr['shap']):

        if shap_list[0] == '%1':
            shap_form = ges_info['shap_form']
        else:
            shap_form = shap_list[0]

        if   shap_list[1] == '%2':
             shap_nodn = ges_info['shap_nodn']
        elif shap_list[1] == '%4':
            if shap_form in shap_forms:
                shap_nodn = node_dgree1[shap_forms.index(shap_form)]
        elif shap_list[1] == '%2c':
            shap_nodn = shap_list[1].replace('%2',ges_info['shap_nodn'])
        else:
            shap_nodn = shap_list[1]

        if shap_form not in shap_forms:
            error_type  = faultly_declared('SHAP', 'Error')
            sgest_info  = "the first variable of shap declaration must to be " \
                        + f"one of {shap_forms}, or '%1'.\n"
            report_error('SFD01', line_num, error_type + sgest_info)

        else:
            # base shap declare
            if len(shap_list) == 2:

                base_shap_dclr_times += 1
                if base_shap_dclr_times > 1 :                  
                    warn_type   = duplicate_declared('base shap', 'Warn')
                    sgest_info  = 'It has been declared at ' \
                                + f'{Empha_color}{base_shap_line}.\n'
                    report_warn('SDD01', line_num, warn_type + sgest_info)

                base_shap_form = shap_form
                if shap_list[1] == '%2':
                      base_shap_node = ges_info['shap_nodn']
                else: base_shap_node = shap_list[1]

                if base_shap_dclr_times == 1:
                    base_shap_line = line_num

                if shap_form in shap_forms:
                    snodn = shap_node[shap_forms.index(shap_form)]
                    if base_shap_node not in snodn:
                        error_type  = faultly_declared('shap', 'Error')
                        sgest_info  = "the second variable of shap declaration" \
                                    + f" is suggested to be one of {snodn}.\n"
                        report_error('SDD03', line_num, error_type + sgest_info)

            # advance shap declare
            elif len(shap_list) >= 3:

                if shap_form != base_shap_form:
                    error_type  = faultly_declared('SHAP', 'Error')
                    sgest_info  = 'the first variable must be same to base shap ' \
                                + f"declared at line {Empha_color}{base_shap_line}"
                    report_error('SFD02', line_num, error_type + sgest_info)

                # sub shap declare using mix element
                if shap_list[1] == '%4' \
                or shap_list[1].isnumeric():

                    vars_list = [var for var in shap_list[2:] if not var.isnumeric()]

                    if len(set(vars_list)) != len(vars_list):
                        report_warn('SDD02', line_num, 'variable duplicated.\n')

                    for var_name in set(vars_list):
                        if 'coef' not in xde_dict:
                            if 'disp' in xde_dict \
                            and var_name not in xde_dict['disp'] :
                                warn_type   = not_declared(var_name, 'Warn')
                                sgest_info  = 'It must be declared in disp.\n'
                                report_warn('SND02', line_num, warn_type + sgest_info)

                        else:
                            if  'disp' in xde_dict \
                            and var_name not in xde_dict['disp'] \
                            and var_name not in xde_dict['coef'] :
                                warn_type   = not_declared(var_name, 'Warn')
                                sgest_info  = 'It must be declared in disp or coef.\n'
                                report_warn('SND03', line_num, warn_type + sgest_info)

                    # base shap is not degree 2 or not coordinate with shap_form
                    base_index = shap_forms.index(base_shap_form)
                    if base_shap_node != node_dgree2[base_index]:
                        error_type  = faultly_declared('SHAP', 'Error')
                        sgest_info  = 'The second variable of base shap must to be ' \
                                    + Empha_color + node_dgree2[base_index] \
                                    + Error_color + '(second order), ' \
                                    + 'since using mix order element.\n'
                        report_error('SFD03', base_shap_line, error_type + sgest_info)

                    # sub shap is not coordinate with base or not coordinate with shap_form
                    if shap_nodn != node_dgree1[base_index]:
                        error_type  = faultly_declared('SHAP', 'Error')
                        sgest_info  = 'The second variable of mixed shap must to be ' \
                                    + Empha_color + node_dgree1[base_index] \
                                    + Error_color + '(first order), ' \
                                    + 'since using mix order element.\n'
                        report_error('SFD04', line_num, error_type + sgest_info)

                # penalty disp var shap declare
                elif shap_list[1] == '%2c' \
                or  (shap_list[1][-1].lower() == 'c' \
                and  shap_list[1][:-1].isnumeric) :

                    for var_comp in shap_list[2:]:
                        if not var_comp.isnumeric():
                            if var_comp.find('_') == -1:
                                error_type  = unsuitable_form(var_comp, 'Error')
                                sgest_info  = "using penalty element, variable group must " \
                                            + "stitch up by '_', and left is penalty disp, " \
                                            + "right is the variable to be sought.\n"
                                report_error('SUF01', line_num, error_type + sgest_info)
                            else:
                                var_name, pan_name = var_comp.split('_')[:2]
                                
                                if 'coef' in xde_dict:
                                    if var_name in xde_dict['coef'] :
                                        warn_type   = faultly_declared(var_name, 'Warn')
                                        sgest_info  = "It must not be declared in 'coef'.\n"
                                        report_warn('SFD05', line_num, warn_type + sgest_info)

                                    elif 'disp' in xde_dict \
                                    and var_name not in xde_dict['disp'] :
                                        warn_type   = faultly_declared(var_name, 'Warn')
                                        sgest_info  = "It must not be declared in 'disp'.\n"
                                        report_warn('SFD06', line_num, warn_type + sgest_info)

                                elif 'disp' in xde_dict \
                                and var_name not in xde_dict['disp'] :
                                    warn_type   = faultly_declared(var_name, 'Warn')
                                    sgest_info  = "It must not be declared in 'disp'.\n"
                                    report_warn('SFD07', line_num, warn_type + sgest_info)

                                if 'disp' in xde_dict and pan_name not in xde_dict['disp'] :
                                    error_type  = faultly_declared(var_comp, 'Error')
                                    sgest_info  = f"{Empha_color}'{pan_name}' " \
                                                + f"{Error_color}must be declared in 'disp.\n"
                                    report_error('SFD08', line_num, error_type + sgest_info)
                                        

                    # base shap is not degree 1 or not coordinate with shap_form
                    base_index = shap_forms.index(base_shap_form)
                    if base_shap_node != node_dgree1[base_index]:
                        error_type  = faultly_declared('SHAP', 'Error')
                        sgest_info  = 'The second variable of base shap must to be ' \
                                    + Empha_color + node_dgree2[base_index] \
                                    + Error_color + '(first order), ' \
                                    + 'since using penalty element.\n'
                        report_error('SFD09', base_shap_line, error_type + sgest_info)

                    # sub shap is not coordinate with base or not coordinate with shap_form
                    if shap_nodn[:-1] != node_dgree1[base_index]:
                        error_type  = faultly_declared('SHAP', 'Error')
                        sgest_info  = 'The second variable of penalty shap must to be ' \
                                    + Empha_color + node_dgree1[base_index] \
                                    + Error_color + '(first order), ' \
                                    + 'since using penalty element.\n'
                        report_error('SFD10', line_num, error_type + sgest_info)

                else:
                    error_type  = faultly_declared('SHAP', 'Error')
                    sgest_info  = f"If it's mix element shap, declare as " \
                                + f"'shap %1 %4 x x ...'; If it's penalty " \
                                + f"element shap, declare as 'shap '%1 %2c x x ...'.\n"
                    report_error('SFD11', line_num, error_type + sgest_info)

            else:
                error_type  = faultly_declared('SHAP', 'Error')
                sgest_info  = f"Shap declaration must have at least " \
                            + f"2 variables as 'SHAP %1 %2'.\n"
                report_error('SFD12', line_num, error_type + sgest_info)

        if not shap_list[1].isnumeric() \
        and shap_list[1][-1] in ['m','a','v','p','e']:
            posfix = 'd' + ges_info['dim'] + shap_form + shap_nodn
            if posfix not in shap_name_list:
                error_type  = faultly_declared('SHAP', 'Error')
                sgest_info  = shap_form + shap_nodn + ' is not a valid shap.\n'
                report_error('SFD13', line_num, error_type + sgest_info)
# end check_shap()

def check_code(ges_info, xde_dict, xde_addr, c_declares):

    # the inner declaration
    inner_declares  = {'tmax','dt','nstep','itnmax','time'} \
                    | {'tolerance','dampalfa','dampbeta'} \
                    | {'it','stop','itn','end'} \
                    | {'imate','nmate','nelem','nvar','nnode'} \
                    | {'ngaus','igaus','det','ndisp','nrefc','ncoor'}

    # gather C declares and check code
    c_declares['all']    = inner_declares.copy()
    c_declares['BFmate'] = inner_declares.copy()
    c_declares['array']  = {}
    c_declares['array']['vect'] = set()
    c_declares['array']['matrix'] = set()

    for strs in ["disp","coef","coor","func"]:
        if strs in xde_dict:
            c_declares['all'] |= set(xde_dict[strs])

    if 'cmplx_tag' in xde_dict and xde_dict['cmplx_tag'] == 1:
        for strs in ['disp', 'func']:
            if strs in xde_dict:
                for var in xde_dict[strs]:
                    c_declares['all'].add(var+'r')
                    c_declares['all'].add(var+'i')

    assist = {}
    for addr in xde_dict["code"].keys():

        assist['stitch'] = ''
        assist['addrss'] = addr
        for code_strs, line_num in zip(xde_dict["code"][addr], xde_addr["code"][addr]):

            code_key = re.match(r'\$C[C6VP]|@[LAWSR]|COMMON|ARRAY',code_strs,re.I)
            if code_key == None: continue
            assist['ckey'] = code_key  = code_key.group()
            assist['lkey'] = lower_key = code_key.lower()

            if lower_key == 'common':
                code_strs = code_strs.replace(code_key,'$cc')+';'

            if lower_key not in ['$cc','$c6'] :
                code_strs = code_strs.replace(code_key,'').lstrip()

            if lower_key[0] == '@':
                code_list = code_strs.split()

            if lower_key in ['$cc','$c6','common'] :
                if gather_declare(code_strs, line_num, assist, c_declares):
                    continue

            elif lower_key == 'array':
                gather_array_declare(code_strs, line_num, assist, c_declares)

            elif lower_key == '$cv':
                check_tensor_assign(code_strs, line_num, xde_dict, c_declares)

            elif lower_key == '$cp':
                check_complex_assign(code_strs, line_num, xde_dict, xde_addr, c_declares)

            elif lower_key == '@l':
                if check_operator(code_strs, code_list, line_num, xde_dict, xde_addr, c_declares):
                    continue

            elif lower_key in ['@w', '@s']:
                check_func_asgn1(code_list, line_num, xde_dict, c_declares, lower_key)

            elif lower_key in ['@a', '@r']:
                check_func_asgn2(code_strs, line_num, xde_dict, c_declares)
# end check_code()

def gather_declare(code_strs, line_num, assist_dict, c_declares):
    # check $cc code
    code_key   = assist_dict['ckey']
    #lower_key  = assist_dict['lkey']
    stitchline = assist_dict['stitch']
    c_dclr_key = r"char|int|long|short|double|float"
    #c_dclr_exp = r"[a-z].*="
    c_func_exp = r"\w+\(.*\)"
    
    #if    code_strs[-1] != ';' and code_strs[-1] != '{' \
    #and code_strs[-1] != '}' and code_strs[-1] != ',':
    #    if len(code_strs) >16:
    #            err_strs = "'"+code_strs[:8]+'...'+code_strs[-8:]+"'"
    #    else: err_strs = "'"+code_strs+"'"
    #    warn_form(line_num, err_strs, "need ';' at the tial.\n")

    code_strs = stitchline + code_strs.replace(code_key,'').lstrip()
    if code_strs[-1] != ';':
        assist_dict['stitch'] = code_strs.replace(code_key,'').lstrip()
        return True    # continue
    else: assist_dict['stitch'] = ''

    # find c declaration sentence and gather the variables
    if re.search(c_dclr_key, code_strs, re.I) != None:

        if re.search(c_func_exp, code_strs, re.I) != None:
            return True   # continue

        code_list = code_strs.split(';')
        code_list.pop()
        
        for sub_strs in code_list:

            if re.search(c_dclr_key, sub_strs.lstrip(), re.I) == None:
                continue

            if re.match(r'static',sub_strs,re.I) != None:
                sub_strs = re.sub(r'static', '', sub_strs, 0, re.I).lstrip()
            sub_strs = re.sub(c_dclr_key, '', sub_strs).lstrip()

            for var in sub_strs.split(','):
                var = var.strip()
                if var.find('=') != -1:
                    var = re.sub(r'=.*', '', var)

                if var.find('[') != -1:
                    idx_list = re.findall(r'\[\d+\]',var,re.I)
                    var = '*'*len(idx_list) + var.split('[')[0].strip()

                c_declares['all'].add(var)
                if assist_dict['addrss'] == 'BFmate':
                    c_declares['BFmate'].add(var)
    else:
        return True
    return False
# end check_common_code()

def gather_array_declare(code_strs, line_num, assist, c_declares):
    
    vara_list = code_strs.replace(assist['ckey'],'').strip().split(',')

    for var_strs in vara_list:
        var_name = var_strs.strip().split('[')[0]
        idx_list = re.findall(r'\[\d+\]',var_strs,re.I)

        if len(idx_list) == 1:

            vect_len  = idx_list[0].lstrip('[').rstrip(']')
            vect_list = [var_name+'['+str(ii+1)+']' for ii in range(int(vect_len))]

            insert_array_declare(c_declares, assist, 'vect', vect_list, var_name)

        elif len(idx_list) == 2:
            
            matr_row  = idx_list[0].lstrip('[').rstrip(']')
            matr_clm  = idx_list[1].lstrip('[').rstrip(']')
            matr_list = [var_name+'['+str(ii+1)+']['+str(jj+1)+']' \
                            for jj in range(int(matr_clm)) \
                                for ii in range(int(matr_row))]

            insert_array_declare(c_declares, assist, 'matrix', matr_list, var_name)
# end gather_array_declare()

def check_tensor_assign(code_strs, line_num, xde_dict, c_declares):

    pattern = re.compile(r'\^?[a-z][a-z0-9]*(?:_[a-z])+',re.I)
    tnsr_list = pattern.findall(code_strs)

    if len(tnsr_list) == 0 and code_strs.find('{') == -1:
        sgest_info = "there is no tensor or derivation of " \
                   + "'coef' variable, need not to use '$CV'.\n"
        report_warn('NSN01', line_num, sgest_info)

    else:
        for tnsr in set(tnsr_list):
            tnsr_name = tnsr.split('_')[0]
            if tnsr.count('_') == 1:

                if ( 'vect' not in xde_dict \
                    or ( 'vect' in xde_dict \
                        and tnsr_name not in xde_dict['vect'] ) ) \
                and tnsr_name not in c_declares['array']['vect']:

                    error_type = not_declared(tnsr_name, 'Error')
                    sgest_info = "It must declared by 'VECT' or 'ARRAY'."
                    report_error('VND02', line_num, error_type + sgest_info)

            elif tnsr.count('_') == 2:

                if ( 'matrix' not in xde_dict \
                    or ( 'matrix' in xde_dict \
                        and tnsr_name not in xde_dict['matrix'] ) ) \
                and tnsr_name not in c_declares['array']['matrix']:

                    error_type = not_declared(tnsr_name, 'Error')
                    sgest_info = "It must declared by 'MATRIX' or 'ARRAY'."
                    report_error('MND02', line_num, error_type + sgest_info)
# end check_tensor_assign()

def check_complex_assign(code_strs, line_num, xde_dict, xde_addr, c_declares):

    pattern = re.compile(r'\^?[a-z]\w*',re.I)
    temp_list = pattern.findall(code_strs)
    tnsr_list, vara_list = [], []

    for var in temp_list:
        if var.find('_') != -1:
            tnsr_list.append(var)
        else: vara_list.append(var)

    if len(vara_list) != 0:
        for var in set(vara_list):

            if var+'r' not in c_declares['all']:
                error_type = not_declared('real of '+var, 'Error')
                report_error('CND02', line_num, error_type + '\n')

            if var+'i' not in c_declares['all']:
                error_type = not_declared('imag of '+var, 'Error')
                report_error('CND03', line_num, error_type + '\n')
                
    if len(tnsr_list) != 0:
        
        check_tensor_assign(code_strs, line_num, xde_dict, c_declares)
        
        for tnsr in set(tnsr_list):

            tnsr_name = tnsr.split('_')[0]

            if tnsr.count('_') == 1:

                if 'vect' in xde_addr \
                and tnsr_name in xde_addr['vect']:
                    tnsr_line = xde_addr['vect'][tnsr_name]
                else:
                    continue

                if ( 'vect' not in xde_dict \
                    or ( 'vect' in xde_dict \
                        and tnsr_name not in xde_dict['vect'] ) ) \
                or tnsr_name in c_declares['array']['vect']:

                    error_type = not_declared(tnsr_name, 'Error')
                    sgest_info = "It must declared by 'VECT'.\n"
                    report_error('VND03', line_num, error_type + sgest_info)

                else:
                    for var in xde_dict['vect'][tnsr_name]: 
                        
                        if var+'r' not in c_declares['all']:
                            Empha_info = f'real of {var} in vector ' \
                                       + f'{tnsr_name}(line {tnsr_line})'
                            error_type = not_declared(Empha_info, 'Error')
                            report_error('CND04', line_num, error_type + '\n')

                        if var+'i' not in c_declares['all']:
                            Empha_info = f'imag of {var} in vector ' \
                                       + f'{tnsr_name}(line {tnsr_line})'
                            error_type = not_declared(Empha_info, 'Error')
                            report_error('CND05', line_num, error_type + '\n')

            elif tnsr.count('_') == 2:

                if ( 'matrix' not in xde_dict \
                    or ( 'matrix' in xde_dict \
                        and tnsr_name not in xde_dict['matrix'] ) ) \
                or tnsr_name in c_declares['array']['matrix']:

                    error_type = not_declared(tnsr_name, 'Error')
                    sgest_info = "It must declared by 'matrix'.\n"
                    report_error('MND03', line_num, error_type + sgest_info)

                else:

                    if  xde_dict['matrix'][tnsr_name][0].isnumeric() \
                    and xde_dict['matrix'][tnsr_name][1].isnumeric() :
                        matrix_list = xde_dict['matrix'][tnsr_name][2:].copy()
                    else:
                        matrix_list = xde_dict['matrix'][tnsr_name].copy()

                    matrix_line_nums = xde_addr['matrix'][tnsr_name][1:].copy()

                    for vars_list, matr_line_num in zip(matrix_list, matrix_line_nums):
                        var_regx = re.compile(r'[a-z][a-z0-9]*',re.I)

                        for var in set(var_regx.findall(vars_list)):

                            if var+'r' not in c_declares['all']:
                                Empha_info = f'real of {var} in matrix ' \
                                           + f'{tnsr_name}(line {matr_line_num})'
                                error_type = not_declared(Empha_info, 'Error')
                                report_error('CND06', line_num, error_type + '\n')

                            if var+'i' not in c_declares['all']:
                                Empha_info = f'imag of {var} in matrix ' \
                                           + f'{tnsr_name}(line {matr_line_num})'
                                error_type = not_declared(Empha_info, 'Error')
                                report_error('CND07', line_num, error_type + '\n')
# end check_complex_assign()

def check_operator(code_strs, code_list, line_num, xde_dict, xde_addr, c_declares):

    # first check length of '@l' code
    oprt_len = len(code_list)
    if oprt_len > 1:
        if code_list[1].lower() != 'n':

            if oprt_len == 2:
                error_type = unsuitable_form(code_strs, 'Error')
                sgest_info = 'not enough information for operator.\n'
                report_error('OUF01', line_num, error_type + sgest_info)
                return True
        else:
            if len(code_list) > 2:
                warn_type  = unsuitable_form(code_strs, 'Warn')
                sgest_info = "useless information after 'n'.\n"
                report_warn('OUF02', line_num, warn_type + sgest_info)
    else:

        error_type = unsuitable_form(code_strs, 'Error')
        sgest_info = 'not enough information for operator.\n'
        report_error('OUF03', line_num, error_type + sgest_info)
        return True

    # check the operator in 'pde.lib' if or not
    if code_list[0].find('.') == -1:
        error_type = unsuitable_form(code_list[0], 'Error')
        sgest_info = "operator name form as 'name.axi', such as 'grad.xyz'.\n"
        report_error('OUF04', line_num, error_type + sgest_info)
        return True

    elif code_list[0].lower() not in oprt_name_list:
        error_type  = unsuitable_form(code_strs, 'Error')
        sgest_info  = Empha_color + code_list[0] \
                    + Error_color + " is not a default operator.\n"
        report_error('OUF05', line_num, error_type + sgest_info)
        return True

    # split operator name, axis, variables
    oprt_name, oprt_deed = map(lambda strs: strs.lower(), code_list[:2])
    oprt_name, oprt_axis = oprt_name.split('.')[:2]
    if oprt_deed != 'n':
        oprt_objt = code_list[2]
    
    # expand the vector in operator variables
    vars_list = []
    if oprt_deed != 'n' \
    and oprt_len > 3:

        for strs in code_list[3:]:

            if   strs.find('_') == -1:
                vars_list.append(strs)
            elif strs.count('_') == 1:
                vector = strs.split('_')[0]

                if 'vect' not in xde_dict \
                    or ( 'vect' in xde_dict \
                        and vector not in xde_dict['vect'] ):

                    error_type = not_declared(vector, 'Error')
                    sgest_info = "It must be declared by 'VECT'.\n"
                    report_error('VND04', line_num, error_type + sgest_info)

                else:
                    vars_list += xde_dict['vect'][vector]

            else:
                error_type = unsuitable_form(strs, 'Error')
                sgest_info = "only vector or scalar can be operator's variable.\n"
                report_error('VND05', line_num, error_type + sgest_info)

    # replenish default variables
    elif oprt_deed != 'n' \
    and oprt_len == 3:

        opr_disp_len = len(operator_data[oprt_name][oprt_axis]['disp'])

        if 'disp' in xde_dict \
        and oprt_deed == 'f':
            vars_list += xde_dict['coor']
            vars_list += xde_dict['disp'][:opr_disp_len]

        elif 'coef' in xde_dict \
        and oprt_deed in ['c','v','m']:
            vars_list += xde_dict['coor']
            vars_list += xde_dict['coef'][:opr_disp_len]

        if   oprt_axis in ['oz', 'so']:
            vars_list.insert(0,'r')
        elif oprt_axis == 's':
            vars_list[0] = 'r'

    # split axis and normal variables
    oprt_axis_list = []
    for strs in vars_list:

        if strs in list('xyzros') \
        or strs in xde_dict['coor']:
            oprt_axis_list.append(strs)
        else:
            break

    oprt_disp_list = vars_list.copy()
    for strs in oprt_axis_list:
        oprt_disp_list.remove(strs)
    
    if oprt_deed != 'n':
        # compare provided axis counting with which in 'pde.lib'
        need_len = len(operator_data[oprt_name][oprt_axis]['axis'])
        provided = len(oprt_axis_list)
        if provided != need_len:
            error_type = unsuitable_form(code_strs, 'Error')
            sgest_info = f"need {need_len} axis but provided {provided}.\n"
            report_error('OUF06', line_num, error_type + sgest_info)


    # warning that operator's axis be not in accordance with 'coor' declaration
    if 'coor' in xde_dict \
    and oprt_axis != ''.join(xde_dict['coor']):
        warn_type   = unsuitable_form(oprt_name+'.'+oprt_axis, 'Warn')
        sgest_info  = f"coordinate of operator {Empha_color}'{oprt_axis}' " \
                    + f"{Warnn_color}is not consistance with 'coor' declaration " \
                    + f"{Empha_color}'{' '.join(xde_dict['coor'])}' {Warnn_color}in line " \
                    + f"{Empha_color}{str(xde_addr['coor'])}, {Warnn_color}" \
                    + "and please make sure that it is necessary to do so.\n"
        report_warn('OUF07', line_num, warn_type + sgest_info)

    if oprt_deed == 'n':
        pass
    elif oprt_deed in ['c','v','m']: 

        # normal variables of operator must be declared in 'COEF'
        if 'coef' not in xde_dict:
            dif_set = set(oprt_disp_list)
        else:
            dif_set = set(oprt_disp_list).difference(set(xde_dict['coef']))

        if len(dif_set) != 0:
            error_type = unsuitable_form(code_strs, 'Error')
            sgest_info = f"'{' '.join(list(dif_set))}' must be declared in 'COEF'.\n"
            report_error('OUF08', line_num, error_type + sgest_info)
        
        # 'c' means resault of operator assigned to scalar (c code declared)
        if oprt_deed == 'c':
            if oprt_objt not in c_declares['all']:
                error_type = not_declared(oprt_objt, 'Error')
                sgest_info = f'it must be declared before line {line_num}.\n'
                report_error('CND08', line_num, error_type + sgest_info)
        
        # 'v' means resault of operator assigned to vector (vect declared)
        elif oprt_deed == 'v':
            if  'vect' in xde_dict \
            and oprt_objt not in xde_dict['vect'] \
            and oprt_objt not in c_declares['array']['vect']:
                error_type = not_declared(oprt_objt, 'Error')
                sgest_info = "it must be declared by 'VECT' or 'ARRAY'.\n"
                report_error('VND06', line_num, error_type + sgest_info)
        
        # 'm' means resault of operator assigned to matrix (matrix declared)
        elif oprt_deed == 'm':
            if  'matrix' in xde_dict \
            and oprt_objt not in xde_dict['matrix'] \
            and oprt_objt not in c_declares['array']['matrix']:
                error_type = not_declared(oprt_objt, 'Error')
                sgest_info = "it must be declared by 'MATRIX' or 'ARRAY'.\n"
                report_error('MND04', line_num, error_type + sgest_info)
    
    # 'f' means resault of operator assigned to fvect or fmatr
    elif oprt_deed == 'f':

        # normal variables of operator must be declared in 'DISP'
        if 'disp' not in xde_dict:
            dif_set = set(oprt_disp_list)
        else:
            dif_set = set(oprt_disp_list).difference(set(xde_dict['disp']))

        if len(dif_set) != 0:
            error_type = unsuitable_form(code_strs, 'Error')
            sgest_info = f"'{' '.join(list(dif_set))}' must be declared in 'DISP'.\n"
            report_error('OUF09', line_num, error_type + sgest_info)

        if  ('fvect' in xde_dict \
            and oprt_objt not in xde_dict['fvect']) \
        and ('fmatr' in xde_dict \
            and oprt_objt not in xde_dict['fmatr']):
            error_type = not_declared(oprt_objt, 'Error')
            sgest_info = "it must be declared by 'FVECT' or 'FMATR'.\n"
            report_error('VND07', line_num, error_type + sgest_info)

    else:
        error_type = unsuitable_form(code_strs, 'Error')
        sgest_info = "first variable of operator must be one of '[n, c, v, m, f]'.\n"
        report_error('OUF10', line_num, error_type + sgest_info)
# end check_operator()

def check_func_asgn1(code_list, line_num, xde_dict, c_declares, atype):
    left_vara, righ_tnsr = code_list[:2]
    left_size, tnsr_size = 0, 0
    tnsr_idxs = code_list[2:]

    if   atype == '@w':
        tvect, tmatr = 'vect', 'matrix'
    elif atype == '@s':
        tvect, tmatr = 'fvect', 'fmatr'

    if   tvect in xde_dict \
    and left_vara in xde_dict[tvect]: 
        pass
    elif tmatr in xde_dict \
    and left_vara in xde_dict[tmatr]:
        pass

    elif left_vara in c_declares['array']['vect']:
        pass
    elif left_vara in c_declares['array']['matrix']:
        pass

    else:
        error_type = not_declared(left_vara, 'Error')
        sgest_info = f"must be declared by {tvect.upper()} or {tmatr.upper()}.\n"
        report_error('VND08', line_num, error_type + sgest_info)

    if  ( ('fvect' in xde_dict \
            and righ_tnsr not in xde_dict['fvect'] ) \
        and ('fmatr' in xde_dict \
            and righ_tnsr not in xde_dict['fmatr'] ) ) \
    or ('fvect' not in xde_dict \
        and 'fmatr' not in xde_dict) :
        error_type = not_declared(righ_tnsr, 'Error')
        sgest_info = "must be declared by 'FVECT' or 'FMATR'.\n"
        report_error('VND09', line_num, error_type + sgest_info)

    if   'fvect' in xde_dict \
    and righ_tnsr in xde_dict['fvect']:
        tnsr_size = int(xde_dict['fvect'][righ_tnsr][0])

    elif 'fmatr' in xde_dict \
    and righ_tnsr in xde_dict['fmatr']:
        tnsr_size = int(xde_dict['fmatr'][righ_tnsr][0]) \
                  * int(xde_dict['fmatr'][righ_tnsr][1])

    dflt_idxs = list(map(str,map(lambda x:x+1, range(tnsr_size))))

    if len(tnsr_idxs) == 0:
        tnsr_idxs = dflt_idxs

    dif_set = set(tnsr_idxs).difference(set(dflt_idxs))

    if len(dif_set) != 0:
        error_type = unsuitable_form(righ_tnsr, 'Error')
        sgest_info = f"the indexs '{' '.join(dif_set)}' " \
                   + f"of '{righ_tnsr}' is out of range.\n"
        report_error('AUF01', line_num, error_type + sgest_info)

    if atype == '@w':

        if   'vect'   in xde_dict \
        and left_vara in xde_dict['vect']:
            left_size = len(xde_dict['vect'][left_vara])
  
        elif 'matrix' in xde_dict \
        and left_vara in xde_dict['matrix']:

            if  xde_dict['matrix'][left_vara][0].isnumeric() \
            and xde_dict['matrix'][left_vara][0].isnumeric() :
                left_size = int(xde_dict['matrix'][left_vara][0]) \
                          * int(xde_dict['matrix'][left_vara][1])

            else:
                left_size = len(xde_dict['matrix'][left_vara]) \
                              *(xde_dict['matrix'][left_vara].count(' ')+1)

    elif atype == '@s':

        if   'fvect' in xde_dict \
        and left_vara in xde_dict['fvect']:
            left_size = int(xde_dict['fvect'][left_vara][0])

        elif 'fmatr' in xde_dict \
        and left_vara in xde_dict['fmatr']:
            left_size = int(xde_dict['fmatr'][left_vara][0]) \
                      * int(xde_dict['fmatr'][left_vara][1])

    if left_size != len(tnsr_idxs):
        error_type = unsuitable_form(left_vara, 'Error')
        sgest_info = f"the size of '{left_vara}' " \
                   + "is not consistent with the right indexs.\n"
        report_error('AUF02', line_num, error_type + sgest_info)
# end check_func_asgn1()

def check_func_asgn2(code_strs, line_num, xde_dict, c_declares):

    left_vara, righ_expr = code_strs.split('=')
    ftnsr_pattern = re.compile(r'\[[a-z][a-z0-9]+(?:_[a-z]+)+\]', re.I)
    tnsr_pattern  = re.compile(r'\^?[a-z][a-z0-9]+(?:_[a-z]+)+' , re.I)
    ftensor_list  = ftnsr_pattern.findall(righ_expr)
    tensor_list   =  tnsr_pattern.findall(righ_expr)
    
    tnsr_dict = {}
    tnsr_dict['vect'] = set()
    tnsr_dict['matr'] = set()

    for tensor in tensor_list:

        if tensor.count('_') > 2:
            error_type = unsuitable_form(tensor, 'Error')
            sgest_info = 'It must be a vector or matrix.'
            report_error('AUF03', line_num, error_type + sgest_info)

        elif tensor.count('_') == 1:
            tnsr_dict['vect'].add(tensor.split('_')[0])

        elif tensor.count('_') == 2:
            tnsr_dict['matr'].add(tensor.split('_')[0])

    tnsr_dict['fvect'] = set()
    tnsr_dict['fmatr'] = set()

    for tensor in ftensor_list:

        if tensor.count('_') == 1:
            tnsr_dict['fvect'].add(tensor.split('_')[0].lstrip('['))

        elif tensor.count('_') == 2:
            tnsr_dict['fmatr'].add(tensor.split('_')[0].lstrip('['))

    tnsr_dict['vect'] = tnsr_dict['vect'].difference(tnsr_dict['fvect'])
    tnsr_dict['matr'] = tnsr_dict['matr'].difference(tnsr_dict['fmatr'])
    
    if left_vara.count('_') > 2:
        error_type = unsuitable_form(left_vara, 'Error')
        sgest_info = 'It must be a vector or matrix.'
        report_error('AUF04', line_num, error_type + sgest_info)

    elif left_vara.count('_') == 1:
        tnsr_dict['fvect'].add(left_vara.strip().split('_')[0])
        
    elif left_vara.count('_') == 2:
        tnsr_dict['fmatr'].add(left_vara.strip().split('_')[0])

    for char in ['','f']:
        for tnsr in ['vect','matr']:
            for var in tnsr_dict[char+tnsr]:

                if  char == '' \
                and tnsr == 'matr':
                    tnsr += 'ix'

                if char+tnsr in xde_dict \
                and var in xde_dict[char+tnsr]:
                    pass
                elif var in c_declares['array'][char+tnsr]:
                    pass
                else:
                    error_type = not_declared(var, 'Error')
                    sgest_info = f"It mast be declared in '{char+tnsr}'."
                    report_error('VND10', line_num, error_type + sgest_info)
# end check_func_asgn2()

def check_matrix(xde_dict, xde_addr, c_declares):

    for matrix in xde_dict['matrix'].keys():

        line_nums = xde_addr['matrix'][matrix].copy()
        matr_name_line = line_nums.pop(0)

        matr_list = [var for var in xde_dict['matrix'][matrix] \
                        if not var.isnumeric()]

        row_lenth = set()

        for row,line_num in zip(matr_list,line_nums):

            row_list = row.split()
            row_lenth.add(len(row_list))

            for strs in row_list:
                for var in re.findall(r'\^?[a-z]\w*(?:\[\d\])*',strs,re.I):

                    if check_variable_declared(var, 'all', c_declares, xde_addr):
                        continue

                    report_error('CND09', line_num, not_declared(var, 'Error') + '\n')

        if xde_dict['matrix'][matrix][0].isnumeric:

            row = xde_dict['matrix'][matrix][0]

            if xde_dict['matrix'][matrix][1].isnumeric:

                clm = xde_dict['matrix'][matrix][1]

                if len(matr_list) != int(row):
                    error_type = faultly_declared(matrix, 'Error')
                    sgest_info = 'The matrix row is not in ' \
                               + 'accordance with which defined.\n'
                    report_error('MFD01', matr_name_line, error_type + sgest_info)

                if int(clm) not in row_lenth:
                    error_type = faultly_declared(matrix, 'Error')
                    sgest_info = 'The matrix column is not in ' \
                               + 'accordance with which defined.\n'
                    report_error('MFD02', matr_name_line, error_type + sgest_info)
            else:
                error_type = faultly_declared(matrix, 'Error')
                sgest_info = 'need to define row and column ' \
                           + 'number at the same time.\n'
                report_error('MFD03', matr_name_line, error_type + sgest_info)

        if len(row_lenth) != 1:
            report_error('MFD04', matr_name_line, faultly_declared(matrix, 'Error') \
                + 'lenth of every row is not equal.\n')
# end check_matrix()

def check_weak(xde_dict, xde_addr, weak):
    
    if   xde_dict[weak][0].lower() == 'null':
        return

    elif xde_dict[weak][0].lower() == 'dist':

        for weak_strs, line_num in zip(xde_dict[weak][1:], xde_addr[weak]):

            for weak_item in split_bracket_expr(weak_strs):

                weak_pattern = re.compile(r'\[?\w+\;?\w+\]|\[\w+\;?\w+\]?', re.I)
                weak_form = set(weak_pattern.findall(weak_item))

                if len(weak_form) != 1:
                    error_type = unsuitable_form(weak_item, 'Error')
                    sgest_info = "one and only one '[*;*]' form in " \
                               + "a lowest priority expression.\n"
                    report_error('WUF01', line_num, error_type + sgest_info)

                else:

                    miss_opr = [weak_opr for weak_opr in ['[',';',']'] \
                                    if weak_item.find(weak_opr) == -1]

                    if len(miss_opr) != 0:
                        error_type = unsuitable_form(weak_item, 'Error')
                        sgest_info = f"It miss {Empha_color}'{' '.join(miss_opr)}'.\n"
                        report_error('WUF02', line_num, error_type + sgest_info)

                weak_func_set = set()

                for wset in weak_form:
                    weak_func_set |= set(map(lambda x:x.lstrip('[').rstrip(']') ,\
                                             wset.split(';')))

                check_weak_items(weak_func_set, weak_item, line_num, xde_dict)

    elif xde_dict[weak][0] == '%1':

        if weak == 'stif':
            error_type = unsuitable_form(' '.join(xde_dict[weak]), 'Error')
            sgest_info = "'STIF' must be declared as paragraph, it is distributed.\n"
            report_error('WUF03', xde_addr[weak][0], error_type + sgest_info)

        coeff_len = len(xde_dict[weak]) - 1

        if 'disp' in xde_dict \
        and coeff_len > 1 \
        and coeff_len < len(xde_dict['disp']):

            no_coeff_var = xde_dict['disp'][coeff_len:]
            no_mass_list = ['0' for i in range(len(no_coeff_var))]

            line_num   = xde_addr[weak][0]
            error_type = unsuitable_form(' '.join(xde_dict[weak]), 'Error')
            sgest_info = f"Not enough '{weak}' coefficient for 'disp' " \
                       + f"declaration at {Empha_color}{xde_addr['disp']}. " \
                       + f"{Error_color}If '{' '.join(no_coeff_var)}' have no " \
                       + f"'mass', it's better declared as {Empha_color}'{weak} " \
                       + f"{' '.join(xde_dict[weak] + no_mass_list)}'.\n"
            report_error('WUF04', line_num, error_type + sgest_info)

    else:
        line_num   = xde_addr[weak][0]
        error_type = faultly_declared(weak, 'Error')
        sgest_info = f"Wrong key word {Empha_color}'{xde_dict[weak][0][:8]}...'\n"
        report_error('WFD01', line_num, error_type + sgest_info)
# end check_weak()

def check_load(xde_dict, xde_addr):

    if not xde_dict['load'][0].isnumeric():

        for weak_strs, line_num in zip(xde_dict['load'], xde_addr['load']):

            for weak_item in split_bracket_expr(weak_strs):

                weak_form = re.findall(r'\[\w+\]?|\[?\w+\]', weak_item, re.I)

                if len(set(weak_form)) != 1:
                    error_type = unsuitable_form(weak_item, 'Error')
                    sgest_info = "one and only one '[*]' form in " \
                               + "a lowest priority expression.\n"
                    report_error('WUF05', line_num, error_type + sgest_info)

                else:
                    miss_opr = [weak_opr for weak_opr in ['[',']'] \
                                    if weak_item.find(weak_opr) == -1]

                    if len(miss_opr) != 0:
                        error_type = unsuitable_form(weak_item, 'Error')
                        sgest_info = f"It miss {Empha_color}'{' '.join(miss_opr)}'.\n"
                        report_error('WUF06', line_num,  error_type + sgest_info)

                weak_func_set = set(map(lambda x: x.lstrip('[').rstrip(']'), weak_form))
                
                check_weak_items(weak_func_set, weak_item, line_num, xde_dict)
# end check_load()

# --------------------------------------------------------------------------------------------------
# ------------------------------------ report in terminal ------------------------------------------
# --------------------------------------------------------------------------------------------------
def report(repr_type):
    def _report(func):
        def __report(SN, line_num, addon_info):
            
            global error
            if repr_type == 'Error':
                error = True

            output  = color[repr_type] + repr_type +f' {SN}: line number ' \
                    + Empha_color + str(line_num) + ', ' \
                    + color[repr_type] + func(SN, line_num, addon_info)
            print(output)
        return __report
    return _report

@report('Error')
def report_error(SN, line_num, addon_info):
    return addon_info

@report('Warn')
def report_warn(SN, line_num, addon_info):
    return addon_info

def faultly_declared(key_word, report_type):
    return f"{Empha_color}'{key_word}' {color[report_type]}is faultly declared. "

def not_declared(key_word, report_type):
    return f"{Empha_color}'{key_word}' {color[report_type]}not be declared. "

def duplicate_declared(key_word, report_type):
    return f"{Empha_color}'{key_word}' {color[report_type]}is a duplicated declaration. "

def unsuitable_form(form_info, report_type):
    if report_type == 'Error': temp_str = 'is'
    else :temp_str = 'may be'
    return f"{Empha_color}'{form_info}' {color[report_type]}{temp_str} not a suitable form. "

# --------------------------------------------------------------------------------------------------
# -------------------------------------- tiny functions --------------------------------------------
# --------------------------------------------------------------------------------------------------
def check_weak_item(weak_func, weak_item, line_num, xde_dict):

    if ('disp' in xde_dict \
        and weak_func in xde_dict['disp']) \
    or ('func' in xde_dict \
        and weak_func in xde_dict['func']):
        pass

    else:
        error_type = unsuitable_form(weak_item, 'Error')
        sgest_info = f"{Empha_color}{weak_func} {Error_color}" \
                   + "must be declared in 'disp' or 'func' line.\n"
        report_error('WUF07', line_num, error_type + sgest_info)
# end check_weak_item()

def check_weak_items(weak_func_set, weak_item, line_num, xde_dict):

    for weak_func in weak_func_set:
        if weak_func.count('_') == 0:
            check_weak_item(weak_func, weak_item, line_num, xde_dict)

        elif weak_func.count('_') == 1:
            if 'vect' in xde_dict:
                for weak in xde_dict['vect'][weak_func.split('_')[0]]:
                    check_weak_item(weak, weak_item, line_num, xde_dict)

        elif weak_func.count('_') == 2:
            if 'matrix' in xde_dict:
                for weak_vect in xde_dict['matrix'][weak_func.split('_')[0]]:
                    if weak_vect.isnumeric() :
                        continue
                    for weak in weak_vect.split():
                        check_weak_item(weak, weak_item, line_num, xde_dict)
# end check_weak_items()

def check_variable_declared(var, addr, c_declares, xde_addr):

    if var in c_declares[addr]:
        return True

    elif var.find('[') != -1:
        idx_list = re.findall(r'\[\d+\]',var,re.I)
        var = '*'*len(idx_list) + var.split('[')[0].strip()

        if var in c_declares[addr]:
            return True

    else:
        return False
# end check_variable()

def insert_array_declare(c_declares, assist, vtype, vlist, var_name):

    c_declares['all'] |= set(vlist)
    c_declares['array'][vtype].add(var_name)

    if assist['addrss'] == 'BFmate':
        c_declares['BFmate'] != set(vlist)
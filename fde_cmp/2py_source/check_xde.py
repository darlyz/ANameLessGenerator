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
color = {'Error': Fore.MAGENTA, 'Warn': Fore.CYAN, 'Empha': Fore.GREEN}

import re as regx
import os

error = False

from felac_data import operator_data
oprt_name_list = [opr_name+'.'+opr_axis \
                    for opr_name in operator_data.keys() \
                        for opr_axis in operator_data[opr_name].keys()]
oprt_dict = operator_data

from felac_data import shapfunc_data
shap_name_list = [ shap_name for shap_name in shapfunc_data['sub'].keys()]

def check_xde(ges_info, xde_lists, list_addr):

    # check disp
    if 'disp' in xde_lists:
        pass
    else:
        error_type  = not_declared('DISP', 'Error')
        sgest_info  = "May be declared as 'DISP * *' in the first garaph, " \
                    + "and '* *' could be referened in 'mdi' file.\n"
        report_error('*', error_type + sgest_info)

    # check coor
    if 'coor' in xde_lists: pass
        #xde_axi       =  ''.join(xde_lists['coor'])
        #xde_coor_strs = ' '.join(xde_lists['coor'])
        #if ext_name not in ['fde','cde','vde',pde'] and xde_axi != axi :
        #    addon_info    = "'{}' is not consistent with '{}' ".format(xde_coor_strs,axi)
        #    addon_info += "declared by mdi file.\n"
        #    error_form(line_num, '', addon_info)
    else:
        error_type  = not_declared('COOR', 'Error')
        sgest_info  = "May be declared as 'COOR {}' " \
                      .format(' '.join(list(ges_info['axi']))) \
                    + "in the first garaph.\n"
        report_error('*', error_type + sgest_info)

    # check shap
    if 'shap' in xde_lists:
        check_shap(ges_info, xde_lists, list_addr)
    else:
        error_type  = not_declared('SHAP', 'Error')
        sgest_info  = "Shap function may be declared as " \
                    + "'SHAP %1 %2' in the first garaph."
        report_error('*', error_type + sgest_info)

    # check gaus
    if 'gaus' in xde_lists:
        pass
    else:
        error_type  = not_declared('GAUS', 'Error')
        sgest_info  = "gauss integral may be declared as " \
                    + "'GAUS %3' in the first garaph."
        report_error('*', error_type + sgest_info)

    # check insert code
    c_declares = {}
    check_code(ges_info, xde_lists, list_addr, c_declares)

    # check mate
    if 'mate' in xde_lists:
        for var in xde_lists['mate']:
            if regx.match(r'\^?[a-z]\w*(?:\[\d\])*', var, regx.I) != None :
                if var in c_declares['BFmate']:
                    continue
                elif var.find('[') != -1:
                    idx_list = regx.findall(r'\[\d+\]',var,regx.I)
                    var = '*'*len(idx_list) + var.split('[')[0].strip()
                    if var in c_declares['BFmate']:
                        continue
                report_error(list_addr['mate'], not_declared(var, 'Error') + '\n')

    # check vect
    if 'vect' in xde_lists:
        for vect in xde_lists['vect'].keys():
            for strs in xde_lists['vect'][vect]:
                for var in regx.findall(r'\^?[a-z]\w*(?:\[\d\])*', strs, regx.I):
                    if var in c_declares['all']:
                        continue
                    elif var.find('[') != -1:
                        idx_list = regx.findall(r'\[\d+\]',var,regx.I)
                        var = '*'*len(idx_list) + var.split('[')[0].strip()
                        if var in c_declares['all']:
                            continue
                    report_error(list_addr['vect'][vect], not_declared(var, 'Error') + '\n')

    # check matrix
    if 'matrix' in xde_lists:
        check_matrix(xde_lists, list_addr, c_declares)

    # check fvect
    if 'fvect' in xde_lists:
        for name, lists in xde_lists['fvect'].items():
            if len(lists) != 1:
                report_error(list_addr['fvect'][name], faultly_declared(name, 'Error') \
                    + f'sugest declare as \'FVECT {name} [len]\'.\n')

    # check fvect
    if 'fmatr' in xde_lists:
        for name, lists in xde_lists['fmatr'].items():
            if len(lists) != 2:
                report_error(list_addr['fmatr'][name], faultly_declared(name, 'Error') \
                    + f'sugest declare as \'FMATR {name} [row] [clm]\'.\n')

    print('Error=',error)
    return error
# end check_xde()

def check_shap(ges_info, xde_lists, list_addr):

    base_shap_dclr_times = 0
    base_shap_line = 0

    for shap_list, line_num in zip(xde_lists['shap'], list_addr['shap']):

        if shap_list[0] == '%1':
            shap_form = ges_info['shap_form']
        else: shap_form = shap_list[0]

        shap_node = [['%2','2','3'], \
                     ['%2','3','6'], \
                     ['%2','4','8','9'], \
                     ['%2','4','6','10','18'], \
                     ['%2','8','20','27'] ]
        shap_forms    = ['l','t','q','w','c']
        node_dgree1   = ['2','3','4','4','8']
        #node_dgree1_5 = ['' ,'' ,'8','' ,'20']
        node_dgree2   = ['3','6','9','10','27']

        if   shap_list[1] == '%2':
             shap_nodn = ges_info['shap_nodn']
        elif shap_list[1] == '%4':
            if shap_form in shap_forms:
                shap_nodn = node_dgree1[shap_forms.index(shap_form)]
        elif  shap_list[1] == '%2c':
              shap_nodn = shap_list[1].replace('%2',ges_info['shap_nodn'])
        else: shap_nodn = shap_list[1]

        if shap_form not in shap_forms:
            error_type  = faultly_declared('SHAP', 'Error')
            sgest_info  = "the first variable of shap declaration must to be " \
                        + f"one of {shap_forms}, or '%1'.\n"
            report_error(line_num, error_type + sgest_info)

        else:
            # base shap declare
            if len(shap_list) == 2:

                base_shap_dclr_times += 1
                if base_shap_dclr_times > 1 :                  
                    warn_type   = duplicate_declared('base shap', 'Warn')
                    sgest_info  = f'It has been declared at {Empha_color}{base_shap_line}.\n'
                    report_warn(line_num,warn_type + sgest_info)

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
                        report_error(line_num, error_type + sgest_info)

            # advance shap declare
            elif len(shap_list) >= 3:

                if shap_form != base_shap_form:
                    error_type  = faultly_declared('SHAP', 'Error')
                    sgest_info  = 'the first variable must be same to base shap ' \
                                + f"declared at line {Empha_color}{base_shap_line}"
                    report_error(line_num, error_type + sgest_info)

                # sub shap declare using mix element
                if shap_list[1] == '%4' or shap_list[1].isnumeric():

                    vars_list = [var for var in shap_list[2:] if not var.isnumeric()]

                    if len(set(vars_list)) != len(vars_list):
                        report_warn(line_num, 'variable duplicated.\n')

                    for var_name in set(vars_list):
                        if 'coef' not in xde_lists:
                            if 'disp' in xde_lists and \
                            var_name not in xde_lists['disp'] :
                                warn_type   = not_declared(var_name, 'Warn')
                                sgest_info  = 'It must be declared in disp.\n'
                                report_warn(line_num, warn_type + sgest_info)

                        else:
                            if  'disp' in xde_lists \
                            and var_name not in xde_lists['disp'] \
                            and var_name not in xde_lists['coef'] :
                                warn_type   = not_declared(var_name, 'Warn')
                                sgest_info  = 'It must be declared in disp or coef.\n'
                                report_warn(line_num, warn_type + sgest_info)

                    # base shap is not degree 2 or not coordinate with shap_form
                    base_index = shap_forms.index(base_shap_form)
                    if base_shap_node != node_dgree2[base_index]:
                        error_type  = faultly_declared('SHAP', 'Error')
                        sgest_info  = 'The second variable of base shap must to be ' \
                                    + Empha_color + node_dgree2[base_index] \
                                    + Error_color + '(second order), ' \
                                    + 'since using mix order element.\n'
                        report_error(base_shap_line, error_type + sgest_info)

                    # sub shap is not coordinate with base or not coordinate with shap_form
                    if shap_nodn != node_dgree1[base_index]:
                        error_type  = faultly_declared('SHAP', 'Error')
                        sgest_info  = 'The second variable of mixed shap must to be ' \
                                    + Empha_color + node_dgree1[base_index] \
                                    + Error_color + '(first order), ' \
                                    + 'since using mix order element.\n'
                        report_error(line_num, error_type + sgest_info)

                # penalty disp var shap declare
                elif shap_list[1] == '%2c' \
                or  (shap_list[1][-1].lower() == 'c' \
                and  shap_list[1][:-1].isnumeric) :

                    for var_comp in shap_list[2:]:
                        if not var_comp.isnumeric():
                            if var_comp.find('_') == -1:
                                report_error(line_num, unsuitable_form(var_comp, 'Error') + \
                                    "using penalty element, variable group must stitch up by '_', " + \
                                        "and left is penalty disp, right is the variable to be sought.\n")
                            else:
                                var_name, pan_name = var_comp.split('_')[:2]
                                
                                if 'coef' in xde_lists:
                                    if var_name in xde_lists['coef'] :
                                        report_warn(line_num, faultly_declared(var_name, 'Warn') \
                                            + "It must not be declared in 'coef'.\n")
                                    elif 'disp' in xde_lists \
                                    and var_name not in xde_lists['disp'] :
                                        report_warn(line_num, faultly_declared(var_name, 'Warn') \
                                            + "It must be declared in 'disp'.\n")
                                elif 'disp' in xde_lists \
                                and var_name not in xde_lists['disp'] :
                                    report_warn(line_num, faultly_declared(var_name, 'Warn') \
                                        + "It must be declared in 'disp'.\n")

                                if 'disp' in xde_lists and pan_name not in xde_lists['disp'] :
                                    report_error(line_num, faultly_declared(var_comp, 'Error') + \
                                        f"{Empha_color}'{pan_name}' {Error_color}must be declared in 'disp.\n")

                    # base shap is not degree 1 or not coordinate with shap_form
                    base_index = shap_forms.index(base_shap_form)
                    if base_shap_node != node_dgree1[base_index]:
                        error_type  = faultly_declared('SHAP', 'Error')
                        sgest_info  = 'The second variable of base shap must to be ' \
                                    + Empha_color + node_dgree2[base_index] \
                                    + Error_color + '(first order), ' \
                                    + 'since using penalty element.\n'
                        report_error(base_shap_line, error_type + sgest_info)

                    # sub shap is not coordinate with base or not coordinate with shap_form
                    if shap_nodn[:-1] != node_dgree1[base_index]:
                        error_type  = faultly_declared('SHAP', 'Error')
                        sgest_info  = 'The second variable of penalty shap must to be ' \
                                    + Empha_color + node_dgree1[base_index] \
                                    + Error_color + '(first order), ' \
                                    + 'since using penalty element.\n'
                        report_error(line_num, error_type + sgest_info)

        if not shap_list[1].isnumeric() \
        and shap_list[1][-1] in ['m','a','v','p','e']:
            if 'd' + ges_info['dim'] + shap_form + shap_nodn not in shap_name_list:
                report_error(line_num, faultly_declared('SHAP', 'Error') + \
                    shap_form + shap_nodn + ' is not a valid shap.')
# end check_shap()

def check_code(ges_info, xde_lists, list_addr, c_declares):

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
        if strs in xde_lists:
            c_declares['all'] |= set(xde_lists[strs])

    assist = {}
    for addr in xde_lists["code"].keys():

        assist['stitch'] = ''
        assist['addrss'] = addr
        for code_strs, line_num in zip(xde_lists["code"][addr], list_addr["code"][addr]):

            code_key = regx.match(r'\$C[C6VP]|@[LAWSR]|COMMON|ARRAY',code_strs,regx.I)
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
                check_tensor_assign(code_strs, line_num, xde_lists, c_declares)

            elif lower_key == '$cp':
                check_complex_assign(code_strs, line_num, xde_lists, list_addr, c_declares)

            elif lower_key == '@l':
                if check_operator(code_list, line_num, xde_lists, list_addr, c_declares):
                    continue

            elif lower_key == '@w':
                check_func_asgn1(code_list, line_num, xde_lists)

            elif lower_key == '@s':
                check_func_asgn2(code_list, line_num, xde_lists)

            elif lower_key == '@a':
                pass

            elif lower_key == '@r':
                pass
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
    if regx.search(c_dclr_key, code_strs, regx.I) != None:
        if regx.search(c_func_exp, code_strs, regx.I) != None:
            return True   # continue

        code_list = code_strs.split(';')
        code_list.pop()
        
        for sub_strs in code_list:

            if regx.search(c_dclr_key, sub_strs.lstrip(), regx.I) == None:
                continue

            if regx.match(r'static',sub_strs,regx.I) != None:
                sub_strs = regx.sub(r'static', '', sub_strs, 0, regx.I).lstrip()
            sub_strs = regx.sub(c_dclr_key, '', sub_strs).lstrip()

            for var in sub_strs.split(','):
                if var.find('=') != -1:
                    var = regx.sub(r'=.*', '', var)

                if var.find('[') != -1:
                    idx_list = regx.findall(r'\[\d+\]',var,regx.I)
                    var = '*'*len(idx_list) + var.split('[')[0].strip()

                c_declares['all'].add(var)
                if assist_dict['addrss'] == 'BFmate':
                    c_declares['BFmate'].add(var)
    else: return True
    return False
# end check_common_code()

def gather_array_declare(code_strs, line_num, assist, c_declares):
    
    vara_list = code_strs.replace(assist['ckey'],'').strip().split(',')

    for var_strs in vara_list:
        var_name = var_strs.strip().split('[')[0]
        idx_list = regx.findall(r'\[\d+\]',var_strs,regx.I)

        if len(idx_list) == 1:

            vect_len  = idx_list[0].lstrip('[').rstrip(']')
            vect_list = [var_name + '[' + str(ii+1) + ']' \
                            for ii in range(int(vect_len))]

            c_declares['all'] |= set(vect_list)
            c_declares['array']['vect'].add(var_name)

            if assist['addrss'] == 'BFmate':
                c_declares['BFmate'] != set(vect_list)

        elif len(idx_list) == 2:
            
            matr_row  = idx_list[0].lstrip('[').rstrip(']')
            matr_clm  = idx_list[1].lstrip('[').rstrip(']')
            matr_list = [var_name+'['+str(ii+1)+']['+str(jj+1)+']' \
                            for jj in range(int(matr_clm)) \
                                for ii in range(int(matr_row))]

            c_declares['all'] |= set(matr_list)
            c_declares['array']['matrix'].add(var_name)

            if assist['addrss'] == 'BFmate':
                c_declares['BFmate'] != set(matr_list)
# end gather_array_declare()

def check_tensor_assign(code_strs, line_num, xde_lists, c_declares):
    pattern = regx.compile(r'\^?[a-z][a-z0-9]*(?:_[a-z])+',regx.I)
    tnsr_list = pattern.findall(code_strs)
    if len(tnsr_list) == 0 and code_strs.find('{') == -1:
        report_warn(line_num,"there is no tensor or derivation of 'coef' variable, need not to use '$CV'.")

    else:
        for tnsr in set(tnsr_list):
            tnsr_name = tnsr.split('_')[0]
            if tnsr.count('_') == 1:
                if  ('vect' in xde_lists and tnsr_name not in xde_lists['vect']) \
                and tnsr_name not in c_declares['array']['vect']:
                    report_error(line_num, not_declared(tnsr_name, 'Error') + \
                        "It must declared by 'VECT' or 'ARRAY'.")
            elif tnsr.count('_') == 2:
                if  ('matrix' in xde_lists and tnsr_name not in xde_lists['matrix']) \
                and tnsr_name not in c_declares['array']['matrix']:
                     report_error(line_num, not_declared(tnsr_name, 'Error') + \
                        "It must declared by 'MATRIX' or 'ARRAY'.")
# end check_tensor_assign()

def check_complex_assign(code_strs, line_num, xde_lists, list_addr, c_declares):
    pattern = regx.compile(r'\^?[a-z]\w*',regx.I)
    temp_list = pattern.findall(code_strs)
    tnsr_list, vara_list = [], []

    for var in temp_list:
        if var.find('_') != -1:
            tnsr_list.append(var)
        else: vara_list.append(var)

    if len(vara_list) != 0:
        for var in set(vara_list):
            if var+'r' not in c_declares['all']:
                report_error(line_num, not_declared('real of '+var, 'Error') + '\n')
            if var+'i' not in c_declares['all']:
                report_error(line_num, not_declared('imag of '+var, 'Error') + '\n')
                
    if len(tnsr_list) != 0:
        
        check_tensor_assign(code_strs, line_num, xde_lists, c_declares)
        
        for tnsr in set(tnsr_list):

            tnsr_name = tnsr.split('_')[0]
            if tnsr_name in list_addr['vect']:
                tnsr_line = list_addr['vect'][tnsr_name]
            else: continue

            if tnsr.count('_') == 1:

                if tnsr_name not in xde_lists['vect'] \
                or tnsr_name in c_declares['array']['vect']:
                    report_error(line_num, not_declared(tnsr_name, 'Error') + \
                        "It must declared by 'VECT'.\n")

                else:
                    for var in xde_lists['vect'][tnsr_name]: 
                        
                        if var+'r' not in c_declares['all']:
                            error_type = not_declared(f'real of {var} in vector {tnsr_name}(line {tnsr_line})', 'Error')
                            report_error(line_num, error_type + '\n')

                        if var+'i' not in c_declares['all']:
                            error_type = not_declared(f'imag of {var} in vector {tnsr_name}(line {tnsr_line})', 'Error')
                            report_error(line_num, error_type + '\n')

            elif tnsr.count('_') == 2:
                if tnsr_name not in xde_lists['matrix'] \
                or tnsr_name in c_declares['array']['matrix']:
                    report_error(line_num, not_declared(tnsr_name, 'Error') + \
                        "It must declared by 'matrix'.\n")
                else:
                    if  xde_lists['matrix'][tnsr_name][0].isnumeric() \
                    and xde_lists['matrix'][tnsr_name][1].isnumeric() :
                        matrix_list = xde_lists['matrix'][tnsr_name][2:].copy()
                    else:
                        matrix_list = xde_lists['matrix'][tnsr_name].copy()

                    matrix_line_nums = list_addr['matrix'][tnsr_name][1:].copy()

                    for vars_list, matr_line_num in zip(matrix_list, matrix_line_nums):
                        var_regx = regx.compile(r'[a-z][a-z0-9]*',regx.I)
                        for var in set(var_regx.findall(vars_list)):
                            if var+'r' not in c_declares['all']:
                                error_type = not_declared(f'real of {var} in matrix {tnsr_name}(line {matr_line_num})', 'Error')
                                report_error(line_num, error_type + '\n')
                            if var+'i' not in c_declares['all']:
                                error_type = not_declared(f'imag of {var} in matrix {tnsr_name}(line {matr_line_num})', 'Error')
                                report_error(line_num, error_type + '\n')
# end check_complex_assign()

def check_operator(code_list, line_num, xde_lists, list_addr, c_declares):

    # first check length of '@l' code
    oprt_len = len(code_list)
    if oprt_len > 1:
        if code_list[1].lower() != 'n':
            if oprt_len == 2:
                report_error(line_num, unsuitable_form('', 'Error') \
                    + 'not enough information for operator.\n')
                return True
        else:
            if len(code_list) > 2:
                report_warn(line_num, unsuitable_form('', 'Warn') \
                    + "useless information after 'n'.\n")
    else:
        report_error(line_num, unsuitable_form('', 'Error') \
            + 'not enough information for operator.\n')
        return True

    # check the operator in 'pde.lib' if or not
    if code_list[0].find('.') == -1:
        report_error(line_num, unsuitable_form('', 'Error') \
            + "operator name form as 'name.axi', such as 'grad.xyz'.\n")
        return True

    elif code_list[0].lower() not in oprt_name_list:
        sgest_info  = Empha_color + code_list[0] \
                    + Error_color + " is not a default operator."
        report_error(line_num, unsuitable_form('', 'Error') + sgest_info)
        return True

    # split operator name, axis, variables
    oprt_name, oprt_deed = map(lambda strs: strs.lower(), code_list[:2])
    oprt_name, oprt_axis = oprt_name.split('.')[:2]
    if oprt_deed != 'n': oprt_objt = code_list[2]
    
    # expand the vector in operator variables
    vars_list = []
    if oprt_deed != 'n' and oprt_len > 3:
        for strs in code_list[3:len(code_list)]:
            if   strs.find('_') == -1:
                vars_list.append(strs)
            elif strs.count('_') == 1:
                vector = strs.split('_')[0]
                if vector not in xde_lists['vect']:
                    report_error(line_num, not_declared(vector, 'Error') + \
                        "It must be declared by 'VECT'.\n")
                else:
                    vars_list += xde_lists['vect'][vector]
            else:
                report_error(line_num, unsuitable_form('', 'Error') + \
                    "only vector or scalar can be operator's variable.\n")

    # replenish default variables
    elif oprt_deed != 'n' and oprt_len == 3:
        if 'disp' in xde_lists and oprt_deed == 'f':
            vars_list += list(oprt_axis) \
                + xde_lists['disp'][:len(oprt_dict[oprt_name][oprt_axis]['disp'])]
        elif 'coef' in xde_lists and oprt_deed in ['c','v','m']:
            vars_list += list(oprt_axis) \
                + xde_lists['coef'][:len(oprt_dict[oprt_name][oprt_axis]['disp'])]

    # split axis and normal variables
    oprt_axis_list = []
    for strs in vars_list:
        if strs in list('xyzros'):
            oprt_axis_list.append(strs)
        else: break

    oprt_disp_list = vars_list.copy()
    for strs in oprt_axis_list:
        oprt_disp_list.remove(strs)
    
    if oprt_deed != 'n':
        # compare provided axis counting with which in 'pde.lib'
        need_len = len(oprt_dict[oprt_name][oprt_axis]['axis'])
        provided = len(oprt_axis_list)
        if provided != need_len: 
            report_error(line_num, unsuitable_form('', 'Error') + f"need {need_len} axis but provided {provided}.\n")


    # warning that operator's axis be not in accordance with 'coor' declaration
    if oprt_axis != ''.join(xde_lists['coor']):
        sgest_info  = f"coordinate of operator {Empha_color}'{oprt_axis}' " \
                    + f"{Warnn_color}is not consistance with 'coor' declaration " \
                    + f"{Empha_color}'{' '.join(xde_lists['coor'])}' {Warnn_color}in line " \
                    + f"{Empha_color}{str(list_addr['coor'])}, {Warnn_color}" \
                    + "and please make sure that it is necessary to do so.\n"
        report_warn(line_num, unsuitable_form('', 'Warn') + sgest_info)

    if oprt_deed == 'n': pass
    elif oprt_deed in ['c','v','m']: 

        # normal variables of operator must be declared in 'COEF'
        if 'coef' not in xde_lists:
            dif_set = set(oprt_disp_list)
        else:
            dif_set = set(oprt_disp_list).difference(set(xde_lists['coef']))
        if len(dif_set) != 0:
            report_error(line_num, unsuitable_form('', 'Error') \
                + f"'{' '.join(list(dif_set))}' must be declared in 'COEF'.\n")
        
        # 'c' means resault of operator assigned to scalar (c code declared)
        if oprt_deed == 'c':
            if oprt_objt not in c_declares['all']:
                report_error(line_num, not_declared(oprt_objt, 'Error') \
                    + f'it must be declared before line {line_num}.\n')
        
        # 'v' means resault of operator assigned to vector (vect declared)
        elif oprt_deed == 'v':
            if  oprt_objt not in xde_lists['vect'] \
            and oprt_objt not in c_declares['array']['vect']:
                report_error(line_num, not_declared(oprt_objt, 'Error') \
                    + "it must be declared by 'VECT' or 'ARRAY'.\n")
        
        # 'm' means resault of operator assigned to matrix (matrix declared)
        elif oprt_deed == 'm':
            if  oprt_objt not in xde_lists['matrix'] \
            and oprt_objt not in c_declares['array']['matrix']:
                report_error(line_num, not_declared(oprt_objt, 'Error') \
                    + "it must be declared by 'MATRIX' or 'ARRAY'.\n")
    
    # 'f' means resault of operator assigned to fvect or fmatr
    elif oprt_deed == 'f':

        # normal variables of operator must be declared in 'DISP'
        if 'disp' not in xde_lists:
            dif_set = set(oprt_disp_list)
        else:
            dif_set = set(oprt_disp_list).difference(set(xde_lists['disp']))
        if len(dif_set) != 0:
            report_error(line_num, unsuitable_form('', 'Error') \
                + f"'{' '.join(list(dif_set))}' must be declared in 'DISP'.\n")

        if  ('fvect' in xde_lists and oprt_objt not in xde_lists['fvect']) \
        and ('fmatr' in xde_lists and oprt_objt not in xde_lists['fmatr']):
            report_error(line_num, not_declared(oprt_objt, 'Error') \
                + "it must be declared by 'FVECT' or 'FMATR'.\n")

    else:
        report_error(line_num, unsuitable_form('', 'Error') \
            + "first variable of operator must be one of '[n, c, v, m, f]'.\n")
# end check_operator()

def check_func_asgn1(code_list, line_num, xde_lists):
    left_vara, righ_tnsr = code_list[:2]
    left_size, tnsr_size = 0,0
    tnsr_idxs = code_list[2:]

    if  ( ('vect'   in xde_lists and left_vara not in xde_lists['vect'] ) \
      and ('matrix' in xde_lists and left_vara not in xde_lists['matrix'] ) ) \
    or ('vect' not in xde_lists and 'matrix' not in xde_lists) :
        report_error(line_num, not_declared(left_vara, 'Error') \
            + "must be declared by 'VECT' or 'MATRIX'.\n")

    if  ( ('fvect' in xde_lists and righ_tnsr not in xde_lists['fvect'] ) \
      and ('fmatr' in xde_lists and righ_tnsr not in xde_lists['fmatr'] ) ) \
    or ('fvect' not in xde_lists and 'fmatr' not in xde_lists) :
        report_error(line_num, not_declared(righ_tnsr, 'Error') \
            + "must be declared by 'FVECT' or 'FMATR'.\n")

    if   'fvect' in xde_lists and righ_tnsr in xde_lists['fvect']:
        tnsr_size = int(xde_lists['fvect'][righ_tnsr][0])
    elif 'fmatr' in xde_lists and righ_tnsr in xde_lists['fmatr']:
        tnsr_size = int(xde_lists['fmatr'][righ_tnsr][0]) \
                  * int(xde_lists['fmatr'][righ_tnsr][1])

    dflt_idxs = list(map(str,map(lambda x:x+1, range(tnsr_size))))
    if len(tnsr_idxs) == 0:
        tnsr_idxs = dflt_idxs
    dif_set = set(tnsr_idxs).difference(set(dflt_idxs))
    if len(dif_set) != 0:
        report_error(line_num, unsuitable_form('', 'Error') \
            + f"the indexs '{' '.join(dif_set)}' of '{righ_tnsr}' is out of range.\n")

    if   'vect'   in xde_lists and left_vara in xde_lists['vect']:
        left_size = len(xde_lists['vect'][left_vara])
    elif 'matrix' in xde_lists and left_vara in xde_lists['matrix']:
        if  xde_lists['matrix'][left_vara][0].isnumeric() \
        and xde_lists['matrix'][left_vara][0].isnumeric() :
            left_size = int(xde_lists['matrix'][left_vara][0]) \
                      * int(xde_lists['matrix'][left_vara][1])
        else:
            left_size = len(xde_lists['matrix'][left_vara]) \
                          *(xde_lists['matrix'][left_vara].count(' ')+1)

    if left_size != len(tnsr_idxs):
        report_error(line_num, unsuitable_form('', 'Error') \
            + f"the size of '{left_vara}' is not consistent with the right indexs.\n")
# end check_func_asgn1()

def check_func_asgn2(code_list, line_num, xde_lists):
    left_vara, righ_tnsr = code_list[:2]
    left_size, tnsr_size = 0,0
    tnsr_idxs = code_list[2:]
    
    if  ( ('fvect' in xde_lists and left_vara not in xde_lists['fvect'] ) \
      and ('fmatr' in xde_lists and left_vara not in xde_lists['fmatr'] ) ) \
    or ('fvect' not in xde_lists and 'fmatr' not in xde_lists) :
        report_error(line_num, not_declared(left_vara, 'Error') \
            + "must be declared by 'FVECT' or 'FMATR'.\n")
    
    if  ( ('fvect' in xde_lists and righ_tnsr not in xde_lists['fvect'] ) \
      and ('fmatr' in xde_lists and righ_tnsr not in xde_lists['fmatr'] ) ) \
    or ('fvect' not in xde_lists and 'fmatr' not in xde_lists) :
        report_error(line_num, not_declared(righ_tnsr, 'Error') \
            + "must be declared by 'FVECT' or 'FMATR'.\n")

    if   'fvect' in xde_lists and righ_tnsr in xde_lists['fvect']:
        tnsr_size = int(xde_lists['fvect'][righ_tnsr][0])
    elif 'fmatr' in xde_lists and righ_tnsr in xde_lists['fmatr']:
        tnsr_size = int(xde_lists['fmatr'][righ_tnsr][0]) \
                  * int(xde_lists['fmatr'][righ_tnsr][1])

    dflt_idxs = list(map(str,map(lambda x:x+1, range(tnsr_size))))
    if len(tnsr_idxs) == 0:
        tnsr_idxs = dflt_idxs
    dif_set = set(tnsr_idxs).difference(set(dflt_idxs))
    if len(dif_set) != 0:
        report_error(line_num, unsuitable_form('', 'Error') \
            + f"the indexs '{' '.join(dif_set)}' of '{righ_tnsr}' is out of range.\n")

    if   'fvect' in xde_lists and left_vara in xde_lists['fvect']:
        left_size = int(xde_lists['fvect'][left_vara][0])
    elif 'fmatr' in xde_lists and left_vara in xde_lists['fmatr']:
        left_size = int(xde_lists['fmatr'][left_vara][0]) \
                  * int(xde_lists['fmatr'][left_vara][1])
    if left_size != len(tnsr_idxs):
        report_error(line_num, unsuitable_form('', 'Error') \
            + f'the size of {left_vara} is not consistent with the right indexs.\n')
# end check_func_asgn2()

def check_matrix(xde_lists, list_addr, c_declares):
    for matrix in xde_lists['matrix'].keys():
        line_nums = list_addr['matrix'][matrix].copy()
        matr_name_line = line_nums.pop(0)

        matr_list = [var \
            for var in xde_lists['matrix'][matrix] \
                if not var.isnumeric()]

        row_lenth = set()
        for row,line_num in zip(matr_list,line_nums):
            row_list = row.split()
            row_lenth.add(len(row_list))
            for strs in row_list:
                for var in regx.findall(r'\^?[a-z]\w*(?:\[\d\])*',strs,regx.I):
                    if var in c_declares['all']:
                        continue
                    elif var.find('[') != -1:
                        idx_list = regx.findall(r'\[\d+\]',var,regx.I)
                        var = '*'*len(idx_list) + var.split('[')[0].strip()
                        if var in c_declares['all']:
                            continue
                    report_error(line_num, not_declared(var, 'Error') + '\n')

        if xde_lists['matrix'][matrix][0].isnumeric:
            row = xde_lists['matrix'][matrix][0]
            if xde_lists['matrix'][matrix][1].isnumeric:
                clm = xde_lists['matrix'][matrix][1]

                if len(matr_list) != int(row):
                    report_error(matr_name_line, faultly_declared(matrix, 'Error') \
                        + 'The matrix row is not in accordance with which defined.\n')
                if int(clm) not in row_lenth:
                    report_error(matr_name_line, faultly_declared(matrix, 'Error') \
                        + 'The matrix column is not in accordance with which defined.\n')
            else:
                report_error(matr_name_line, faultly_declared(matrix, 'Error') \
                    + 'need to define row and column number at the same time.\n')

        if len(row_lenth) != 1:
            report_error(matr_name_line, faultly_declared(matrix, 'Error') \
                + 'lenth of every row is not equal.\n')
# end check_matrix()

def report(repr_type):
    def _report(func):
        def __report(line_num, addon_info):
            
            global error
            if repr_type == 'Error':
                error = True

            output  = color[repr_type] + repr_type +': line number ' \
                    + Empha_color + str(line_num) + ', ' \
                    + color[repr_type] + func(line_num, addon_info)
            print(output)
        return __report
    return _report

@report('Error')
def report_error(line_num, addon_info):
    return addon_info

@report('Warn')
def report_warn(line_num, addon_info):
    return addon_info

def faultly_declared(key_word, report_type):
    return f"{Empha_color}'{key_word}' {color[report_type]}is faultly declared. "

def not_declared(key_word, report_type):
    return f"{Empha_color}'{key_word}' {color[report_type]}not be declared. "

def duplicate_declared(key_word, report_type):
    return f"{Empha_color}'{key_word}' {color[report_type]}is a duplicated declaration. "

def unsuitable_form(form_info, report_type):
    return f"{Empha_color}'{form_info}' {color[report_type]}is not a suitable form. "
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
scalar = 0
vector = 1
matrix = 2

def check_xde(ges_info, xde_dict, xde_addr):

    # check disp
    if 'disp' in xde_dict:
        pass # to check with mdi file
    else:
        error_type  = not_declared('DISP', 'Error')
        sgest_info  = "May be declared as 'DISP * *' in the first garaph, " \
                    + "and '* *' could be referened in 'mdi' file.\n"
        report_error('DSPND', '*', error_type + sgest_info)

    # check coor
    if 'coor' in xde_dict:
        pass # to check with mdi file
    else:
        error_type  = not_declared('COOR', 'Error')
        sgest_info  = "May be declared as 'COOR {}' " \
                      .format(' '.join(list(ges_info['axi']))) \
                    + "in the first garaph.\n"
        report_error('CORND', '*', error_type + sgest_info)

    # check shap
    if 'shap' in xde_dict:
        check_shap(ges_info, xde_dict, xde_addr)
    else:
        error_type  = not_declared('SHAP', 'Error')
        sgest_info  = "Shap function may be declared as " \
                    + "'SHAP %1 %2' in the first garaph."
        report_error('SHPND', '*', error_type + sgest_info)

    # check gaus
    if 'gaus' in xde_dict:
        pass # to check with mdi file
    else:
        error_type  = not_declared('GAUS', 'Error')
        sgest_info  = "gauss integral may be declared as " \
                    + "'GAUS %3' in the first garaph."
        report_error('GASND', '*', error_type + sgest_info)

    # check insert code and gether c code variable declaration
    c_declares = {}
    check_code(ges_info, xde_dict, xde_addr, c_declares)

    # check mate
    if 'mate' in xde_dict:

        var_not_declare = set()
        mate_var_list = []
        mate_val_list = []

        for var in xde_dict['mate']:

            if not is_number(var) :
                mate_var_list.append(var)
                add_var_not_declared(var, c_declares['BFmate'], var_not_declare)

            else:
                mate_val_list.append(var)

        line_num   = xde_addr['mate']

        if len(mate_val_list) > len(mate_var_list):
            sgest_info = f"redundant values, {Empha_color}" \
                       + f"'{','.join(mate_val_list[mate_var_list.index(mate_var_list[-1])+1:])}' " \
                       + f"{Warnn_color}will be discarded.\n"
            report_warn('MWN01',line_num, sgest_info)

        elif len(mate_val_list) < len(mate_var_list):
            sgest_info = f"lack values, {Empha_color}" \
                       + f"'{','.join(mate_var_list[mate_val_list.index(mate_val_list[-1])+1:])}' " \
                       + f"{Warnn_color}will be assigned by {Empha_color}'0.0'.\n"
            report_warn('MWN02',line_num, sgest_info)

        if len(var_not_declare) != 0:
            error_type = not_declared(','.join(var_not_declare), 'Error')
            sgest_info = f"Must be declared befor {line_num}.\n"
            report_error('MND01', line_num, error_type + '\n')
    else:
        error_type  = not_declared('MATE', 'Error')
        sgest_info  = "Material may be declared as " \
                    + "'MATE aa bb ... 1.0 2e2 ...' in the first garaph, "\
                    + "and don't forget insert '$CC double aa,bb,...;' before 'MATE'.\n"
        report_error('MATND', '*', error_type + sgest_info)

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
            check_weak(weak, xde_dict, xde_addr, c_declares)

    # check load
    if 'load' in xde_dict:
        check_load(xde_dict, xde_addr, c_declares)


    # check vect
    if 'vect' in xde_dict:

        vect_not_used = set(xde_dict['vect'].keys()).difference(c_declares['tnsr_used']['vect'])
        vect_not_used_addr = set()
        for vect in vect_not_used:
            vect_not_used_addr.add(str(xde_addr['vect'][vect]))

        if len( vect_not_used )!= 0:
            report_warn('VND01', ','.join(vect_not_used_addr), ','.join(vect_not_used) + ' not used\n')

    # check matrix
    if 'matrix' in xde_dict:
        matr_not_used = set(xde_dict['matrix'].keys()).difference(c_declares['tnsr_used']['matrix'])
        matr_not_used_addr = set()
        for matr in matr_not_used:
            matr_not_used_addr.add(str(xde_addr['matrix'][matr][0]))

        if len( matr_not_used )!= 0:
            report_warn('VND01', ','.join(matr_not_used_addr), ','.join(matr_not_used) + ' not used\n')


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

    # first get base shap declaration check it and check the lack information
    for shap_list, line_num in zip(xde_dict['shap'], xde_addr['shap']):

        # get and check base shap declare
        if len(shap_list) == 2:

            # get the first parameter
            if  shap_list[0] == '%1':
                shap_form = ges_info['shap_form']
            else:
                shap_form = shap_list[0]

            # get and check the second parameter
            if  shap_list[1] == '%2':
                shap_nodn = ges_info['shap_nodn']

            elif shap_list[1] == '%4':
                error_type  = faultly_declared('SHAP', 'Error')
                sgest_info  = "not enough information when using mix order element, " \
                            + "'%4' must be followed by one or more of " \
                            + f"'{','.join(xde_dict['disp'])}' which 'disp' declared.\n"
                report_error('SFD01', line_num, error_type + sgest_info)
                continue

            elif shap_list[1] == '%2c':
                error_type  = faultly_declared('SHAP', 'Error')
                sgest_info  = "not enough information when using penalty element, " \
                            + "'%2c' must be followed by '*_*' and '*' is 'disp' declared.\n"
                report_error('SFD02', line_num, error_type + sgest_info)
                continue

            else:
                shap_nodn = shap_list[1]

            # check the first and second parameter
            if shap_form not in shap_forms:
                error_type  = faultly_declared('SHAP', 'Error')
                sgest_info  = "the first variable of shap declaration must to be " \
                            + f"one of {shap_forms}, or '%1'.\n"
                report_error('SFD03', line_num, error_type + sgest_info)
                continue

            else:
                if shap_nodn not in shap_node[shap_forms.index(shap_form)]:
                    error_type  = faultly_declared('SHAP', 'Error')
                    sgest_info  = "the first variable of shap declaration must to be " \
                                + f"one of {shap_node[shap_forms.index(shap_form)]}.\n"
                    report_error('SFD04', line_num, error_type + sgest_info)
                    continue

            # check the duplicated base shap declaration
            base_shap_dclr_times += 1

            if base_shap_dclr_times > 1 :                  
                warn_type   = duplicate_declared('base shap', 'Warn')
                sgest_info  = 'It has been declared at ' \
                            + f'{Empha_color}{base_shap_line}.\n'
                report_warn('SDD05', line_num, warn_type + sgest_info)
                continue

            # get base shap declaration
            base_shap_form = shap_form
            base_shap_nodn = shap_nodn
            base_shap_line = line_num

        # report the lack
        elif len(shap_list) < 2:
            error_type  = faultly_declared('SHAP', 'Error')
            sgest_info  = f"Shap declaration must have at least " \
                        + f"2 variables as 'SHAP %1 %2'.\n"
            report_error('SFD06', line_num, error_type + sgest_info)

    # report no base shap declaration
    if base_shap_dclr_times == 0:
        error_type  = faultly_declared('SHAP', 'Error')
        sgest_info  = "No base shap declaration, it must at least" \
                    + " insert a line write as 'SHAP %1 %2'.\n"
        report_error('SFD07', line_num, error_type + sgest_info)

    # second check the mix order or penalty element
    for shap_list, line_num in zip(xde_dict['shap'], xde_addr['shap']):

        # get and check mix order or penalty shap declare
        if len(shap_list) > 2:

            # get the first parameter
            if shap_list[0] == '%1':
                shap_form = ges_info['shap_form']
            else:
                shap_form = shap_list[0]

            # check the first parameter
            if shap_form != base_shap_form:
                error_type  = faultly_declared('SHAP', 'Error')
                sgest_info  = 'the first variable must be same to base shap ' \
                            + f"declared at line {Empha_color}{base_shap_line}"
                report_error('SFD08', line_num, error_type + sgest_info)

            # get the second parameter
            if   shap_list[1] == '%2':
                error_type  = faultly_declared('SHAP', 'Error')
                sgest_info  = "redundant information when declare base shap, " \
                            + "'%2' must be followed by nothing.\n"
                report_error('SFD09', line_num, error_type + sgest_info)
                continue

            elif shap_list[1] == '%4':
                if shap_form in shap_forms:
                    shap_nodn = node_dgree1[shap_forms.index(shap_form)]

            elif shap_list[1] == '%2c':
                shap_nodn = shap_list[1].replace('%2',ges_info['shap_nodn'])

            else:
                shap_nodn = shap_list[1]

            # check the second parameter
            if shap_nodn.isnumeric():

                vars_list = [var for var in shap_list[2:] if not var.isnumeric()]

                if len(set(vars_list)) != len(vars_list):
                    report_warn('SWN10', line_num, 'variable duplicated.\n')

                # check variables use mix order shap be declared in 'disp' or 'coef'
                var_not_dclr = []
                for var_name in vars_list:
                    if 'coef' not in xde_dict:
                        if 'disp' in xde_dict \
                        and var_name not in xde_dict['disp'] :
                           var_not_dclr.append(var_name) 

                    else:
                        if  'disp' in xde_dict \
                        and var_name not in xde_dict['disp'] \
                        and var_name not in xde_dict['coef'] :
                            var_not_dclr.append(var_name) 
                            
                if len(var_not_dclr) != 0:
                    warn_type   = not_declared(','.join(var_not_dclr), 'Warn')
                    sgest_info  = 'It must be declared in disp or coef.\n'
                    report_warn('SND11', line_num, warn_type + sgest_info)

                # base shap is not degree 2 or not coordinate with shap_form
                base_index = shap_forms.index(base_shap_form)
                if base_shap_nodn != node_dgree2[base_index]:
                    error_type  = faultly_declared('SHAP', 'Error')
                    sgest_info  = 'The second variable of base shap must to be ' \
                                + Empha_color + node_dgree2[base_index] \
                                + Error_color + '(second order), ' \
                                + 'since using mix order element.\n'
                    report_error('SFD12', base_shap_line, error_type + sgest_info)

                # sub shap is not coordinate with base or not coordinate with shap_form
                if shap_nodn != node_dgree1[base_index]:
                    error_type  = faultly_declared('SHAP', 'Error')
                    sgest_info  = 'The second variable of mixed shap must to be ' \
                                + Empha_color + node_dgree1[base_index] \
                                + Error_color + '(first order), ' \
                                + 'since using mix order element.\n'
                    report_error('SFD13', line_num, error_type + sgest_info)

            elif shap_nodn[:-1].isnumeric() \
            and  shap_nodn[-1] == 'c':
                
                falty_form_list = []
                var_not_dclr    = []
                var_name_list   = []
                pan_name_list   = []

                for var_comp in shap_list[2:]:

                    if var_comp.count('_') == 1:
                        var_name, pan_name = var_comp.split('_')
                        temp_var_name = var_name
                        temp_pan_name = pan_name

                        # gether both side of '_'
                        var_name_list.append(var_name)
                        pan_name_list.append(pan_name)

                        # gether variable declared in 'coef' or not in 'disp'
                        if 'coef' in xde_dict:
                            if var_name in xde_dict['coef']:
                                temp_var_name = Empha_color + var_name

                            if pan_name in xde_dict['coef']:
                                temp_pan_name = Empha_color + pan_name

                        if 'disp' in xde_dict:
                            if var_name not in xde_dict['disp']:
                                temp_var_name = Empha_color + var_name

                            if pan_name not in xde_dict['disp']:
                                temp_pan_name = Empha_color + pan_name
                        
                        else:
                            temp_var_name = Empha_color + var_name
                            temp_pan_name = Empha_color + pan_name

                        if temp_var_name != var_name \
                        or temp_pan_name != pan_name:

                            if temp_var_name == var_name:
                                temp_var_name = Error_color + var_name
                            if temp_pan_name == pan_name:
                                temp_pan_name = Error_color + pan_name

                            var_not_dclr.append(temp_var_name + Error_color + '_' + temp_pan_name)

                    # gether variable component without '-' or with more than one '-'
                    else:
                        falty_form_list.append(var_comp)

                # check variables declared in 'coef' or not in 'disp'
                if len(falty_form_list) != 0:
                    error_type  = unsuitable_form(', '.join(falty_form_list), 'Error')
                    sgest_info  = "It must be declared as '*_*'.\n"
                    report_error('SUF14', line_num, error_type + sgest_info)

                # check variable components without '-' or with more than one '-'
                if len(var_not_dclr) != 0:
                    error_type  = faultly_declared(', '.join(var_not_dclr), 'Error')
                    sgest_info  = "The green color variables must not be declared " \
                                + "in 'coef' and must be declared in 'disp'.\n"
                    report_error('SFD15', line_num, error_type + sgest_info)


                # check variables used at both side of '_'
                multi_use = set(var_name_list) & set(pan_name_list)

                if len(multi_use) != 0:
                    error_type  = unsuitable_form(', '.join(multi_use), 'Error')
                    sgest_info  = f"{Empha_color}{', '.join(multi_use)} " \
                                + f"{Error_color}must not be used at both side of '_'.\n"
                    report_error('SUF16', line_num, 'not a suitable form, ' + sgest_info)

                # base shap is not degree 1 or not coordinate with shap_form
                base_index = shap_forms.index(base_shap_form)
                if base_shap_nodn != node_dgree1[base_index]:
                    error_type  = faultly_declared('SHAP', 'Error')
                    sgest_info  = 'The second variable of base shap must to be ' \
                                + Empha_color + node_dgree1[base_index] \
                                + Error_color + '(first order), ' \
                                + 'since using penalty element.\n'
                    report_error('SFD17', base_shap_line, error_type + sgest_info)

                # sub shap is not coordinate with base or not coordinate with shap_form
                if shap_nodn[:-1] != node_dgree1[base_index]:
                    error_type  = faultly_declared('SHAP', 'Error')
                    sgest_info  = 'The second variable of penalty shap must to be ' \
                                + Empha_color + node_dgree1[base_index] \
                                + Error_color + '(first order), ' \
                                + 'since using penalty element.\n'
                    report_error('SFD18', line_num, error_type + sgest_info)

            else:
                error_type  = faultly_declared('SHAP', 'Error')
                sgest_info  = f"If it's mix element shap, declare as " \
                            + f"'shap %1 %4 x x ...'; If it's penalty " \
                            + f"element shap, declare as 'shap '%1 %2c x x ...'.\n"
                report_error('SFD19', line_num, error_type + sgest_info)

            ''' # 'm','a','v','p','e' shap need to imporve
            if not shap_list[1].isnumeric() \
            and shap_list[1][-1] in ['m','a','v','p','e']:
                posfix = 'd' + ges_info['dim'] + shap_form + shap_nodn
                if posfix not in shap_name_list:
                    error_type  = faultly_declared('SHAP', 'Error')
                    sgest_info  = shap_form + shap_nodn + ' is not a valid shap.\n'
                    report_error('SFD13', line_num, error_type + sgest_info)
            '''
# end check_shap()

def check_code(ges_info, xde_dict, xde_addr, c_declares):

    # the inner declaration
    inner_declares  = {'tmax','dt','nstep','itnmax','time'} \
                    | {'tolerance','dampalfa','dampbeta'} \
                    | {'it','stop','itn','end'} \
                    | {'imate','nmate','nelem','nvar','nnode'} \
                    | {'ngaus','igaus','ndisp','nrefc','ncoor'} \
                    | {'vol','det','weigh','stif','fact','shear','r0'} \
                    | {'*nvard','*kdord','*kvord','*refc','*gaus'} \
                    | {'*coor','*coorr','*rctr','*crtr'} \
                    | {'*coora','*coefa','*prmt','*estif','*emass','*edamp','*eload'} \
                    | {'num','ibegin'}

    # gather C declares and check code
    c_declares['all']    = inner_declares.copy()
    c_declares['BFmate'] = inner_declares.copy()
    c_declares['array']  = {}
    c_declares['array']['vect'] = set()
    c_declares['array']['matrix'] = set()
    c_declares['tnsr_used'] = {}
    c_declares['tnsr_used']['vect'] = set()
    c_declares['tnsr_used']['matrix'] = set()


    for strs in ["disp","coef","coor"]:
        if strs in xde_dict:
            c_declares['all'] |= set(xde_dict[strs])

    if 'func' in xde_dict:
        for func_list in xde_dict['func']:
            c_declares['all'] |= set(func_list)

    if 'cmplx_tag' in xde_dict \
    and xde_dict['cmplx_tag'] == 1:
        if "disp" in xde_dict:
            for var in xde_dict[strs]:
                c_declares['all'].add(var+'r')
                c_declares['all'].add(var+'i')
        if 'func' in xde_dict:
            for func_list in xde_dict['func']:
                for var in func_list:
                    c_declares['all'].add(var+'r')
                    c_declares['all'].add(var+'i')

    assist = {}
    for addr in xde_dict["code"].keys():

        assist['stitch'] = ''
        assist['addrss'] = addr
        for code_strs, line_num in zip(xde_dict["code"][addr], xde_addr["code"][addr]):

            code_key = re.match(r'\$C[C6VP]|@[LAWSR]|COMMON|ARRAY',code_strs,re.I)

            if code_key == None:
                continue

            assist['ckey'] = code_key  = code_key.group()
            assist['lkey'] = lower_key = code_key.lower()

            if lower_key == 'common':
                code_strs = code_strs.replace(code_key,'')+';'

            else:
                code_strs = code_strs.replace(code_key,'').lstrip()

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
                if check_operator(code_strs, line_num, xde_dict, xde_addr, c_declares):
                    continue

            elif lower_key in ['@w', '@s']:
                check_ftensor_assign_1(code_strs, line_num, xde_dict, xde_addr, c_declares, lower_key)

            elif lower_key in ['@a', '@r']:
                check_ftensor_assign_2(code_strs, line_num, xde_dict, xde_addr, c_declares, lower_key)
# end check_code()

def gather_declare(code_strs, line_num, assist_dict, c_declares):
    # check $cc code
    code_key   = assist_dict['ckey']
    #lower_key  = assist_dict['lkey']
    declare_pattern  = r"char|int|long|short|double|float"
    #expr_pattern = r"[a-z].*="
    function_pattern = r"\w+\(.*\)"


    # find c declaration sentence and gather the variables
    if re.search(declare_pattern, code_strs, re.I) != None:

        code_strs = assist_dict['stitch'] + code_strs
        if code_strs[-1] != ';':
            assist_dict['stitch'] = code_strs
            return True    # continue
        else:
            assist_dict['stitch'] = ''

        code_list = code_strs.split(';')
        code_list.pop()

        for sub_sentence in code_list:

            if re.search(function_pattern, code_strs, re.I) != None:
                continue

            if re.search(declare_pattern, sub_sentence, re.I) == None:
                continue

            var_strs = re.split(declare_pattern,sub_sentence,re.I)[1].strip()

            for var in var_strs.split(','):
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
# end gather_declare()

def gather_array_declare(code_strs, line_num, assist, c_declares):
    
    var_list = code_strs.replace(assist['ckey'],'').strip().split(',')

    wrong_form_list = []

    for var_strs in var_list:
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

        else:
            wrong_form_list.append(var_strs)

    if len(wrong_form_list) != 0:
        warn_type   = unsuitable_form(', '.join(wrong_form_list), 'Warn')
        sgest_info  = "Right form write as 'a[d]' or '^a[d][d]', where " \
                    + "'a' means charactors and 'd' means digitals.\n"
        report_warn('CUF01', line_num, warn_type + sgest_info)
# end gather_array_declare()

def insert_array_declare(c_declares, assist, vtype, vlist, var_name):

    c_declares['all'] |= set(vlist)
    c_declares['array'][vtype].add(var_name)

    if assist['addrss'] == 'BFmate':
        c_declares['BFmate'] |= set(vlist)
# end insert_array_declare()

def check_tensor_assign(code_strs, line_num, xde_dict, c_declares, complex_tag = 0):

    tensor_pattern = re.compile(r'\^?[a-z][a-z0-9]*(?:_[a-z])+',re.I)
    tensor_list = tensor_pattern.findall(code_strs)

    if len(tensor_list) == 0 \
    and code_strs.find('{') == -1:
        sgest_info = "there is no tensor or derivation of " \
                   + "'coef' variable, need not to use '$CV'.\n"
        report_warn('CUF02', line_num, sgest_info)

    elif complex_tag == 0:
        wrong_form_list = []
        vect_not_found  = []
        matr_not_found  = []

        for tensor in set(tensor_list):
            tensor_name = tensor.split('_')[0]

            # find all the vectors not declared
            if tensor.count('_') == 1:

                c_declares['tnsr_used']['vect'].add(tensor_name)

                if ( 'vect' not in xde_dict \
                    or ( 'vect' in xde_dict \
                        and tensor_name not in xde_dict['vect'] ) ) \
                and tensor_name not in c_declares['array']['vect']:

                    vect_not_found.append(tensor)

            # find all the matrices not declared
            elif tensor.count('_') == 2:

                c_declares['tnsr_used']['matrix'].add(tensor_name)

                if ( 'matrix' not in xde_dict \
                    or ( 'matrix' in xde_dict \
                        and tensor_name not in xde_dict['matrix'] ) ) \
                and tensor_name not in c_declares['array']['matrix']:

                    matr_not_found.append(tensor)

            # find all the wrong form
            else:
                wrong_form_list.append(tensor)

        # check all the vectors not declared
        if len(vect_not_found) != 0:
            error_type = not_declared(', '.join(set(vect_not_found)), 'Error')
            sgest_info = "It must declared by 'VECT' or 'ARRAY'.\n"
            report_error('CND03', line_num, error_type + sgest_info)

        # check all the matrices not declared
        if len(matr_not_found) != 0:
            error_type = not_declared(', '.join(set(matr_not_found)), 'Error')
            sgest_info = "It must declared by 'MATRIX' or 'ARRAY'.\n"
            report_error('CND04', line_num, error_type + sgest_info)

        # check all the wrong form
        if len(wrong_form_list) != 0:
            warn_type   = unsuitable_form(', '.join(set(wrong_form_list)), 'Warn')
            sgest_info  = "Right form write as 'a[d]' or '^a[d][d]', where " \
                        + "'a' means charactors and 'd' means digitals.\n"
            report_warn('CUF05', line_num, warn_type + sgest_info)
# end check_tensor_assign()

def check_complex_assign(code_strs, line_num, xde_dict, xde_addr, c_declares):

    var_pattern = re.compile(r'\^?[a-z]\w*',re.I)
    var_list = var_pattern.findall(code_strs)
    tensor_list, scalar_list = [], []

    for var in var_list:
        if var.find('_') != -1:
            tensor_list.append(var)
        else:
            scalar_list.append(var)

    if len(scalar_list) != 0:

        real_list = []
        imag_list = []

        for var in set(scalar_list):

            # find all real part not declared
            if var+'r' not in c_declares['all']:
                real_list.append(var)

            # find all image part not declared
            if var+'i' not in c_declares['all']:
                imag_list.append(var)

        # check all real part not declared
        if len(real_list) != 0:
            error_type = not_declared('real of '+', '.join(real_list), 'Error')
            report_error('CND06', line_num, error_type + '\n')

        # check all image part not declared
        if len(imag_list) != 0:
            error_type = not_declared('imag of '+', '.join(imag_list), 'Error')
            report_error('CND07', line_num, error_type + '\n')
                
    if len(tensor_list) != 0:
        
        check_tensor_assign(code_strs, line_num, xde_dict, c_declares, 1)

        vect_not_found  = []
        matr_not_found  = []
        vect_real_not_found = []
        vect_imag_not_found = []
        matr_real_not_found = []
        matr_imag_not_found = []
        
        for tensor in set(tensor_list):

            tensor_name = tensor.split('_')[0]

            if tensor.count('_') == 1:

                c_declares['tnsr_used']['vect'].add(tensor_name)

                if 'vect' in xde_addr \
                and tensor_name in xde_addr['vect']:
                    vect_line_num = xde_addr['vect'][tensor_name]
                else:
                    continue

                # gether vectors not declared by 'vect'
                if ( 'vect' not in xde_dict \
                    or ( 'vect' in xde_dict \
                        and tensor_name not in xde_dict['vect'] ) ) \
                or tensor_name in c_declares['array']['vect']:

                    vect_not_found.append(tensor)

                else:
                    for var in xde_dict['vect'][tensor_name]: 
                        
                        # gether real part of component of vector not declared
                        if var+'r' not in c_declares['all']:

                            Empha_info = f'real of {var} in vector ' \
                                       + f'{tensor_name}(line {vect_line_num})'
                            error_type = not_declared(Empha_info, 'Error')

                            vect_real_not_found.append('\t'+error_type)

                        # gether iamge part of component of vector not declared
                        if var+'i' not in c_declares['all']:

                            Empha_info = f'imag of {var} in vector ' \
                                       + f'{tensor_name}(line {vect_line_num})'
                            error_type = not_declared(Empha_info, 'Error')

                            vect_imag_not_found.append('\t'+error_type)

            elif tensor.count('_') == 2:

                c_declares['tnsr_used']['matrix'].add(tensor_name)

                # gether matrics not declared by 'matrix'
                if ( 'matrix' not in xde_dict \
                    or ( 'matrix' in xde_dict \
                        and tensor_name not in xde_dict['matrix'] ) ) \
                or tensor_name in c_declares['array']['matrix']:

                    matr_not_found.append(tensor)

                else:

                    matrix_list      = xde_dict['matrix'][tensor_name][2:].copy()
                    matrix_line_nums = xde_addr['matrix'][tensor_name][1:].copy()

                    for vars_list, matr_line_num in zip(matrix_list, matrix_line_nums):
                        var_regx = re.compile(r'[a-z][a-z0-9]*',re.I)

                        for var in set(var_regx.findall(' '.join(vars_list))):

                            # gether real part of component of matrix not declared
                            if var+'r' not in c_declares['all']:

                                Empha_info = f'real of {var} in matrix ' \
                                           + f'{tensor_name}(line {matr_line_num})'
                                error_type = not_declared(Empha_info, 'Error')

                                matr_real_not_found.append('\t'+error_type)

                            # gether image part of component of matrix not declared
                            if var+'i' not in c_declares['all']:

                                Empha_info = f'imag of {var} in matrix ' \
                                           + f'{tensor_name}(line {matr_line_num})'
                                error_type = not_declared(Empha_info, 'Error')

                                matr_imag_not_found.append('\t'+error_type)

        # check all the vectors not declared by 'vect'
        if len(vect_not_found) != 0:
            error_type = not_declared(', '.join(set(vect_not_found)), 'Error')
            sgest_info = "It must declared by 'VECT'.\n"
            report_error('CND08', line_num, error_type + sgest_info)

        # check all the matrices not declared by 'matrix'
        if len(matr_not_found) != 0:
            error_type = not_declared(', '.join(set(matr_not_found)), 'Error')
            sgest_info = "It must declared by 'matrix'.\n"
            report_error('CND09', line_num, error_type + sgest_info)

        # check all of real part of component of vector not declared
        if len(vect_real_not_found) != 0:
            report_error('CND10', line_num, '\n' + '\n'.join(set(vect_real_not_found)) + '\n')

        # check all of image part of component of vector not declared
        if len(vect_imag_not_found) != 0:
            report_error('CND11', line_num, '\n' + '\n'.join(set(vect_imag_not_found)) + '\n')

        # check all of real part of component of matrix not declared
        if len(matr_real_not_found) != 0:
            report_error('CND12', line_num, '\n' + '\n'.join(set(matr_real_not_found)) + '\n')

        # check all of image part of component of matrix not declared
        if len(matr_imag_not_found) != 0:
            report_error('CND13', line_num, '\n' + '\n'.join(set(matr_imag_not_found)) + '\n')
# end check_complex_assign()

def check_operator(code_strs, line_num, xde_dict, xde_addr, c_declares):

    code_list = code_strs.split()

    try:
        opr_name, opr_axis = code_list[0].split('.')

    # code_list[0] has no '.'
    except ValueError:
        error_type  = unsuitable_form(code_list[0],'Error')
        sgest_info  = "Suggested form as 'operator.axis', " \
                    + "for isinstance 'grad.xyz'.\n"
        report_error('OUF01', line_num, error_type + sgest_info)

    # code_list is empty
    except IndexError:
        error_type  = unsuitable_form('', 'Error')
        report_error('OUF02', line_num, 'Empty operator.\n')

    else:

        # check that operator.axis is in oprt_name_list
        if code_list[0].lower() not in oprt_name_list:
            error_type  = unsuitable_form(code_strs, 'Error')
            sgest_info  = Empha_color + code_list[0] \
                        + Error_color + " is not a default operator.\n"
            report_error('OUF03', line_num, error_type + sgest_info)
            return True

        try:
            opr_deed = code_list[1].lower()

        # no following operator action
        except IndexError:
            error_type  = unsuitable_form(code_list[0],'Error')
            sgest_info  = "No action and object definded after operator, " \
                        + "for isinstance 'grad.xyz f dp'.\n"
            report_error('OUF04', line_num, error_type + sgest_info)

        else:

            if opr_deed == 'n':

                # redundancy for operator deed 'n'
                if len(code_list[2:]) != 0:
                    warn_type  = unsuitable_form(code_strs, 'Warn')
                    sgest_info = "useless information after 'n'.\n"
                    report_warn('OUF05', line_num, warn_type + sgest_info)

            else:
                try:
                    opr_object = code_list[2]

                # no following operator object
                except IndexError:
                    error_type  = unsuitable_form(code_list[0],'Error')
                    sgest_info  = "No object definded after operator action, " \
                                + "for isinstance 'grad.xyz f dp'.\n"
                    report_error('OUF06', line_num, error_type + sgest_info)

                opr_parameters = code_list[3:].copy()

                opr_features = {}
                opr_features['name'] = opr_name
                opr_features['axis'] = opr_axis
                opr_features['deed'] = opr_deed
                opr_features['objt'] = opr_object
                opr_features['parameters'] = opr_parameters

                check_operator_content(opr_features, code_strs, line_num,  xde_dict, xde_addr, c_declares)

    return False
# end check_operator()

def check_operator_content(opr_features, code_strs, line_num, xde_dict, xde_addr, c_declares):

    opr_name = opr_features['name']
    opr_axis = opr_features['axis']
    opr_deed = opr_features['deed']
    opr_object = opr_features['objt']
    opr_parameters = opr_features['parameters']

    opr_default_disp_paramater = operator_data[opr_name][opr_axis]['disp']
    opr_default_disp_length    = len(opr_default_disp_paramater)
    opr_default_axis_paramater = operator_data[opr_name][opr_axis]['axis']
    opr_default_axis_length    = len(opr_default_axis_paramater)

    # get default parameters of operator
    if len(opr_parameters) == 0:

        opr_parameters += list(opr_axis)

        if 'disp' in xde_dict \
        and opr_deed == 'f':
            opr_parameters += xde_dict['disp'][:opr_default_disp_length]

        elif 'coef' in xde_dict \
        and opr_deed in ['c','v','m']:
            opr_parameters += xde_dict['coef'][:opr_default_disp_length]

        if   opr_axis in ['oz', 'so']:
            opr_parameters.insert(0,'r')

        elif opr_axis == 's':
            opr_parameters[0] = 'r'
    
    # get provided parameters of operator
    else:

        temp_list = opr_parameters.copy()
        opr_parameters.clear()

        for strs in temp_list:

            if   strs.find('_') == -1:
                opr_parameters.append(strs)

            elif strs.count('_') == 1:

                vect = strs.split('_')[0]
                c_declares['tnsr_used']['vect'].add(vect)

                if 'vect' not in xde_dict \
                or ( 'vect' in xde_dict \
                    and vect not in xde_dict['vect'] ):

                    error_type = not_declared(vect, 'Error')
                    sgest_info = "It must be declared by 'VECT'.\n"
                    report_error('OND07', line_num, error_type + sgest_info)

                else:
                    opr_parameters += xde_dict['vect'][vect]

            else:
                error_type = unsuitable_form(strs, 'Error')
                sgest_info = "only vector or scalar can be operator's variable.\n"
                report_error('OUF08', line_num, error_type + sgest_info)

    # get axis variables
    opr_axis_list = []
    for strs in opr_parameters:
    
        if strs in list('xyzros') \
        or strs in xde_dict['coor']:
            opr_axis_list.append(strs)
        else:
            break

    # get disp or coef variables
    opr_disp_list = opr_parameters.copy()
    for strs in opr_axis_list:
        opr_disp_list.remove(strs)

    opr_axis_list_length = len(opr_axis_list)
    opr_disp_list_length = len(opr_disp_list)

    # check the axis and disp or coef variables count of operator parameters
    if opr_axis_list_length != opr_default_axis_length:
        error_type  = unsuitable_form(code_strs, 'Error')
        sgest_info  = f"need {opr_default_axis_length} axis " \
                    + f"but provided {opr_axis_list_length}.\n"
        report_error('OUF09', line_num, error_type + sgest_info)

    if opr_disp_list_length != opr_default_disp_length:
        error_type  = unsuitable_form(code_strs, 'Error')
        sgest_info  = f"need {opr_default_disp_length} disp " \
                    + f"but provided {opr_disp_list_length}.\n"
        report_error('OUF10', line_num, error_type + sgest_info)

    
    # warning that operator's axis be not in accordance with 'coor' declaration
    if 'coor' in xde_dict \
    and opr_axis != ''.join(xde_dict['coor']):
        warn_type   = unsuitable_form(opr_name+'.'+opr_axis, 'Warn')
        sgest_info  = f"coordinate of operator {Empha_color}'{opr_axis}' " \
                    + f"{Warnn_color}is not consistance with 'coor' declaration " \
                    + f"{Empha_color}'{' '.join(xde_dict['coor'])}' {Warnn_color}in line " \
                    + f"{Empha_color}{str(xde_addr['coor'])}, {Warnn_color}" \
                    + "and please make sure that it is necessary to do so.\n"
        report_warn('OUF11', line_num, warn_type + sgest_info)

    # check operator actions
    if opr_deed in ['c','v','m']:
        
        # normal variables of operator must be declared in 'COEF'
        if 'coef' not in xde_dict:
            diff_set = set(opr_disp_list)
        else:
            diff_set = set(opr_disp_list).difference(set(xde_dict['coef']))

        if len(diff_set) != 0:
            error_type = unsuitable_form(code_strs, 'Error')
            sgest_info = f"'{', '.join(list(diff_set))}' must be declared in 'COEF'.\n"
            report_error('OUF12', line_num, error_type + sgest_info)

        # 'c' means resault of operator assigned to scalar (c code declared)
        if opr_deed == 'c':
            if opr_object not in c_declares['all']:
                error_type = not_declared(opr_object, 'Error')
                sgest_info = f'it must be declared before line {line_num}.\n'
                report_error('OND13', line_num, error_type + sgest_info)

        # 'v' means resault of operator assigned to vector (vect declared)
        elif opr_deed == 'v':
            if  'vect' in xde_dict \
            and opr_object not in xde_dict['vect'] \
            and opr_object not in c_declares['array']['vect']:
                error_type = not_declared(opr_object, 'Error')
                sgest_info = "it must be declared by 'VECT' or 'ARRAY'.\n"
                report_error('OND14', line_num, error_type + sgest_info)

        # 'm' means resault of operator assigned to matrix (matrix declared)
        elif opr_deed == 'm':
            if  'matrix' in xde_dict \
            and opr_object not in xde_dict['matrix'] \
            and opr_object not in c_declares['array']['matrix']:
                error_type = not_declared(opr_object, 'Error')
                sgest_info = "it must be declared by 'MATRIX' or 'ARRAY'.\n"
                report_error('OND15', line_num, error_type + sgest_info)

    # 'f' means resault of operator assigned to fvect or fmatr
    elif opr_deed == 'f':

        # normal variables of operator must be declared in 'DISP'
        if 'disp' not in xde_dict:
            diff_set = set(opr_disp_list)
        else:
            diff_set = set(opr_disp_list).difference(set(xde_dict['disp']))

        if len(diff_set) != 0:
            error_type = unsuitable_form(code_strs, 'Error')
            sgest_info = f"'{' '.join(list(diff_set))}' must be declared in 'DISP'.\n"
            report_error('OUF16', line_num, error_type + sgest_info)

        # check object of operator is declared by 'FVECT' or 'FMATR'
        fvect = 'fvect' in xde_dict and opr_object in xde_dict['fvect']
        fmatr = 'fmatr' in xde_dict and opr_object in xde_dict['fmatr']

        # object of operator not allowed to be declared by 'FVECT' or 'FMATR' at the same time
        if  fvect and fmatr:
            error_type  = faultly_declared(opr_object, 'Error')
            sgest_info  = f"It not allowed to be declared by 'FVECT'" \
                        + f"(line {Empha_color}{xde_addr['fvect'][opr_object]}" \
                        + f"{Error_color}) and 'FMATR'" \
                        + f"(line {Empha_color}{xde_addr['fmatr'][opr_object]}" \
                        + f"{Error_color}) at the same time.\n"
            report_error('OFD17', line_num, error_type + sgest_info)

        elif not fvect and not fmatr:
            error_type = not_declared(opr_object, 'Error')
            sgest_info = "it must be declared by 'FVECT' or 'FMATR'.\n"
            report_error('OND18', line_num, error_type + sgest_info)

    else:
        error_type = unsuitable_form(code_strs, 'Error')
        sgest_info = "first variable of operator must be one of '[n, c, v, m, f]'.\n"
        report_error('OUF19', line_num, error_type + sgest_info)
# end check_operator_content()

# @W (func_vect) (fvect|fmatr) * * *...
# @S (fvect|fmatr) (fvect|fmatr) * * *...
# * means digitals
def check_ftensor_assign_1(code_strs, line_num, xde_dict, xde_addr, c_declares, atype):

    code_list = code_strs.split()

    try:
        left_tensor = code_list[0]
    
    except IndexError:
        error_type = unsuitable_form('*', 'Error')
        report_error('FUF01', line_num, 'Empty assignment.\n')

    else:
        try:
            righ_tensor = code_list[1]

        except IndexError:
            error_type = unsuitable_form('*', 'Error')
            report_error('FUF02', line_num, 'No right tensor followed.\n')

        else:
            try:
                righ_indexs = list(map(int, code_list[2:]))

            except ValueError:

                error_type = unsuitable_form(f"{' '.join(code_list[2:])}", 'Error')
                report_error('FUF03', line_num, error_type + 'Have none digitals.\n')

            else:
                ftensor_features = {}
                ftensor_features['left'] = left_tensor
                ftensor_features['righ'] = righ_tensor
                ftensor_features['indx'] = righ_indexs

                check_ftensor_assign_1_content(ftensor_features, line_num, xde_dict, xde_addr, c_declares, atype)
# end check_ftensor_assign_1()

def check_ftensor_assign_1_content(ftensor_features, line_num, xde_dict, xde_addr, c_declares, atype):

    left_tensor = ftensor_features['left']
    righ_tensor = ftensor_features['righ']
    righ_indexs = ftensor_features['indx']

    left_size, righ_size = 0, 0

    if   atype == '@w':
        tvect, tmatr = 'vect', 'matrix'
    else:
        tvect, tmatr = 'fvect', 'fmatr'

    left_judge_tag = 0
    duplicate_declared_info = []
    duplicate_declared_type = []
    declared_type = f"'{tvect}', '{tmatr}'"

    # gether left tensor declaration by 'vect' or 'fvect'
    if tvect in xde_dict and left_tensor in xde_dict[tvect]:
        left_judge_tag += 1

        error_str   = f"{Error_color}declared by '{tvect}' at line " \
                    + f"{Empha_color}{xde_addr[tvect][left_tensor]}"
                    
        duplicate_declared_info.append('\t' + error_str)
        duplicate_declared_type.append(f'{tvect}')

        # check the component of left vector declared by 'func'
        if atype == '@w':

            c_declares['tnsr_used'][tvect].add(left_tensor)
            left_size = len(xde_dict[tvect][left_tensor])

            component_not_func = []
            for strs in xde_dict[tvect][left_tensor]:
                break_tag = False
                for func_list in xde_dict['func']:
                    if break_tag:
                        break
                    for func in func_list:
                        if strs == func:
                            break_tag = True
                            break
                if not break_tag:
                    component_not_func.append(strs)

            if len(component_not_func) != 0:
                error_type  = not_declared(f"{', '.join(component_not_func)}", 'Error')
                sgest_info  = f"The component of {tvect} {left_tensor}(line " \
                            + f"{Empha_color}{xde_addr[tvect][left_tensor]}" \
                            + f"{Error_color}) must declared by 'func'.\n"
                report_error('FND04',line_num, error_type + sgest_info)

        else:

            left_size = xde_dict[tvect][left_tensor][0]

    # gether left tensor declaration by 'matrix' or 'fmatr'
    if tmatr in xde_dict and left_tensor in xde_dict[tmatr]:
        left_judge_tag += 1

        if tmatr == 'matrix':
            tmatr_line_num = xde_addr[tmatr][left_tensor][0]
        else:
            tmatr_line_num = xde_addr[tmatr][left_tensor]

        error_str   = f"{Error_color}declared by '{tmatr}' at line " \
                    + f"{Empha_color}{tmatr_line_num}"

        duplicate_declared_info.append('\t' + error_str)
        duplicate_declared_type.append(f'{tmatr}')

        left_size = xde_dict[tmatr][left_tensor][0] \
                  * xde_dict[tmatr][left_tensor][1]

        # check the component of left matrix declared by 'func'
        if atype == '@w':

            component_not_func = []
            for str_list in xde_dict[tmatr][left_tensor][2:]:
                for strs in str_list:
                    break_tag = False
                    for func_list in xde_dict['func']:
                        if break_tag:
                            break
                        for func in func_list:
                            if strs == func:
                                break_tag = True
                                break
                    if not break_tag:
                        component_not_func.append(strs)

            if len(component_not_func) != 0:
                error_type  = not_declared(f"{', '.join(component_not_func)}", 'Error')
                sgest_info  = f"The component of {tmatr} {left_tensor}(line " \
                            + f"{Empha_color}{xde_addr[tmatr][left_tensor][0]}" \
                            + f"{Error_color})must declared by 'func'.\n"
                report_error('FND05',line_num, error_type + sgest_info)

    ''' !! comment it because left tensor must be component by 'func' variable
    if atype == '@w':

        declared_type += f", 'array' vector form, 'array' matrix form"

        # gether declaration by 'array' vector form
        if left_tensor in c_declares['array']['vect']:
            left_judge_tag += 1

            error_str   = f"{Error_color}declared by 'array' vector form " \
                        + f"at line {Empha_color}{str(xde_addr['array'])}"

            duplicate_declared_info.append('\t' + error_str)
            duplicate_declared_type.append("'array' vector form")

        # gether declaration by 'array' matrix form
        if left_tensor in c_declares['array']['matrix']:
            left_judge_tag += 1

            error_str   = f"{Error_color}declared by 'array' matrix form " \
                        + f"at line {Empha_color}{str(xde_addr['array'])}"

            duplicate_declared_info.append('\t' + error_str)
            duplicate_declared_type.append("'array' matrix form")
    '''

    # check left tensor duplicated declaration
    if left_judge_tag > 1:
        error_type  = faultly_declared(left_tensor, 'Error')
        sgest_info  = f"It has be duplicated declared by " \
                    + f"{', '.join(duplicate_declared_type)}:\n"
        report_error('FFD06', line_num, error_type + sgest_info \
                    + '\n'.join(duplicate_declared_info)+ '\n')

    # check left tensor not declared
    elif left_judge_tag == 0:
        error_type  = not_declared(left_tensor, 'Error')
        sgest_info  = f"It must be declared by one of {declared_type}.\n"
        report_error('FND07', line_num, error_type + sgest_info)

    
    righ_judge_tag = 0
    duplicate_declared_info.clear()
    duplicate_declared_type.clear()
    declared_type = "'fvect', 'fmatr'"

    # gether right tensor declaration by 'fvect'
    if 'fvect' in xde_dict and righ_tensor in xde_dict['fvect']:
        righ_judge_tag += 1

        error_str   = f"{Error_color}declared by '{'fvect'}' at line " \
                    + f"{Empha_color}{xde_addr['fvect'][righ_tensor]}"
                    
        duplicate_declared_info.append('\t' + error_str)
        duplicate_declared_type.append('fvect')

        righ_size = xde_dict['fvect'][righ_tensor][0]

    # gether right tensor declaration by 'fmatr'
    if 'fmatr' in xde_dict and righ_tensor in xde_dict['fmatr']:
        righ_judge_tag += 1

        error_str   = f"{Error_color}declared by '{'fmatr'}' at line " \
                    + f"{Empha_color}{xde_addr['fmatr'][righ_tensor]}"

        duplicate_declared_info.append('\t' + error_str)
        duplicate_declared_type.append('fmatr')

        righ_size = xde_dict['fmatr'][righ_tensor][0] \
                  * xde_dict['fmatr'][righ_tensor][1]

    # check right tensor duplicated declaration
    if righ_judge_tag > 1:
        error_type  = faultly_declared(righ_tensor, 'Error')
        sgest_info  = f"It has be duplicated declared by " \
                    + f"{', '.join(duplicate_declared_type)}:\n"
        report_error('FFD08', line_num, error_type + sgest_info \
                    + '\n'.join(duplicate_declared_info)+ '\n')

    # check right tensor not declared
    elif righ_judge_tag == 0:
        error_type  = not_declared(righ_tensor, 'Error')
        sgest_info  = f"It must be declared by one of {declared_type}.\n"
        report_error('FND09', line_num, error_type + sgest_info)

    # gether right indexs and check if out of range
    max_righ_size = righ_size

    if len(righ_indexs) != 0:
        righ_size = len(righ_indexs)

        out_range_index = []
        for index in righ_indexs:
            if index > max_righ_size:
                out_range_index.append(str(index))

        if len(out_range_index) != 0:
            error_type  = unsuitable_form(righ_tensor, 'Error')
            sgest_info  = f"the indexs '{', '.join(out_range_index)}' " \
                        + f"of '{righ_tensor}' is out of range, " \
                        + f"max size is {max_righ_size}.\n"
            report_error('FUF10', line_num, error_type + sgest_info)

    else:
        pass # righ_indexs = list(map(lambda x: x+1, range(righ_size)))

    # check size of left and right tensor
    if left_size != righ_size:
        error_type = unsuitable_form(left_tensor, 'Error')
        sgest_info = f"the size of '{left_tensor}' " \
                   + "is not consistent with the right indexs.\n"
        report_error('FUF11', line_num, error_type + sgest_info)
# end check_ftensor_assign_1_content()

# @A (fvect_i|fmatr_i_j) = [fvect_i|fmatr_i_j](/|*)(scal|vect_i|matr_i_j...) (+|-) ...
#
# @R (fvect_i|fmatr_i_j) = [disp(_i)(_j)(/coor(_i)(_j))](/|*)(scal|vect_i|matr_i_j...)
#                    (+|-) [func(_i)(_j)](/|*)(scal|vect_i|matr_i_j...) (+|-) ...
#
# @R (fvect_i|fmatr_i_j) [disp(/coor)] [func] ... descprit in doc
def check_ftensor_assign_2(code_strs, line_num, xde_dict, xde_addr, c_declares, atype):

    if code_strs.find('=') != -1:

        left_var, righ_expr = code_strs.split('=')

        left_var_type = left_var.count('_')

        error_report_list = []

        if   left_var_type == vector:
            tensor = left_var.strip().split('_')[0]
            check_tensor_not_declared(tensor, xde_dict['fvect'], 'fvect', error_report_list)

        elif left_var_type == matrix:
            tensor = left_var.strip().split('_')[0]
            check_tensor_not_declared(tensor, xde_dict['fmatr'], 'fmatr', error_report_list)

        else:
            error_type  = unsuitable_form(left_var, 'Error')
            sgest_info  = "Left variable must be declared by 'fvect' or 'fmatr'.\n"
            error_report_list.append(error_type + sgest_info)

        var_dict = {}
        classify_var_in_fassign(righ_expr, var_dict, c_declares, xde_dict)

        error_report_list += \
        check_fassign_right_expression_var(var_dict, line_num, xde_dict, xde_addr, c_declares)

        if len(error_report_list) != 0:
            strs = '\t'+'\t'.join(error_report_list)
            report_error('FXX12', line_num, f"error descript as:\n{strs}")

    else:
        if atype == '@r':

            temp_list = code_strs.split()
            try:
                left_var  = temp_list[0]
                righ_list = temp_list[1:]
            except IndexError:
                error_type  = unsuitable_form('', 'Error')
                sgest_info  = ["\tForm as a tensor expression: 'f_i = [a_i]*b_j + ...', \n", \
                               "\tor form as tensor assignment: 'f [a] [b] ...'.\n"]
                report_error('FUF13', line_num, error_type + '\n' + ''.join(sgest_info))

            else:

                left_len = 0

                if 'fvect' in xde_dict and left_var in xde_dict['fvect']:

                    left_len = xde_dict['fvect'][left_var][0]

                elif 'matr' in xde_dict and left_var in xde_dict['matr']:

                    left_len = xde_dict['fmatr'][left_var][0] \
                             * xde_dict['fmatr'][left_var][1]

                else:

                    error_type  = not_declared(left_var, 'Error')
                    sgest_info  = "It must be declared by 'fvect' or 'fmatr'.\n"
                    report_error('FND14', line_num, error_type + sgest_info)

                if left_len != 0 and left_len != len(righ_list):

                    error_type  = unsuitable_form('', 'Error')
                    sgest_info  = f"The following items must counted equals to the length of {left_var}.\n"
                    report_error('FUF15', line_num, error_type + sgest_info)

                else:

                    error_report_list = []

                    for item in righ_list:
                        var_dict = {}
                        classify_var_in_fassign(item, var_dict, c_declares, xde_dict)

                        error_report_list += \
                        check_fassign_right_expression_var(var_dict, line_num, xde_dict, xde_addr, c_declares)

                    if len(error_report_list) != 0:
                        strs = '\t'+'\t'.join(error_report_list)
                        report_error('FXX16', line_num, f"error descript as:\n{strs}")

        else:

            error_type  = unsuitable_form('', 'Error')
            report_error('FUF17', line_num, "Missing '=', it must be a tensor expression.\n")
# end check_ftensor_assign_2()
        
def add_var_not_declared(var, search_list, var_not_declare):
    if var.find('[') != -1:
        idx_list = re.findall(r'\[\d+\]',var,re.I)
        var = '*'*len(idx_list) + var.split('[')[0].strip()
    if var not in search_list:
        var_not_declare.add(var)
        return True
    else:
        return False
# end add_var_not_declared()

def check_tensor_not_declared(tensor, search_list, declaration, error_report_list):
    if tensor not in search_list:
        error_type  = not_declared(tensor, 'Error')
        sgest_info  = f"It must be declared by '{declaration}'"
        error_report_list.append(error_type + sgest_info + '\n')
        return True
    else:
        return False
# end check_tensor_not_declared()

def classify_var_in_fassign(righ_expr, var_dict, c_declares, xde_dict):
    
    var_dict['error'] = set()

    for var_type in ['disp', 'coor', 'valu', '', 'f']:
        for tensor_type in ['scal', 'vect', 'matr']:
            var_dict[var_type+tensor_type] = set()

    var_pattern = re.compile(r'\[\w+(?:/\w+)?\]?|\[?\w+(?:/\w+)?\]|\^?\w+')
    var_list = var_pattern.findall(righ_expr)

    for var in var_list:

        if is_number(var): 
            continue

        tensor_type = var.count('_')

        if var[0] == '[' or var[-1] == ']':

            if not (var[0] == '[' and var[-1] == ']'):
                var_dict['error'].add(var)

            var = var.lstrip('[').rstrip(']')

            if   var.count('/') == 0:
                classify_variable(var, var_dict, '', tensor_type, c_declares, xde_dict)

            elif var.count('/')  > 2:
                var_dict['error'].add(var)

            else:

                sub_var_list = var.lstrip('[').rstrip(']').split('/')

                for i,sub_var in enumerate(sub_var_list):

                    sub_var_type = sub_var.count('_')

                    if i == 0:
                        classify_variable(sub_var, var_dict, 'disp', sub_var_type, c_declares, xde_dict)

                    else:
                        classify_variable(sub_var, var_dict, 'coor', sub_var_type, c_declares, xde_dict)

        else:
            classify_variable(var, var_dict, 'valu', tensor_type, c_declares, xde_dict)
# end classify_var_in_fassign()

def classify_variable(var, var_dict, var_type, tensor_type, c_declares, xde_dict):
    tensor = var.split('_')[0]
    if   tensor_type == scalar:
        var_dict[var_type+'scal'].add(var)

    elif tensor_type == vector:
        var_dict[var_type+'vect'].add(tensor)

        if var_type != 'f' and 'fvect' in xde_dict and tensor not in xde_dict['fvect']:
            c_declares['tnsr_used']['vect'].add(var.split('_')[0])

    elif tensor_type == matrix:
        var_dict[var_type+'matr'].add(tensor)

        if var_type != 'f' and 'fvect' in xde_dict and tensor not in xde_dict['fmatr']:
            c_declares['tnsr_used']['matrix'].add(var.split('_')[0])

    else:
        var_dict['error'].add(var)
# end classify_variable()

def check_fassign_right_expression_var(var_dict, line_num, xde_dict, xde_addr, c_declares):
    
    error_report_list = []

    # check func, coor, normal type of tensor
    for var_type in ['disp', 'coor', 'valu']:

        for tensor_type in ['scal', 'vect', 'matr']:

            if var_type == 'valu':
                declaration_type = 'C code'
                var_search_list = c_declares['all']

                if tensor_type == 'vect':
                    tensor_search_list = list(c_declares['array']['vect'])

                    if 'vect' in xde_dict:
                        tensor_search_list += list(xde_dict['vect'].keys())

                elif tensor_type == 'matr':
                    tensor_search_list = list(c_declares['array']['matrix'])

                    if 'matrix' in xde_dict:
                        tensor_search_list += list(xde_dict['matrix'].keys())

            else:
                declaration_type = var_type
                var_search_list = xde_dict[var_type]

                tensor_search_list = []

                if tensor_type == 'vect':
                    if 'vect' in xde_dict:
                        tensor_search_list += list(xde_dict['vect'].keys())

                elif tensor_type == 'matr':
                    if 'matrix' in xde_dict:
                        tensor_search_list += list(xde_dict['matrix'].keys())

            var_key = var_type + tensor_type

            if   tensor_type == 'scal':

                var_not_declare = set()

                for var in var_dict[var_key]:
                    add_var_not_declared(var, var_search_list, var_not_declare)

                add_not_declare_report(var_not_declare, '', declaration_type, error_report_list)

            elif tensor_type == 'vect':

                for tensor in var_dict[var_key]:

                    if check_tensor_not_declared(tensor, tensor_search_list, tensor_type, error_report_list):
                        continue

                    if var_type == 'valu':
                        if tensor in c_declares['array']['vect']:
                            continue
                    
                    var_not_declare = set()
        
                    for var in xde_dict[tensor_type][tensor]:
                        add_var_not_declared(var, var_search_list, var_not_declare)

                    belong_descript = f" of {tensor}({xde_addr[tensor_type][tensor]})"
                    add_not_declare_report(var_not_declare, belong_descript, declaration_type, error_report_list)

            elif tensor_type == 'matr':

                tensor_type = 'matrix'

                for tensor in var_dict[var_key]:

                    if check_tensor_not_declared(tensor, tensor_search_list, tensor_type, error_report_list):
                        continue

                    if var_type == 'valu':
                        if tensor in c_declares['array']['matrix']:
                            continue

                    var_not_declare = set()

                    for row in xde_dict[tensor_type][tensor][2:]:
                        for var in row:
                            add_var_not_declared(var, var_search_list, var_not_declare)

                    belong_descript = f" of {tensor}({xde_addr[tensor_type][tensor]})"
                    add_not_declare_report(var_not_declare, belong_descript, declaration_type, error_report_list)

    # check unknown type of tensor
    solv_var_search_list = []
    if 'disp' in xde_dict:
        solv_var_search_list += xde_dict['disp']
    if 'func' in xde_dict:
        for func_list in xde_dict['func']:
            solv_var_search_list += func_list

    vect_search_list = []
    for key in ['fvect', 'vect']:
        if key in xde_dict:
            vect_search_list += list(xde_dict[key].keys())

    matr_search_list = []
    for key in ['fmatr', 'matrix']:
        if key in xde_dict:
            matr_search_list += list(xde_dict[key].keys())

    if len(var_dict['scal']) != 0:

        var_not_declare = set()

        for var in var_dict['scal']:
            add_var_not_declared(var, solv_var_search_list, var_not_declare)

        add_not_declare_report(var_not_declare, '', 'disp or func', error_report_list)

    if len(var_dict['vect']) != 0:

        for tensor in var_dict['vect']:

            if check_tensor_not_declared(tensor, vect_search_list, 'vect or fvect', error_report_list):
                continue

            if not ( 'fvect' in xde_dict and tensor in xde_dict['fvect']):

                var_not_declare = set()

                for var in xde_dict['vect'][tensor]:
                    add_var_not_declared(var, solv_var_search_list, var_not_declare)

                belong_descript = f" of {tensor}({xde_addr['vect'][tensor]})"
                add_not_declare_report(var_not_declare, belong_descript, 'disp or func', error_report_list)

    if len(var_dict['matr']) != 0:

        for tensor in var_dict['matr']:

            if check_tensor_not_declared(tensor, matr_search_list, 'matrix or fmatr', error_report_list):
                continue

            if not ( 'fmatr' in xde_dict and tensor in xde_dict['fmatr']):

                var_not_declare = set()

                for row in xde_dict[tensor_type][tensor][2:]:
                    for var in row:
                        add_var_not_declared(var, solv_var_search_list, var_not_declare)

                belong_descript = f" of {tensor}({xde_addr['matr'][tensor]})"
                add_not_declare_report(var_not_declare, belong_descript, 'disp or func', error_report_list)

    # check error items
    if len(var_dict['error']) != 0:
        error_type = unsuitable_form(','.join(var_dict['error']), 'Error')
        error_report_list.append(error_type)

    return error_report_list
# end check_fassign_right_expression_var()

def add_not_declare_report(var_not_declare, belong_descript, declaration_type, error_report_list):
    if len(var_not_declare) != 0:
        error_type  = not_declared(','.join(var_not_declare) + belong_descript, 'Error')
        sgest_info  = f"Must be declared by '{declaration_type}'.\n"
        error_report_list.append( error_type + sgest_info )
# end not_declare_report()

def check_weak(weak, xde_dict, xde_addr, c_declares):

    if   xde_dict[weak][0].lower() == 'null':
        return

    elif xde_dict[weak][0].lower() == 'dist':

        for weak_strs, line_num in zip(xde_dict[weak][1:], xde_addr[weak]):

            error_report_list = []

            for weak_item in split_bracket_expr(weak_strs):

                weak_pattern_str = r'\[?\w+(?:/\w+)?;?\w+(?:/\w+)?\]|\[\w+(?:/\w+)?;?\w+(?:/\w+)?\]?'
                weak_pattern = re.compile(weak_pattern_str, re.I)
                weak_form = set(weak_pattern.findall(weak_item))
                
                if len(weak_form) != 1:
                    error_type = unsuitable_form(weak_item, 'Error')
                    sgest_info = "one and only one '[*;*]' form in " \
                               + "a lowest priority expression.\n"
                    error_report_list.append(error_type + sgest_info)
                
                else:
                
                    miss_opr = [weak_opr for weak_opr in ['[',';',']'] \
                                    if weak_item.find(weak_opr) == -1]
                
                    if len(miss_opr) != 0:
                        error_type = unsuitable_form(weak_item, 'Error')
                        sgest_info = f"It miss {Empha_color}'{' '.join(miss_opr)}'.\n"
                        error_report_list.append(error_type + sgest_info)
                    
                weak_var_set = set()
                    
                for wset in weak_form:
                    weak_var_set |= set(map(lambda x:x.lstrip('[').rstrip(']') ,\
                                             wset.split(';')))

                var_dict = {}
                var_dict['error'] = set()

                for var_type in ['disp', 'coor', 'valu', '']:
                    for tensor_type in ['scal', 'vect', 'matr']:
                        var_dict[var_type+tensor_type] = set()

                weak_factor = re.sub(weak_pattern_str, '', weak_item,0, re.I)
                classify_var_in_weak_factor(weak_factor, var_dict, c_declares, xde_dict)

                classify_var_in_weak_item(weak_var_set, var_dict, c_declares, xde_dict)
            
            error_report_list += \
            check_var_in_weak_forms(var_dict, line_num, xde_dict, xde_addr, c_declares)

            if len(error_report_list) != 0:
                error_type = unsuitable_form(weak_item, 'Error')
                report_error('WUF01', line_num, 'errors descript:\n\t' + '\t'.join(error_report_list))

    else:

        if weak == 'stif':
            error_type = unsuitable_form(' '.join(xde_dict[weak]), 'Error')
            sgest_info = "'STIF' must be declared as paragraph, it is distributed.\n"
            report_error('WUF02', xde_addr[weak][0], error_type + sgest_info)

        error_report_list = []
        line_num   = xde_addr[weak]
        coeff_len = len(xde_dict[weak]) - 1

        if 'disp' in xde_dict \
        and coeff_len > 1 \
        and coeff_len < len(xde_dict['disp']):

            no_coeff_var = xde_dict['disp'][coeff_len:]
            no_mass_list = ['0' for i in range(len(no_coeff_var))]

            error_type = unsuitable_form(' '.join(xde_dict[weak]), 'Error')
            sgest_info = f"Not enough '{weak}' coefficient for 'disp' " \
                       + f"declaration at {Empha_color}{xde_addr['disp']}. " \
                       + f"{Error_color}If '{' '.join(no_coeff_var)}' have no " \
                       + f"'{weak}', it's better declared as {Empha_color}'{weak} " \
                       + f"{' '.join(xde_dict[weak] + no_mass_list)}'.\n"
            report_error('WUF03', line_num, error_type + sgest_info)

        error_report_list += \
        check_assignment_weak_form(xde_dict[weak], c_declares)

        if len(error_report_list) != 0:
            error_type = unsuitable_form('', 'Error')
            report_error('WUF07', line_num, 'errors descript:\n\t' + '\t'.join(error_report_list))
# end check_weak()

def classify_var_in_weak_factor(weak_factor, var_dict, c_declares, xde_dict):
    
    var_list = re.findall(r'\^?\w+', weak_factor)

    for var in var_list:

        if is_number(var):
            continue

        tensor_type = var.count('_')

        classify_variable(var, var_dict, 'valu', tensor_type, c_declares, xde_dict)
# end classify_var_in_weak()

def classify_var_in_weak_item(weak_var_set, var_dict, c_declares, xde_dict):

    for var in weak_var_set:

        if var.count('/') == 0:

            tensor_type = var.count('_')

            classify_variable(var, var_dict, '', tensor_type, c_declares, xde_dict)

        elif var.count('/')  > 2:
            var_dict['error'].add(var)

        else:

            sub_var_list = var.lstrip('[').rstrip(']').split('/')

            for i,sub_var in enumerate(sub_var_list):

                sub_var_type = sub_var.count('_')

                if i == 0:
                    classify_variable(sub_var, var_dict, 'disp', sub_var_type, c_declares, xde_dict)

                else:
                    classify_variable(sub_var, var_dict, 'coor', sub_var_type, c_declares, xde_dict)
# end classify_var_in_weak_item() 

def check_var_in_weak_forms(var_dict, line_num, xde_dict, xde_addr, c_declares):

    error_report_list = []

    # check func, coor, normal type of tensor
    for var_type in ['disp', 'coor', 'valu']:

        for tensor_type in ['scal', 'vect', 'matr']:

            if var_type == 'valu':
                declaration_type = 'C code'
                var_search_list = c_declares['all']

                if tensor_type == 'vect':
                    tensor_search_list = list(c_declares['array']['vect'])

                    if 'vect' in xde_dict:
                        tensor_search_list += list(xde_dict['vect'].keys())

                elif tensor_type == 'matr':
                    tensor_search_list = list(c_declares['array']['matrix'])

                    if 'matrix' in xde_dict:
                        tensor_search_list += list(xde_dict['matrix'].keys())
                        
            else:
                declaration_type = var_type
                var_search_list = xde_dict[var_type]

                tensor_search_list = []

                if tensor_type == 'vect':
                    if 'vect' in xde_dict:
                        tensor_search_list += list(xde_dict['vect'].keys())

                elif tensor_type == 'matr':
                    if 'matrix' in xde_dict:
                        tensor_search_list += list(xde_dict['matrix'].keys())

            var_key = var_type + tensor_type

            if   tensor_type == 'scal':

                var_not_declare = set()

                for var in var_dict[var_key]:
                    add_var_not_declared(var, var_search_list, var_not_declare)

                add_not_declare_report(var_not_declare, '', declaration_type, error_report_list)

            elif tensor_type == 'vect':

                for tensor in var_dict[var_key]:

                    if check_tensor_not_declared(tensor, tensor_search_list, tensor_type, error_report_list):
                        continue

                    if var_type == 'valu':
                        if tensor in c_declares['array']['vect']:
                            continue
                    
                    var_not_declare = set()
        
                    for var in xde_dict[tensor_type][tensor]:
                        add_var_not_declared(var, var_search_list, var_not_declare)

                    belong_descript = f" of {tensor}({xde_addr[tensor_type][tensor]})"
                    add_not_declare_report(var_not_declare, belong_descript, declaration_type, error_report_list)

            elif tensor_type == 'matr':

                tensor_type = 'matrix'

                for tensor in var_dict[var_key]:

                    if check_tensor_not_declared(tensor, tensor_search_list, tensor_type, error_report_list):
                        continue

                    if var_type == 'valu':
                        if tensor in c_declares['array']['matrix']:
                            continue

                    var_not_declare = set()

                    for row in xde_dict[tensor_type][tensor][2:]:
                        for var in row:
                            add_var_not_declared(var, var_search_list, var_not_declare)

                    belong_descript = f" of {tensor}({xde_addr[tensor_type][tensor]})"
                    add_not_declare_report(var_not_declare, belong_descript, declaration_type, error_report_list)

    # check unknown type of tensor
    solv_var_search_list = []
    if 'disp' in xde_dict:
        solv_var_search_list += xde_dict['disp']
    if 'func' in xde_dict:
        for func_list in xde_dict['func']:
            solv_var_search_list += func_list

    vect_search_list = xde_dict['vect'].keys()

    matr_search_list = xde_dict['matrix'].keys()

    if len(var_dict['scal']) != 0:

        var_not_declare = set()

        for var in var_dict['scal']:
            add_var_not_declared(var, solv_var_search_list, var_not_declare)

        add_not_declare_report(var_not_declare, '', 'disp or func', error_report_list)

    if len(var_dict['vect']) != 0:

        for tensor in var_dict['vect']:

            if check_tensor_not_declared(tensor, vect_search_list, 'vect', error_report_list):
                continue

            var_not_declare = set()

            for var in xde_dict['vect'][tensor]:
                add_var_not_declared(var, solv_var_search_list, var_not_declare)

            belong_descript = f" of {tensor}({xde_addr['vect'][tensor]})"
            add_not_declare_report(var_not_declare, belong_descript, 'disp or func', error_report_list)

    if len(var_dict['matr']) != 0:

        for tensor in var_dict['matr']:

            if check_tensor_not_declared(tensor, matr_search_list, 'matrix', error_report_list):
                continue

            var_not_declare = set()

            for row in xde_dict[tensor_type][tensor][2:]:
                for var in row:
                    add_var_not_declared(var, solv_var_search_list, var_not_declare)

            belong_descript = f" of {tensor}({xde_addr['matr'][tensor]})"
            add_not_declare_report(var_not_declare, belong_descript, 'disp or func', error_report_list)

    # check error items
    if len(var_dict['error']) != 0:
        error_type = unsuitable_form(','.join(var_dict['error']), 'Error')
        error_report_list.append(error_type + '\n')

    return error_report_list
# end check_weak_item()

def check_assignment_weak_form(weak_factor_list, c_declares):
    
    error_report_list = []

    for weak_factor in weak_factor_list:

        if is_number(weak_factor):
            continue

        fucntion_list = re.findall(r'\w+\([\w,]+\)?', weak_factor)

        for strs in fucntion_list:

            weak_factor = weak_factor.replace(strs,'')

            var_list = strs.rstrip(')').split('(')[1].split(',')

            if len(var_list) != 0:

                for var in var_list:

                    if is_number(weak_factor):
                        continue

                    if var not in c_declares['all']:

                        error_type = not_declared(var, 'Error')
                        error_report_list.append(error_type + 'It must be declared in C code.\n')


        for var in re.findall(r'\w+', weak_factor):

            if is_number(var):
                continue

            if var.find('_') != -1:

                error_type = unsuitable_form(var, 'Error')
                error_report_list.append(error_type + 'No tensor allowed in this form.\n')

            else:

                if var not in c_declares['all']:

                    error_type = not_declared(var, 'Error')
                    error_report_list.append(error_type + 'It must be declared in C code.\n')

    return error_report_list
# end check_assignment_weak_form()

def check_load(xde_dict, xde_addr, c_declares):

    if xde_dict['load'][0].find('_') != -1:

        for weak_strs, line_num in zip(xde_dict['load'], xde_addr['load']):

            error_report_list = []

            for weak_item in split_bracket_expr(weak_strs):

                weak_pattern_str = r'\[\w+(?:/\w+)?\]?|\[?\w+(?:/\w+)?\]'
                weak_pattern = re.compile(weak_pattern_str, re.I)
                weak_form = set(weak_pattern.findall(weak_item))

                if len(weak_form) != 1:
                    error_type = unsuitable_form(weak_item, 'Error')
                    sgest_info = "one and only one '[*]' form in " \
                               + "a lowest priority expression.\n"
                    error_report_list.append(error_type + sgest_info)

                else:

                    miss_opr = [weak_opr for weak_opr in ['[',']'] \
                                    if weak_item.find(weak_opr) == -1]

                    if len(miss_opr) != 0:
                        error_type = unsuitable_form(weak_item, 'Error')
                        sgest_info = f"It miss {Empha_color}'{' '.join(miss_opr)}'.\n"
                        error_report_list.append(error_type + sgest_info)

                weak_var_set = set(map(lambda x: x.lstrip('[').rstrip(']'), weak_form))

                var_dict = {}
                var_dict['error'] = set()

                for var_type in ['disp', 'coor', 'valu', '']:
                    for tensor_type in ['scal', 'vect', 'matr']:
                        var_dict[var_type+tensor_type] = set()

                weak_factor = re.sub(weak_pattern_str, '', weak_item,0, re.I)
                classify_var_in_weak_factor(weak_factor, var_dict, c_declares, xde_dict)

                classify_var_in_weak_item(weak_var_set, var_dict, c_declares, xde_dict)

            error_report_list += \
            check_var_in_weak_forms(var_dict, line_num, xde_dict, xde_addr, c_declares)

            if len(error_report_list) != 0:
                error_type = unsuitable_form(weak_item, 'Error')
                report_error('WUF04', line_num, 'errors descript:\n\t' + '\t'.join(error_report_list))
    
    else :
        error_report_list = []
        line_num   = xde_addr['load'][0]
        coeff_len = len(xde_dict['load'])

        if 'disp' in xde_dict \
        and coeff_len > 1 \
        and coeff_len < len(xde_dict['disp']):

            no_coeff_var = xde_dict['disp'][coeff_len:]
            no_mass_list = ['0' for i in range(len(no_coeff_var))]

            error_type = unsuitable_form(' '.join(xde_dict['load']), 'Error')
            sgest_info = f"Not enough 'load' coefficient for 'disp' " \
                       + f"declaration at {Empha_color}{xde_addr['disp']}. " \
                       + f"{Error_color}If '{' '.join(no_coeff_var)}' have no " \
                       + f"'load', it's better declared as {Empha_color}'load " \
                       + f"{' '.join(xde_dict['load'] + no_mass_list)}'.\n"
            report_error('WUF05', line_num, error_type + sgest_info)

        error_report_list += \
        check_assignment_weak_form(xde_dict['load'], c_declares)

        if len(error_report_list) != 0:
            error_type = unsuitable_form('', 'Error')
            report_error('WUF06', line_num, 'errors descript:\n\t' + '\t'.join(error_report_list))
# end check_load()

def is_number(strs):

    pattern = re.compile(r'^[-+]?(?:\d+(\.\d*)?|\.\d+)(e\d+)?$')
    matched = pattern.match(strs)
    if matched:
        return True
    else:
        return False        
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
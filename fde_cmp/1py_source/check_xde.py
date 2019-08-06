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
    print(c_declares)



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
                    | {'ngaus','igaus','det','ndisp','nrefc','ncoor'}

    # gather C declares and check code
    c_declares['all']    = inner_declares.copy()
    c_declares['BFmate'] = inner_declares.copy()
    c_declares['array']  = {}
    c_declares['array']['vect'] = set()
    c_declares['array']['matrix'] = set()

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
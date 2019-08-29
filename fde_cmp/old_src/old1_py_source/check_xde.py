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

color={'Error':Fore.MAGENTA,'Warnn':Fore.CYAN,'Empha':Fore.GREEN}

import re as regx
def check_xde(xde_lists,list_addr,shap_tag,gaus_tag):

    error = False

    all_declares  = {'tmax','dt','nstep','itnmax','time'}
    all_declares |= {'tolerance','dampalfa','dampbeta'}
    all_declares |= {'it','stop','itn','end'}
    all_declares |= {'imate','nmate','nelem','num','nvar','nnode'}
    all_declares |= {'ngaus','igaus','det','ndisp','nrefc','ncoor'}

    # gather C declares
    c_declares = {}
    c_dclr_key = r"int|long|short|double|float"
    c_dclr_exp = r"[a-z].*="
    for keys in xde_lists["code"].keys():
        c_declares[keys] = set()
        for strs,line_num in zip(xde_lists["code"][keys],list_addr["code"][keys]):
            dclr_regx = regx.search(c_dclr_key,strs,regx.I)
            if dclr_regx != None:
                dclr_key = dclr_regx.group()
                varas = regx.split(dclr_key,strs.rstrip(';'))[-1]

                def trans(matched):
                    index_str = matched.group('index')
                    index_str = ','
                    return index_str

                varas = regx.sub(r'(?P<index>(=.*,?)+)',trans,varas)

                var_list = varas.split(',')
                if '' in var_list: var_list.remove('')

                for var in var_list:
                    if regx.search(c_dclr_exp, var, regx.I) != None:
                        temp_var = var.split('=')[0].strip()
                    else: temp_var = var.strip()

                    if temp_var.find('[') != -1:
                        temp_var = temp_var.split('[')[0]

                    if temp_var in all_declares:
                        duplicate_declare(line_num,temp_var,'\n')
                    else: all_declares.add(temp_var)

                    c_declares[keys].add(temp_var)

    # gather all declares
    for strs in ["disp","coef","coor","func"]:
        if strs in xde_lists:
            all_declares |= set(xde_lists[strs])

    # check mate
    is_var = r'[a-z]\w*'
    for vara in xde_lists['mate']:
        if regx.match(is_var,vara,regx.I) != None :
            if vara not in c_declares['BFmate']:
                not_declare(list_addr['mate'],vara,'\n')

    # check vect
    if 'vect' in xde_lists:
        for vect in xde_lists['vect'].keys():
            for strs in xde_lists['vect'][vect]:
                for vara in regx.findall(r'[a-z]\w*',strs,regx.I):
                    if vara not in all_declares:
                        not_declare(list_addr['vect'][vect],vara,'\n')

    # check matrix
    if 'matrix' in xde_lists:
        for matrix in xde_lists['matrix'].keys():
            line_nums = list_addr['matrix'][matrix].copy()
            line_nums.pop(0)
            for lists,num in zip(xde_lists['matrix'][matrix],line_nums):
                for strs in lists.split():
                    for vara in regx.findall(r'[a-z]\w*',strs,regx.I):
                        if vara not in all_declares:
                            not_declare(num,vara,'\n')

    # check disp
    if 'disp' in xde_lists:
        pass
    else:
        addon_info = 'may be declared as '
        not_declare('*','disp var','may be declared as \'DISP * *\' in the first garaph, and \'* *\' could be referened in \'mdi\' file.\n')
        error = True

    # check coor
    if 'coor' in xde_lists:
        pass
    else:
        not_declare('*','coor var','may be declared as \'COOR * *\' in the first garaph, and \'* *\' could be referened in \'mdi\' file.\n')
        error = True

    # check shap
    if 'shap' in xde_lists:
        nodn = regx.search(r'[1-9]+',shap_tag,regx.I).group()

        for shap_list,num in zip(xde_lists['shap'],list_addr['shap']):

            if shap_list[0] == '%1':
                  shap_shap = shap_tag[0]
            else: shap_shap = shap_list[0]

            shap_node   = [['%2','2','3'], ['%2','3','6'], ['%2','4','9'], \
                          ['%2','4','10'], ['%2','8','27'] ]
            shap_type     = ['l','t','q','w','c']
            node_dgree1   = ['2','3','4','4','8']
            node_dgree1_5 = ['' ,'' ,'8','' ,'20']
            node_dgree2   = ['3','6','9','10','27']

            # base shap declare
            if len(shap_list) == 2:
                base_shap_type = shap_shap
                if shap_list[1] == '%2':
                      base_shap_node = regx.search(r'[1-9]+',shap_tag,regx.I).group()
                else: base_shap_node = shap_list[1]
                base_shap_line = num

                if shap_shap not in shap_type:
                    fault_declare(num,'shap','suggested format is \'SHAP %1 %2\'.\n')

                for stype,snodn in zip(shap_type, shap_node):
                   if shap_shap == stype:
                       if shap_list[1] not in snodn:
                           fault_declare(num,'shap', \
                               'suggested format is \'SHAP {} {}\'.\n'.format(shap_list[0],str(snodn)))

            # advance shap declare
            elif len(shap_list) >= 3:
                if shap_shap != base_shap_type:
                    fault_declare(num,'shap', \
                        'the first variable must be same to base shap declared at line' \
                            + Empha_color +' {}\n'.format(base_shap_line))

                # sub shap declare using mix element
                if shap_list[1] == '%4' or shap_list[1].isnumeric():

                    var_list = shap_list[2:len(shap_list)]
                    if len(set(var_list)) != len(var_list):
                        warn_form(num, '', 'variable duplicated.\n')

                    for var_name in set(var_list):
                        if var_name.isnumeric(): continue

                        if 'coef' not in xde_lists:
                            if var_name not in xde_lists['disp'] :
                                wnot_declare(num,var_name,'It must be declared in disp.\n')
                        else:
                            if  var_name not in xde_lists['disp'] \
                            and var_name not in xde_lists['coef'] :
                                wnot_declare(num,var_name,'It must be declared in disp or coef.\n')

                    for stype,snodn,subnod in zip(shap_type,node_dgree2,node_dgree1):
                        if base_shap_type == stype :

                            # base shap is not degree 2 or not coordinate with shap_type
                            if base_shap_node != snodn :
                                addon_info  = 'using mix degree element, the second variable of base shap must to be '
                                addon_info += Empha_color + snodn
                                addon_info += Error_color + ' at line '
                                addon_info += Empha_color + str(base_shap_line) + '.\n'
                                fault_declare(num,'shap', addon_info)

                            # sub shap is not coordinate with base or not coordinate with shap_type
                            elif base_shap_node == snodn \
                            and shap_list[1].isnumeric() \
                            and shap_list[1] != subnod:
                                addon_info  = 'using mix degree element, the second variable must to be '
                                addon_info += Empha_color + subnod + ', '
                                addon_info += Error_color + 'because base shap node is '
                                addon_info += Empha_color + base_shap_node + ', '
                                addon_info += Error_color + 'and base shap type is '
                                addon_info += Empha_color + base_shap_type + '.\n'
                                fault_declare(num,'shap', addon_info)

                # penalty disp var shap declare
                elif shap_list[1] == '%2c' \
                or  (shap_list[1][-1] == 'c' \
                and  shap_list[1][:-1].isnumeric) :

                    if base_shap_node in node_dgree2:
                        warn_form(base_shap_line,'','must to be linear shap function.\n')
                    if shap_list[1][:-1].replace('%2',nodn) in node_dgree2:
                        warn_form(num,'','must to be linear shap function.\n')

                    var_list = shap_list[2:len(shap_list)]
                    pena_var_list = []
                    for var in var_list:
                        if var.isnumeric(): continue
                        if shap_list[2].find('_'):
                            pena_var_list.append(shap_list[2].split('_')[0])
                        else: pena_var_list.append(shap_list[2])

                    if len(set(pena_var_list)) != len(pena_var_list):
                        warn_form(num, '', 'variable duplicated.\n')

                    for var_name in set(pena_var_list):

                        if var_name not in xde_lists['disp'] :
                            warn_form(num,'',Empha_color + var_name +\
                                Warnn_color + ' must be declared in disp.\n')  

                        if 'coef' in xde_lists \
                        and var_name in xde_lists['coef'] :
                            warn_form(num,'',Empha_color + var_name +\
                                Warnn_color + ' must not be declared in coef.\n')







    else:
        not_declare('*','shap func','may be declared as \'SHAP %1 %2\' in the first garaph')
        error = True


    return error






def error(func):
    def _error(*args, **argv):
        output_words =  Error_color + 'error: line number '
        output_words += Empha_color + str(args[0]) +', '
        output_words += Error_color + func(*args, **argv)
        print(output_words)
    return _error

@error
def not_declare(line_num, declare_name, addon_info):
    return Empha_color + declare_name \
         + Error_color + " not be declared. {}".format(addon_info)

@error
def fault_declare(line_num, declare_name, addon_info):
    return Empha_color + declare_name \
         + Error_color + " faultly declared. {}".format(addon_info)

@error
def error_form(line_num, form_info, addon_info):
    return Empha_color + form_info \
         + Error_color + " error form. {}".format(addon_info)


def warn(func):
    def _warn(*args, **argv):
        output_words =  Warnn_color + 'warn: line number '
        output_words += Empha_color + str(args[0]) + ', '
        output_words += Warnn_color + func(*args, **argv)
        print(output_words)
    return _warn

@warn
def duplicate_declare(line_num, declare_name, addon_info):
    return Empha_color + declare_name \
         + Warnn_color + " is duplicately declared. {}".format(addon_info)

@warn
def wnot_declare(line_num, declare_name, addon_info):
    return Empha_color + declare_name \
         + Warnn_color + " not be declared. {}".format(addon_info)

@warn
def warn_form(line_num, form_info, addon_info):
    return Empha_color + form_info \
         + Warnn_color + " not suitable form. {}".format(addon_info)
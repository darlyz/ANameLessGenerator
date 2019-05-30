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
Empha_color = Fore.BLUE

import re as regx
def check_xde(xde_lists,list_addr,shap_tag,gaus_tag):

    error = False

    # gather C declares
    c_declares = {}
    c_dclr_key = r"int|long|short|double|float"
    for keys in xde_lists["code"].keys():
        c_declares[keys] = []
        for strs in xde_lists["code"][keys]:
            dclr_regx = regx.search(c_dclr_key,strs,regx.I)
            if dclr_regx != None:
                dclr_key = dclr_regx.group()
                varas = regx.split(dclr_key,strs.rstrip(';'))[-1]
                c_declares[keys] += varas.split(',')
        for ii in range(len(c_declares[keys])):
            c_declares[keys][ii] = c_declares[keys][ii].strip()

    # gather all declares
    declares = []
    for keys in xde_lists["code"].keys():
        declares += c_declares[keys]
    for strs in ["disp","coef","coor","func"]:
        if strs in xde_lists:
            declares += xde_lists[strs]

    # check mate
    is_var = r'[a-z]\w*'
    for vara in xde_lists['mate']:
        if regx.match(is_var,vara,regx.I) != None :
            if vara not in c_declares['BFmate']:
                not_declare(list_addr['mate'],vara,'')

    # check vect
    if 'vect' in xde_lists:
        for vect in xde_lists['vect'].keys():
            for strs in xde_lists['vect'][vect]:
                for vara in regx.findall(r'[a-zA-z]\w*',strs,regx.I):
                    if vara not in declares:
                        not_declare(list_addr['vect'][vect],vara,'')

    # check matrix
    if 'matrix' in xde_lists:
        for matrix in xde_lists['matrix'].keys():
            line_nums = list_addr['matrix'][matrix].copy()
            line_nums.pop(0)
            for lists,num in zip(xde_lists['matrix'][matrix],line_nums):
                for strs in lists.split():
                    for vara in regx.findall(r'[a-zA-z]\w*',strs,regx.I):
                        if vara not in declares:
                            not_declare(num,vara,'')

    # check disp
    if 'disp' in xde_lists:
        pass
    else:
        addon_info = 'may be declared as '
        not_declare('*','disp var','may be declared as \'DISP * *\' in the first garaph, and \'* *\' could be referened in \'mdi\' file')
        error = True
    
    # check coor
    if 'coor' in xde_lists:
        pass
    else:
        not_declare('*','coor var','may be declared as \'COOR * *\' in the first garaph, and \'* *\' could be referened in \'mdi\' file')
        error = True

    # check shap
    if 'shap' in xde_lists:
        for shap_list,num in zip(xde_lists['shap'],list_addr['shap']):
            
            if shap_list[0] == '%1':
                  shap_shap = shap_tag[0]
            else: shap_shap = shap_list[0]

            shap_type = ['l','t','q','w','c']
            shap_node = [['%2','2','3'], ['%2','3','6'], ['%2','4','9'], \
                        ['%2','4','10'], ['%2','8','27'] ]

            if len(shap_list) == 2:
                base_shap_type = shap_shap
                if shap_list[1] == '%2':
                      base_shap_node = regx.search(r'[1-9]+',shap_tag,regx.I).group()
                else: base_shap_node = shap_list[1]
                base_shap_line = num

                if shap_shap not in shap_type:
                    fault_declare(num,'shap','suggested format is \'SHAP %1 %2\'.')

                for stype,snodn in zip(shap_type, shap_node):
                   if shap_shap == stype:
                       if shap_list[1] not in snodn:
                           fault_declare(num,'shap', \
                               'suggested format is \'SHAP {} {}\'.'.format(shap_list[0],str(snodn)))
            
            elif len(shap_list) >= 3:
                if shap_shap != base_shap_type:
                    fault_declare(num,'shap', \
                        'the first variable must be same to base shap declared at line' \
                            + Empha_color +' {}'.format(base_shap_line))

                if shap_list[1] == '%4' or shap_list[1].isnumeric():
                    for stype,snodn,subnod in zip(shap_type,['3','6','9','10','27'],['2','3','4','4','8']):
                        if base_shap_type == stype :
                            if base_shap_node != snodn :
                                addon_info  = 'using mix degree element, the second variable of base shap must to be '
                                addon_info += Empha_color + snodn
                                addon_info += Error_color + ' at line '
                                addon_info += Empha_color + str(base_shap_line) + '.'
                                fault_declare(num,'shap', addon_info)
                            elif base_shap_node == snodn \
                            and shap_list[1].isnumeric() \
                            and shap_list[1] != subnod:
                                addon_info  = 'using mix degree element, the second variable must to be '
                                addon_info += Empha_color + subnod +'.'
                                fault_declare(num,'shap', addon_info)
                elif shap_list[1] == '%2c' or regx.match(r'[0-9]+c',shap_list[1],regx.I) != None:
                    print(shap_list[1],shap_list[2])

                    

    else:
        not_declare('*','shap func','may be declared as \'SHAP %1 %2\' in the first garaph')
        error = True


    return error




def error(func):
    def _error(*args, **argv):
        output_words =  Error_color + 'error: line number '
        output_words += Empha_color + str(args[0])+', '
        output_words += Error_color + func(*args, **argv)
        print(output_words)
    return _error

@error
def not_declare(line_num, declare_name, addon_info):
    return Empha_color+ '\'' + str(declare_name) + '\'' \
        + Error_color + " not be declared. {}".format(addon_info)

@error
def fault_declare(line_num, declare_name, addon_info):
    return Empha_color+ '\'' + str(declare_name) + '\'' \
        + Error_color + " faultly declared. {}".format(addon_info)
'''
 Copyright: Copyright (c) 2019
 Created: 2019-3-30
 Author: Zhang_Licheng
 Title: parse the xde file and check it
 All rights reserved
'''
from colorama import init, Fore, Back, Style
init(autoreset=True)
Error_color = Fore.MAGENTA
Warnn_color = Fore.CYAN
Empha_color = Fore.GREEN

import re
import json
from genxde import gen_obj, ifo_folder
from check_xde import check_xde

dict_check = {'pre':0, 'sec':0, 'fnl':1}
addr_check = {'pre':0, 'sec':0, 'fnl':1}

scalar = 0
vector = 1
matrix = 2

def parse_xde(ges_info, xde_dict, xde_addr, xdefile):

    # parse xde to features and workflow features
    # just push the sentence into dict
    # report the meaningless sentence and paragraph declaration error
    pre_parse(xde_dict, xde_addr, xdefile)

    # a simple parsing feature sentence to list
    # and check the duplicated of some feature declaration
    sec_parse(xde_dict, xde_addr)
    
    # fully check all features 
    if gen_obj['check'] > 0:
        if check_xde(ges_info, xde_dict, xde_addr):
            return True
 
    # parse features into a readable and transable style
    fnl_parse(ges_info, xde_dict, xde_addr)

    return False

def pre_parse(xde_dict, xde_addr, xdefile):

    # all the xde keys
    key_pattern  = r'ARRAY|COEF|COOR|COMMON|DAMP' \
                 + r'|DEFI|DISP|DIST|END|USERC|' \
                 + r'FUNC|FVECT|FMATR|GAUS|LOAD|' \
                 + r'MATE|MASS|MATRIX|SHAP|STIF|VECT|' \
                 + r'\$C[CPV6]|\$I|@[LAWSR]'

    keywd_tag = {'bf_matrix'   : '', \
                 'paragraph'   : 'BFmate',\
    }

    line_i = 0
    stitchline = ''
    xde_dict['code'] = {}
    xde_addr['code'] = {}

    # parsing while read xde to xde_dict
    for line in xdefile.readlines():
        line_i += 1

        # skip comment line and blank line
        if re.match(r'\s*(\$c[c6])?\s*((\\|//).*)?\s*\n',line,re.I) != None:
            continue

        # deal with valid sentence with comment
        # identify comment and stitch the next line begin with '\'
        line = stitchline + line
        if line.find('\\') != -1 :
            stitchline = line.split('\\')[0]
            continue
        else: stitchline = ''

        # identify comment begin with '//'
        if line.find('//') != -1:
            line = line.split('//')[0]

        # pop the space from head and tail
        line = line.strip()

        # retrieve the keywords
        matched_key = re.match(key_pattern, line, re.I)

        # find the keyword at the head
        if matched_key != None:

            key_match = matched_key.group()
            key_lower = key_match.lower()

            # match and pop to xde_dict
            if key_lower in ['disp','coef','coor','gaus','shap','fmatr','fvect','vect']:
                push_keyword_declaration(xde_dict, xde_addr, key_lower, line, line_i)

            if key_lower in ['mass','damp','stif']:
                push_keyword_declaration(xde_dict, xde_addr, key_lower, line, line_i)
                if key_lower == line.lower():
                    keywd_tag['paragraph'] = key_lower

            elif key_lower == 'mate':

                if keywd_tag['paragraph'] != 'BFmate':
                    print(f"{Error_color}Error PRE01: if other " \
                        + "paragraph is writed before definition, " \
                        + "key word 'DEFI' should not be ommited before " \
                        + "'MATE' line and C insertion for 'MATE'.\n")

                line = re.sub(r'[\;\,]',' ',line)

                push_keyword_declaration(xde_dict, xde_addr, key_lower, line, line_i)

                keywd_tag['paragraph'] = 'AFmate'

            elif key_lower.find('$')!= -1 \
            or   key_lower.find('@')!= -1:
                push_workflow_code(xde_dict, xde_addr, keywd_tag, line, line_i)

                if key_lower == '$cp':
                    xde_dict['cmplx_tag'] = 1

            elif key_lower in ['common','array']:

                push_workflow_code(xde_dict, xde_addr, keywd_tag, line, line_i)

                if key_lower == 'array':
                    push_keyword_declaration(xde_dict, xde_addr, key_lower, line, line_i)

            elif key_lower == 'dist':

                if line.find('|') != -1:
                    xde_dict['cmplx_tag'] = 1

                if keywd_tag['paragraph'] in ['mass','damp','stif']:
                    xde_dict[keywd_tag['paragraph']].append(line)
                    xde_addr[keywd_tag['paragraph']].append(line_i)

            elif key_lower == 'load':

                if line.find('|') != -1:
                    xde_dict['cmplx_tag'] = 1

                if not 'load' in xde_dict:
                    xde_dict['load'] = []
                    xde_addr['load'] = []

                xde_dict['load'].append(line)
                xde_addr['load'].append(line_i)
                if line.find('=') != -1:
                    keywd_tag['paragraph'] = 'load'

            elif key_lower == 'func':

                if key_lower == line.lower():
                    keywd_tag['paragraph'] = 'func'

                else:
                    if not 'func' in xde_dict:
                        xde_dict['func'] = []
                        xde_addr['func'] = []
                    xde_dict['func'].append(line)
                    xde_addr['func'].append(line_i)

            elif key_lower == 'matrix':

                if keywd_tag['paragraph'] != 'matrix':
                    keywd_tag['bf_matrix'] = keywd_tag['paragraph']

                push_keyword_declaration(xde_dict, xde_addr, key_lower, line, line_i)

                keywd_tag['paragraph'] = 'matrix'

            elif key_lower == 'defi':
                keywd_tag['paragraph'] = 'BFmate'

            elif key_lower == 'end':
                pass

            elif key_lower == 'userc':
                pass

        # find the non-keyword-head line in 'func' 'stif' 'mass', 'damp' and 'matrix' paragraph
        else:

            # find cmplx_tag tag
            if line.find('|') != -1:
                xde_dict['cmplx_tag'] = 1

            paragraph_key = keywd_tag['paragraph']

            # find weak form and disp var deform in non-keyword-head line
            if  paragraph_key in ['mass','damp','stif','load'] \
            and paragraph_key in xde_dict:

                xde_dict[paragraph_key].append(line)
                xde_addr[paragraph_key].append(line_i)

            elif  paragraph_key == 'func':
                xde_dict['code'][paragraph_key].append(line)
                xde_addr['code'][paragraph_key].append(line_i)

            elif paragraph_key == 'matrix' :
                xde_dict['matrix'].append(line)
                xde_addr['matrix'].append(line_i)

            else:
                print(f'{Warnn_color}Warn PRE03: redundant information ' \
                     + 'or wrong declare, line {line_i}: ' + line)

    export_parsing_result('pre', xde_dict, xde_addr)
# end pre_parse()

def push_keyword_declaration(xde_dict, xde_addr, keyword, line_str, line_num):
    if  keyword not in xde_dict:
        xde_dict[keyword] = []
        xde_addr[keyword] = []
    xde_dict[keyword].append(line_str)
    xde_addr[keyword].append(line_num)
# end push_keyword_declaration()

def push_workflow_code(xde_dict, xde_addr, keywd_tag, line_str, line_num):
    code_find = 0
    paragraph_key = keywd_tag['paragraph']

    # tackle that code line write between matrix and other paragraph
    if  paragraph_key == 'matrix':
        paragraph_key = keywd_tag['bf_matrix']

    if  paragraph_key in ['BFmate','AFmate','func','stif','mass','damp']:

        code_find = 1

        if paragraph_key not in xde_dict['code']:
            xde_dict['code'][paragraph_key] = []
            xde_addr['code'][paragraph_key] = []

        xde_dict['code'][paragraph_key].append(line_str)
        xde_addr['code'][paragraph_key].append(line_num)

    if  code_find == 0:
        print(f'{Error_color}Error PRE02: line {Empha_color}{line_num}, ' \
            + f'{Error_color}wrong position inserted.\n')
# end push_workflow_code()

def sec_parse(xde_dict, xde_addr):

    for keyword in xde_dict.keys():

        if keyword in ['disp','coef','coor','gaus','mate']:

            if len(xde_dict[keyword]) > 1:
                declared_linenum   = xde_addr[keyword][0]
                duplicated_linenum = ','.join(map(str,xde_addr[keyword][1:]))
                report_duplicated_declaration(keyword, declared_linenum, duplicated_linenum)
            
            xde_dict[keyword] = xde_dict[keyword][0].split()[1:]
            xde_addr[keyword] = xde_addr[keyword][0]

        elif keyword == 'vect':

            vect_list = xde_dict['vect'].copy()
            vect_addr = xde_addr['vect'].copy()

            xde_dict['vect'].clear()
            xde_addr['vect'].clear()
            
            xde_dict['vect'] = {}
            xde_addr['vect'] = {}

            for vect, line_num in zip(vect_list, vect_addr):
                vect = re.sub(r'vect', '', vect,0,re.I)

                if vect.find('=') != -1:
                    name, component = vect.split('=')
                    xde_dict['vect'][name.rstrip()] = component.lstrip().split()
                    xde_addr['vect'][name.rstrip()] = line_num

                else:
                    temp_list = vect.split()
                    xde_dict['vect'][temp_list[0]] = temp_list[1:]
                    xde_addr['vect'][temp_list[0]] = line_num

        elif keyword == 'matrix':

            matr_list = xde_dict['matrix'].copy()
            matr_addr = xde_addr['matrix'].copy()

            xde_dict['matrix'].clear()
            xde_addr['matrix'].clear()

            xde_dict['matrix'] = {}
            xde_addr['matrix'] = {}

            matr_split_list = []
            addr_split_list = []
            matr_count = -1

            for matr, line_num in zip(matr_list, matr_addr):

                if re.match(r'matrix', matr, re.I) != None:

                    matr_count += 1
                    matr_split_list.append([])
                    addr_split_list.append([])

                matr_split_list[matr_count].append(matr)
                addr_split_list[matr_count].append(line_num)

            for matr_list, matr_addr in zip(matr_split_list, addr_split_list):

                for (i, matr), line_num in zip(enumerate(matr_list), matr_addr):

                    if i == 0:
                        matr = re.sub(r'matrix', '', matr, 0, re.I).lstrip()
                        temp_list = matr.split()

                        if len(temp_list) == 1:
                            matr_name = temp_list[0]
                            row = len(matr_list) - 1

                        elif len(temp_list) == 2:
                            matr_name, row = temp_list
                            clm = len(matr_list[1].split())

                        elif len(temp_list) == 3:
                            matr_name, row, clm = temp_list

                        else:
                            print(f"{Error_color}Error SEC01:  line {Empha_color}{line_num}, " \
                                 +f"{Error_color}too much number, at most need two to describ row and column.\n")
                            break

                        try:
                            xde_dict['matrix'][matr_name] = [int(row), int(clm)]
                            xde_addr['matrix'][matr_name] = [line_num]

                        except ValueError:
                            print(f"{Error_color}Error SEC02: line {Empha_color}{line_num}, " \
                                 +f"{Error_color}must to be a number to describ row and column.\n")
                            break

                    else:
                        xde_dict['matrix'][matr_name].append(matr.split())
                        xde_addr['matrix'][matr_name].append(line_num)

        elif keyword == 'func':

            func_list = xde_dict['func'].copy()
            xde_dict['func'].clear()

            for func in func_list:
                func = re.sub(r'func', '', func,0,re.I)
                xde_dict['func'].append(func.lstrip().split())

        elif keyword == 'shap':

            shap_list = xde_dict['shap'].copy()
            xde_dict['shap'].clear()

            for shap in shap_list:
                xde_dict['shap'].append(re.sub(r'shap', '', shap,0,re.I).lstrip().split())

        elif keyword in ['fvect', 'fmatr']:

            tnsr_list = xde_dict[keyword].copy()
            tnsr_addr = xde_addr[keyword].copy()

            xde_dict[keyword].clear()
            xde_addr[keyword].clear()

            xde_dict[keyword] = {}
            xde_addr[keyword] = {}

            for i,strs in enumerate(tnsr_list):

                line_num = tnsr_addr[i]
                strs = re.sub(keyword, '', strs, 0, re.I)
                temp_list = strs.split()

                try:
                    xde_dict[keyword][temp_list[0]] = list(map(int,temp_list[1:]))
                    xde_addr[keyword][temp_list[0]] = line_num

                except ValueError:
                    print(f"{Error_color}Error SEC03: line {Empha_color}{line_num}, " \
                         +f"{Error_color}must to be a number to describ row or column.\n")
                    break

        elif keyword in ['mass', 'damp','stif']:

            weak_list = xde_dict[keyword].copy()
            weak_addr = xde_addr[keyword].copy()

            xde_dict[keyword].clear()
            xde_addr[keyword].clear()

            weak_para_list = []
            addr_para_list = []

            # push duplicated weak paragraph into 
            # [[],[]..] style of weak_para_list
            # so as to addr_para_list
            para_count = -1
            for strs, line_num in zip(weak_list, weak_addr):
                if strs[:4].lower() == keyword:
                    para_count += 1
                    weak_para_list.append([])
                    addr_para_list.append([])
                weak_para_list[para_count].append(strs)
                addr_para_list[para_count].append(line_num)

            if len(weak_para_list) > 1:
                declared_linenum = addr_para_list[0][0]
                duplicated_linenum = ','.join(map(str,[x[0] for x in addr_para_list[1:]]))
                report_duplicated_declaration(keyword, declared_linenum, duplicated_linenum)

            # parse first declaration
            weak_list = weak_para_list[0]
            weak_addr = addr_para_list[0]

            # distributed weak form as 'dist = +[a;a]*c + ...'
            if weak_list[0].lower() == keyword \
            and re.match(r'dist', weak_list[1], re.I) != None:

                xde_dict[keyword].append('dist')
                
                try:
                    xde_dict[keyword].append(weak_list[1].split('=')[1].lstrip())
                
                except IndexError:
                    print(f"{Error_color}Error SEC04: line {Empha_color}{weak_addr[1]}, " \
                          f"{Error_color}error form of {Empha_color}'{weak_list[1][:10]}...', " \
                          f"{Error_color}missing '=' after '{weak_list[1][:4]}'.\n")
                
                xde_addr[keyword].append(weak_addr[1])

                if len(weak_list) >2 :
                    for line_str, line_num in zip(weak_list[2:], weak_addr[2:]):
                        xde_dict[keyword].append(line_str)
                        xde_addr[keyword].append(line_num)

            # lumped weak form as '%1 rho ... '
            else:
                xde_dict[keyword] += re.sub(keyword, '', weak_list[0], 0, re.I).lstrip().split()
                xde_addr[keyword] = weak_addr[0]

        elif keyword == 'load':

            weak_list = xde_dict[keyword].copy()
            weak_addr = xde_addr[keyword].copy()

            xde_dict[keyword].clear()
            xde_addr[keyword].clear()

            weak_para_list = []
            addr_para_list = []

            # push duplicated weak paragraph into 
            # [[],[]..] style of weak_para_list
            # so as to addr_para_list
            para_count = -1
            for strs, line_num in zip(weak_list, weak_addr):
                if strs[:4].lower() == keyword:
                    para_count += 1
                    weak_para_list.append([])
                    addr_para_list.append([])
                weak_para_list[para_count].append(strs)
                addr_para_list[para_count].append(line_num)

            if len(weak_para_list) > 1:
                declared_linenum = addr_para_list[0][0]
                duplicated_linenum = ','.join(map(str,[x[0] for x in addr_para_list[1:]]))
                report_duplicated_declaration(keyword, declared_linenum, duplicated_linenum)

            # parse first declaration
            weak_list = weak_para_list[0]
            weak_addr = addr_para_list[0]

            # expression form as 'load = +[a]*b + ...'
            if re.search(r'[=\[\]]',weak_list[0]) != None:

                try:
                    xde_dict[keyword].append(weak_list[0].split('=')[1].lstrip())
                
                except IndexError:
                    print(f"{Error_color}Error SEC04: line {Empha_color}{weak_addr[1]}, " \
                          f"{Error_color}error form of {Empha_color}'{weak_list[1][:10]}...', " \
                          f"{Error_color}missing '=' after '{weak_list[1][:4]}'.\n")
                
                xde_addr[keyword].append(weak_addr[0])

                if len(weak_list) >1 :
                    for line_str, line_num in zip(weak_list[1:], weak_addr[1:]):
                        xde_dict[keyword].append(line_str)
                        xde_addr[keyword].append(line_num)

            # assignment form as 'load fx fy ...'
            else:
                xde_dict[keyword] = weak_list[0].split()[1:]
                xde_addr[keyword].append(weak_addr[0])

            '''
            for i,load_str in enumerate(xde_dict['load']):
                if load_str[:4].lower() == 'load':

                    try:
                        xde_dict['load'][i] = load_str.split('=')[1].lstrip()

                    except IndexError:
                        print(f"{Error_color}Error SEC05: line {Empha_color}{xde_addr['load'][i]}, " \
                              f"{Error_color}error form of {Empha_color}'{load_str[:10]}...', " \
                              f"{Error_color}missing '=' after '{load_str[:4]}'.\n")
            '''

    export_parsing_result('sec', xde_dict, xde_addr)
# end sec_parse()

def report_duplicated_declaration(keyword, declared_linenum, duplicated_linenum):
    print(f"{Error_color}Error SEC01: duplicated declaration of '{keyword}' at "\
          f"line {Empha_color}{duplicated_linenum}, {Error_color}it has been "\
          f"declared at line {Empha_color}{declared_linenum}.\n")

def fnl_parse(ges_info, xde_dict, xde_addr):

    keyword_list = list(xde_dict.keys())

    # parsing workflow features
    parse_workflow_code(xde_dict)

    # parsing non-workflow features
    for keyword in keyword_list:

        # parse disp and func for complex
        if keyword in ['disp', 'func']:
            if 'cmplx_tag' in xde_dict and xde_dict['cmplx_tag'] == 1:

                xde_dict[f'cmplx_{keyword}'] = xde_dict[keyword].copy()
                xde_dict[keyword].clear()

                for var in xde_dict[f'cmplx_{keyword}']:
                    xde_dict[keyword].append(var+'r')
                    xde_dict[keyword].append(var+'i')

        elif 'shap' == keyword:
            parse_shap_declaration(ges_info, xde_dict)

        elif 'mate' == keyword:
            parse_mate_declaration(xde_dict)

        elif 'gaus' == keyword:

            if xde_dict['gaus'][0] == '%3':
                xde_dict['gaus'] = ges_info['gaus_type']

            else:
                xde_dict['gaus'] = xde_dict['gaus'][0]

        elif keyword in ['mass','damp']:

            if  xde_dict[keyword][0] == '%1':
                xde_dict[keyword][0] = 'lump'

            if  len(xde_dict[keyword]) == 1:
                xde_dict[keyword].append('1.0')

        # initial to empty fvect
        elif 'fvect' == keyword:

            for lists in xde_dict['fvect'].values():

                if len(lists) == 0:
                    lists.clear()
                    lists += [""]

                elif len(lists) == 1:
                    length = int(lists[0])
                    lists.clear()
                    lists += ['' for ii in range(length)]

        # initial to empty fmatr
        elif 'fmatr' == keyword:

            for lists in xde_dict['fmatr'].values():

                if len(lists) == 0:
                    lists += ['1','1']

                elif len(lists) == 2:
                    lists += [['' for ii in range(int(lists[1]))] \
                                  for ii in range(int(lists[0]))]

        # transform array declaration
        elif 'array' == keyword:
            complete_array_info(xde_dict, xde_addr)

    export_parsing_result('fnl', xde_dict, xde_addr)
# end fnl_parse()

def parse_shap_declaration(ges_info, xde_dict):
    
    shap_dict = {}

    # 3.1.1 common shap (maybe user declare twice or more, so the first active)
    base_shap_dclr_times = 0
    for shap_list in xde_dict['shap']:

        base_shap_dclr_times += 1
        if base_shap_dclr_times > 1:
            break

        if len(shap_list) == 2:

            if  shap_list[0] == '%1': 
                shap_list[0] = ges_info['shap_form']

            if  shap_list[1] == '%2': 
                shap_list[1] = ges_info['shap_nodn']

            base_shap_type = shap_list[0] + shap_list[1]
            shap_dict[base_shap_type] = xde_dict['disp'].copy()

            if 'coef' in xde_dict:
                xde_dict['coef_shap'] = {}
                xde_dict['coef_shap'][base_shap_type] = xde_dict['coef'].copy()
    
    # 3.1.2 penalty or mix shap
    for shap_list in xde_dict['shap']:

        if len(shap_list) >= 3:

            if  shap_list[0] == '%1':
                shap_list[0] = ges_info['shap_form']

            if  shap_list[1] == '%4' \
            or  shap_list[1].isnumeric():

                var_list  = shap_list[2:]
                disp_find_n = len(set(var_list)&set(xde_dict['disp']))
                
                coef_find_n = 0
                if 'coef' in xde_dict:
                    coef_find_n = len(set(var_list)&set(xde_dict['coef']))

                if (disp_find_n > 0 or coef_find_n > 0) \
                and shap_list[1] == '%4':

                    if   base_shap_type == 't6' : 
                        shap_list[1] = '3'

                    elif base_shap_type == 'q9' : 
                        shap_list[1] = '4'

                    elif base_shap_type == 'w10': 
                        shap_list[1] = '4'

                    elif base_shap_type == 'c27': 
                        shap_list[1] = '8'

                    subs_shap_type = shap_list[0] + shap_list[1]

                if disp_find_n > 0:
                    if subs_shap_type not in shap_dict:
                        shap_dict[subs_shap_type] = []

                if coef_find_n > 0:
                    if subs_shap_type not in xde_dict['coef_shap']:
                        xde_dict['coef_shap'][subs_shap_type] = []

                for var_name in var_list:

                    if var_name.isnumeric():
                        continue

                    if 'coef' not in xde_dict:
                        if var_name not in xde_dict['disp'] :
                            continue

                    else:
                        if  var_name not in xde_dict['disp'] \
                        and var_name not in xde_dict['coef'] :
                            continue

                    if var_name in shap_dict[base_shap_type]:
                        shap_dict[base_shap_type].remove(var_name)
                        shap_dict[subs_shap_type].append(var_name)

                    if 'coef_shap' in xde_dict:

                        if var_name in xde_dict['coef_shap'][base_shap_type]:
                            xde_dict['coef_shap'][base_shap_type].remove(var_name)
                            xde_dict['coef_shap'][subs_shap_type].append(var_name)

            elif shap_list[1] == '%2c' \
            or  (shap_list[1][-1].lower() == 'c' \
                and shap_list[1][:-1].isnumeric) :

                var_list = shap_list[2:]

                pena_vars = {}
                for var_name in var_list:

                    if var_name.isnumeric(): 
                        continue

                    if var_name.find('_'):
                        var_name, pan_name = var_name.split('_')[:2]

                    pena_vars[var_name] = pan_name

                shap_list[1]   = shap_list[1].replace('%2',ges_info['shap_nodn'])
                subs_shap_type = shap_list[0] + shap_list[1]

                if subs_shap_type not in shap_dict:
                    shap_dict[subs_shap_type] = pena_vars

                for pena_var in pena_vars.keys() :
                    shap_dict[base_shap_type].remove(pena_var)
    
    xde_dict['shap'] = shap_dict
# end parse_shap_declaration()

def parse_mate_declaration(xde_dict):

    mate_dict = {}
    mate_dict['default'] = {}
    mate_var = []
    mate_val = []

    from check_xde import is_number
    for strs in xde_dict['mate']:

        if is_number(strs) :
            mate_val.append(strs)

        else:
            mate_var.append(strs)

    len_val = len(mate_val)
    for var_i, var in enumerate(mate_var):

        if var_i < len_val:
            mate_dict['default'][var] = mate_val[var_i]

        else:
            mate_dict['default'][var] = '0.0'

    xde_dict['mate'] = mate_dict
# end parse_mate_declaration()

def parse_workflow_code(xde_dict):

    regx_key = r'\$C[CPV6]|@[LAWSR]|ARRAY'

    for code_place in xde_dict['code'].keys():
        for code_i, code_line in enumerate(xde_dict['code'][code_place]):
            code_regx = re.match(regx_key,code_line,re.I)

            if code_regx == None:
                # say something
                continue

            code_key = code_regx.group()
            code_key_lower = code_key.lower()

            if   code_key_lower == '$cc' \
            or   code_key_lower == '$c6':
                xde_dict['code'][code_place][code_i] \
                    = 'Insr_Code: ' + code_line.replace(code_key,'').lstrip()

            elif code_key_lower == '$cv':
                xde_dict['code'][code_place][code_i] \
                    = 'Tnsr_Asgn: ' + code_line.replace(code_key,'').lstrip()

            elif code_key_lower == '$cp':
                xde_dict['code'][code_place][code_i] \
                    = 'Cplx_Asgn: ' + code_line.replace(code_key,'').lstrip()

            # 3.6.2 parsing operator
            elif code_key_lower == '@l':

                opr_list = code_line.replace(code_key,'').lstrip().split()
                opr_expr = opr_list[0]
                opr_name = opr_expr.split('.')[0]
                asgn_type = opr_list[1].lower()

                var_prefxs = ['',  '',   '',     '[']
                var_posfxs = ['',  '_i', '_i_j', ']']
                asgn_types = ['c', 'v',  'm',    'f']

                if asgn_type == 'n':

                    if   opr_name.lower() == 'singular':
                        xde_dict['code'][code_place][code_i] \
                            = 'Oprt_Asgn: '+opr_expr

                    elif opr_name.lower() == 'vol':
                        xde_dict['code'][code_place][code_i] \
                            = 'Oprt_Asgn: '+opr_expr

                elif asgn_type in asgn_types:

                    type_indx = asgn_types.index(asgn_type)
                    prefx_str = var_prefxs[type_indx]
                    posfx_str = var_posfxs[type_indx]

                    if asgn_type == 'f':

                        if   'fvect' in xde_dict \
                        and opr_list[2] in xde_dict['fvect']:
                            posfx_str = '_i'   + posfx_str

                        elif 'fmatr' in xde_dict \
                        and opr_list[2] in xde_dict['fmatr']:
                            posfx_str = '_i_j' + posfx_str

                    temp_str  = 'Oprt_Asgn: ' \
                              + prefx_str + opr_list[2] + posfx_str \
                              + '=' + opr_expr + '(' \
                              + ','.join(opr_list[3:]) + ')'

                    xde_dict['code'][code_place][code_i] = temp_str

            # 3.6.3 parsing assignment
            elif code_key_lower == '@a':
                expr = code_line.replace(code_key,'').lstrip().split('=')
                xde_dict['code'][code_place][code_i] \
                    = 'Func_Asgn: [' + expr[0].rstrip() \
                    + ']=' + expr[1].lstrip()

            elif code_key_lower == '@r':
                expr = code_line.replace(code_key,'').lstrip().split('=')
                xde_dict['code'][code_place][code_i] \
                    = 'Func_Asgn: [' + expr[0].rstrip() \
                    + ']=' + expr[1].lstrip().replace('[','').replace(']','')

            elif code_key_lower in ['@w','@s']:
                opr_list = code_line.replace(code_key,'').lstrip().split()
                temp_str = 'Func_Asgn: '

                for strs, prefx, posfx \
                in zip(['vect', 'matrix', 'fvect', 'fmatr' ], \
                       ['',     '',       '[',     '['     ],
                       ['_i=',  '_i_j=',  '_i]=',  '_i_j]=']) :

                    if strs in xde_dict \
                    and opr_list[0] in xde_dict[strs]:
                        prefx_str, posfx_str = prefx, posfx

                temp_str += prefx_str + opr_list[0] + posfx_str

                temp_str += opr_list[1] + '[' + ','.join(opr_list[2:]) + ']'

                xde_dict['code'][code_place][code_i] = temp_str
# end parse_workflow_code()

def complete_array_info(xde_dict, xde_addr):

    for strs, line_num in zip( xde_dict['array'], xde_addr['array']):

        strs = re.sub(r'array', '', strs, 0, re.I).lstrip()

        for array in strs.split(','):

            index_list = list (map( lambda x: int(x.lstrip('[').rstrip(']')), \
                                    re.findall(r'\[\d+\]',array) ))
            array_var  = array.split('[')[0]

            tensor_type = len(index_list)

            if tensor_type == vector:

                vect_len = index_list[0]

                if 'array_vect' not in xde_dict:
                    xde_dict['array_vect'] = {}
                    xde_addr['array_vect'] = {}

                xde_dict['array_vect'][array_var] = \
                    [array_var + '[' + str(ii+1) + ']' \
                        for ii in range(vect_len)]

                xde_addr['array_vect'][array_var] = line_num

            elif tensor_type == matrix:

                matr_row = index_list[0]
                matr_clm = index_list[1]

                if 'array_matrix' not in xde_dict:
                    xde_dict['array_matrix'] = {}
                    xde_addr['array_matrix'] = {}

                xde_dict['array_matrix'][array_var] = [matr_row, matr_clm] \
                    + [[array_var + '[' + str(ii+1) + '][' + str(jj+1) + ']' \
                        for jj in range(matr_clm)] \
                            for ii in range(matr_row)]

                xde_addr['array_matrix'][array_var] = [line_num]
# end complete_array_info()

def export_parsing_result(stage, xde_dict, xde_addr):
    if dict_check[stage] != 0:
        file = open(ifo_folder + stage + '_check.json', mode='w')
        file.write(json.dumps(xde_dict,indent=4))
        file.close()
    if addr_check[stage] != 0:
        file = open(ifo_folder + stage + '_addr.json',  mode='w')
        file.write(json.dumps(xde_addr,indent=4))
        file.close()
# end export_parsing_result()
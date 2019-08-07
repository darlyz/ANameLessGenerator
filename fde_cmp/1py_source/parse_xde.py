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

dict_check = {'pre':1, 'sec':1, 'fnl':0}
addr_check = {'pre':1, 'sec':1, 'fnl':0}

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
    #fnl_parse(ges_info, xde_dict, xde_addr)

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

    if dict_check['pre'] != 0:
        file = open(ifo_folder + 'pre_check.json', mode='w')
        file.write(json.dumps(xde_dict,indent=4))
        file.close()
    if addr_check['pre'] != 0:
        file = open(ifo_folder + 'pre_addr.json',  mode='w')
        file.write(json.dumps(xde_addr,indent=4))
        file.close()
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

            # distributed weak form declaration
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

            # lumped weak form declaration
            else:
                xde_dict[keyword].append('lump')
                xde_dict[keyword] += re.sub(keyword, '', weak_list[0], 0, re.I).lstrip().split()
                xde_addr[keyword] = weak_addr[0]

        elif keyword == 'load':
            for i,load_str in enumerate(xde_dict['load']):
                if load_str[:4].lower() == 'load':

                    try:
                        xde_dict['load'][i] = load_str.split('=')[1].lstrip()

                    except IndexError:
                        print(f"{Error_color}Error SEC05: line {Empha_color}{xde_addr['load'][i]}, " \
                              f"{Error_color}error form of {Empha_color}'{load_str[:10]}...', " \
                              f"{Error_color}missing '=' after '{load_str[:4]}'.\n")

    if dict_check['sec'] != 0:
        file = open(ifo_folder + 'sec_check.json', mode='w')
        file.write(json.dumps(xde_dict,indent=4))
        file.close()
    if addr_check['sec'] != 0:
        file = open(ifo_folder + 'sec_addr.json',  mode='w')
        file.write(json.dumps(xde_addr,indent=4))
        file.close()
# end pre_parse()

def report_duplicated_declaration(keyword, declared_linenum, duplicated_linenum):
    print(f"{Error_color}Error SEC01: duplicated declaration of '{keyword}' at "\
          f"line {Empha_color}{duplicated_linenum}, {Error_color}it has been "\
          f"declared at line {Empha_color}{declared_linenum}.\n")

def fnl_parse(ges_info, xde_dict, xde_addr):
    pass
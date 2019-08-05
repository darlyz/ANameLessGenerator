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

dict_check = {'pre':0, 'sec':1, 'fnl':0}
addr_check = {'pre':0, 'sec':1, 'fnl':0}

def parse_xde(ges_info, xde_dict, xde_addr, xdefile):

    pre_parse(xde_dict, xde_addr, xdefile)

    sec_parse(xde_dict, xde_addr)
    
    #if gen_obj['check'] > 0:
    #    from check_xde import check_xde
    #    error = check_xde(ges_info, xde_dict, xde_addr)
    #    if error :
    #        return error
    # 
    #sec_parse(ges_info, xde_dict, xde_addr)

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
                report_duplicated_declaration(keyword, xde_addr)
            
            xde_dict[keyword] = xde_dict[keyword][0].split()[1:]

        elif keyword == 'vect':

            vect_list = xde_dict['vect'].copy()
            xde_dict['vect'].clear()
            xde_dict['vect'] = {}

            for vect in vect_list:
                vect = re.sub(r'vect', '', vect,0,re.I)
                if vect.find('=') != -1:
                    name, component = vect.split('=')
                    xde_dict['vect'][name.rstrip()] = component.lstrip().split()
                else:
                    temp_list = vect.split()
                    xde_dict['vect'][temp_list[0]] = temp_list[1:]

        elif keyword == 'matrix':

            matr_list = xde_dict['matrix'].copy()
            addr_list = xde_addr['matrix'].copy()

            xde_dict['matrix'].clear()
            xde_addr['matrix'].clear()

            xde_dict['matrix'] = {}
            xde_addr['matrix'] = {}

            matr_split_list = []
            addr_split_list = []
            matr_count = -1

            for matr, line_num in zip(matr_list, addr_list):

                if re.match(r'matrix', matr, re.I) != None:

                    matr_count += 1
                    matr_split_list.append([])
                    addr_split_list.append([])

                matr_split_list[matr_count].append(matr)
                addr_split_list[matr_count].append(line_num)

            for matr_list, addr_list in zip(matr_split_list, addr_split_list):

                for (i, matr), line_num in zip(enumerate(matr_list), addr_list):

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
                xde_dict['func'] += func.lstrip().split()

        elif keyword == 'shap':

            shap_list = xde_dict['shap'].copy()
            xde_dict['shap'].clear()

            for shap in shap_list:
                xde_dict['shap'].append(re.sub(r'shap', '', shap,0,re.I).lstrip().split())

        elif keyword in ['fvect', 'fmatr']:

            key_list = xde_dict[keyword].copy()
            xde_dict[keyword].clear()
            xde_dict[keyword] = {}

            for i,strs in enumerate(key_list):

                line_num = xde_addr[keyword][i]
                strs = re.sub(keyword, '', strs, 0, re.I)
                temp_list = strs.split()

                try:
                    xde_dict[keyword][temp_list[0]] = list(map(int,temp_list[1:]))

                except ValueError:
                    print(f"{Error_color}Error SEC03: line {Empha_color}{line_num}, " \
                         +f"{Error_color}must to be a number to describ row or column.\n")
                    break

        elif keyword in ['mass', 'damp','stif']:

            key_list = xde_dict[keyword].copy()
            xde_dict[keyword].clear()

            if key_list[0].lower() == keyword \
            and re.match(r'dist', key_list[1], re.I) != None:

                xde_dict[keyword].append('dist')
                xde_dict[keyword].append(key_list[1].split('=')[1].lstrip())

                if len(key_list) >2 :
                    for strs in key_list[2:]:
                        xde_dict[keyword].append(strs)

            else:
                xde_dict[keyword].append('lump')
                xde_dict[keyword] += re.sub(keyword, '', key_list[0], 0, re.I).lstrip().split()

        elif keyword == 'load':

            xde_dict['load'][0] = xde_dict['load'][0].split('=')[1]





    if dict_check['sec'] != 0:
        file = open(ifo_folder + 'sec_check.json', mode='w')
        file.write(json.dumps(xde_dict,indent=4))
        file.close()
    if addr_check['sec'] != 0:
        file = open(ifo_folder + 'sec_addr.json',  mode='w')
        file.write(json.dumps(xde_addr,indent=4))
        file.close()
# end pre_parse()

def report_duplicated_declaration(keyword, xde_addr):
    print(f"{Error_color}Error SEC01: duplicated declaration of '{keyword}' at "\
          f"line {Empha_color}{','.join(map(str,xde_addr[keyword][1:]))}, "\
          f"{Error_color}it has been declared at line {Empha_color}{xde_addr[keyword][0]}.\n")
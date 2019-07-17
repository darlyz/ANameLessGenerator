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
import re as regx
pre_check = 1
sec_check = 1
ifo_folder = '../4other_gen_file/'

def parse_xde(ges_info, xde_lists, list_addr, xdefile):

    # 1 preliminary parse
    pre_parse(ges_info, xde_lists, list_addr, xdefile)
    
    # 2 checking
    from check_xde import check_xde
    error = check_xde(ges_info, xde_lists, list_addr)
    if error : return error
     
    # 3 secondary parse
    sec_parse(ges_info, xde_lists, list_addr)

    return False

def pre_parse(ges_info, xde_lists, list_addr, xdefile):

    # all the xde keys
    keyws_reg  = r'ARRAY|COEF|COOR|COMMON|DAMP' \
               + r'|DEFI|DISP|DIST|END|USERC|' \
               + r'FUNC|FVECT|FMATR|GAUS|LOAD|' \
               + r'MATE|MASS|MATRIX|SHAP|STIF|VECT|' \
               + r'\$C[CPV6]|\$I|@[LAWSR]'

    keywd_tag = {'bf_matrix'   : '', \
                 'matr_dclr'   : 0, \
                 'paragraph'   : 'BFmate',\
    }

    line_i, stitchline = 0, ''
    xde_lists['code'] = {}
    list_addr['code'] = {}

    # 1 fist step parsing while read xde to xde_lists
    for line in xdefile.readlines():
        line_i += 1

        # 1.1.2 skip comment line and blank line
        if regx.match(r'\s*(\$c[c6])?\s*((\\|//).*)?\s*\n',line,regx.I) != None:
            continue

        # 1.1 deal with valid sentence with comment
        # 1.1.1 identify comment and stitch the next line begin with '\'
        line = stitchline + line
        if line.find('\\') != -1 :
            stitchline = line.split('\\')[0]
            continue
        else: stitchline = ''

        # 1.1.3 identify comment begin with '//'
        if line.find('//') != -1:
            line = line.split('//')[0]

        # 1.1.4 pop the space from head and tail
        line = line.strip()

        # 1.2 retrieve the keywords
        code_regx = regx.match(keyws_reg, line, regx.I)

        # 1.2.1 find the keyword at the head
        if code_regx != None:

            key_lower = code_regx.group().lower()

            # 1.2.1.1 match and pop to xde_lists
            if key_lower in ['disp','coef','coor','gaus']:
                push_key_declare(key_lower, line_i, line, xde_lists, list_addr)

            elif key_lower == 'mate':

                if keywd_tag['paragraph'] != 'BFmate':
                    print(f"{Error_color}Error NSN02, : if other " \
                        + "paragraph is writed before definition, " \
                        + "key word 'DEFI' should not be ommited before " \
                        + "'MATE' line and C insertion for 'MATE'.\n")

                push_key_declare('mate', line_i, line, xde_lists, list_addr)
                keywd_tag['paragraph'] = 'AFmate'

            elif key_lower == 'vect':
                push_tonser_declare('vect', line_i, line, xde_lists, list_addr)
                if line.find('|') != -1: xde_lists['cmplx_tag'] = 1

            elif key_lower in ['fmatr','fvect']:
                push_tonser_declare(key_lower, line_i, line, xde_lists, list_addr)

            elif key_lower.find('$')!= -1 or key_lower.find('@')!= -1:
                line = line \
                    .replace('%1',ges_info['shap_form']) \
                    .replace('%2',ges_info['shap_nodn'])

                push_code_line (line_i, line, keywd_tag, xde_lists, list_addr)

                if code_regx.group().lower() == '$cp':
                    xde_lists['cmplx_tag'] = 1

            elif key_lower in ['common','array']:

                line = line \
                    .replace('%1',ges_info['shap_form']) \
                    .replace('%2',ges_info['shap_nodn'])

                push_code_line (line_i, line, keywd_tag, xde_lists, list_addr)

            elif key_lower in ['mass','damp','stif']:
                push_weak_declare(key_lower, line_i, line, keywd_tag, xde_lists, list_addr)

            elif key_lower == 'shap':

                if not 'shap' in xde_lists:
                    list_addr['shap'] = []
                    xde_lists['shap'] = []

                list_addr['shap'].append(line_i)
                xde_lists['shap'].append(line.split()[1:])

            elif key_lower == 'dist':

                if line.find('|') != -1:
                    xde_lists['cmplx_tag'] = 1

                if keywd_tag['paragraph'] in ['mass','damp','stif']:
                    xde_lists[keywd_tag['paragraph']].append('dist')
                    xde_lists[keywd_tag['paragraph']].append(line.split('=')[1].strip())
                    list_addr[keywd_tag['paragraph']].append(line_i)

            elif key_lower == 'load':

                if line.find('|') != -1:
                    xde_lists['cmplx_tag'] = 1

                if not 'load' in xde_lists:
                    xde_lists['load'] = []
                    list_addr['load'] = []

                if line.find('=') != -1:
                    xde_lists['load'].append(line.split('=')[1].strip())
                    list_addr['load'].append(line_i)
                    keywd_tag['paragraph'] = 'load'

                else:
                    load_list = line.rstrip().split()[1:]
                    xde_lists['load'].append(str(len(load_list)))
                    xde_lists['load'] += load_list
                    list_addr['load'].append(line_i)
                

            elif key_lower == 'func':

                wordlist = line.split()

                if len(wordlist) != 1:
                    if not 'func' in xde_lists:
                        xde_lists['func'] = []
                    keywd_tag['func'] = 1
                    xde_lists['func'] += wordlist[1:]

                else:
                    keywd_tag['paragraph'] = 'func'

            elif key_lower == 'matrix':

                push_tonser_declare('matrix', line_i, line, xde_lists, list_addr)
                matrix_name = line.split()[1]
                line_num    = list_addr['matrix'][matrix_name]
                list_addr['matrix'][matrix_name] = []
                list_addr['matrix'][matrix_name].append(line_num)
                
                # tackle that code line write between matrix and other paragraph
                if  keywd_tag['matr_dclr'] == 0:
                    keywd_tag['matr_dclr'] = 1
                    keywd_tag['bf_matrix'] = keywd_tag['paragraph']

                keywd_tag['paragraph'] = 'matrix'

            elif key_lower == 'defi':
                keywd_tag['paragraph'] = 'BFmate'

            elif key_lower == 'end':
                pass

            elif key_lower == 'userc':
                pass

        # 1.2.2 find the non-keyword-head line in 'func' 'stif' 'mass' and 'damp' paragraph
        else:
            # 1.2.2.1 find cmplx_tag tag
            if line.find('|') != -1:
                xde_lists['cmplx_tag'] = 1

            key_words= keywd_tag['paragraph']

            # 1.2.2.2 find weak form and disp var deform in non-keyword-head line
            if  key_words in ['mass','damp','stif','load'] \
            and key_words in xde_lists:

                if line.rstrip().lower() == 'null':
                    xde_lists[key_words].append(line.rstrip())
                    list_addr[key_words].append(line_i)

                else:
                    xde_lists[key_words].append(line)
                    list_addr[key_words].append(line_i)

            elif  key_words == 'func':
                xde_lists['code'][key_words].append(line)
                list_addr['code'][key_words].append(line_i)

            elif key_words == 'matrix' :
                xde_lists['matrix'][matrix_name].append(line)
                list_addr['matrix'][matrix_name].append(line_i)

            else:
                print(f'{Warnn_color}Warn NSN03: redundant information ' \
                     + 'or wrong declare, line {line_i}: ' + line)

    if pre_check == 1:
        import json
        file = open(ifo_folder+'pre_check.json',mode='w')
        file.write(json.dumps(xde_lists,indent=4))
        file.close()
        file = open(ifo_folder+'pre_addr.json',mode='w')
        file.write(json.dumps(list_addr,indent=4))
        file.close()
# end pre_parse()

# key declare type1: DISP, COEF, COOR, GAUS, MATE
def push_key_declare (strs, line_num, line, xde_lists, list_addr):

    if strs in xde_lists:
        print(f'{Warnn_color}Warn NSN04: line {Empha_color}' \
             +f'{line_num}, {strs} {Warnn_color}has been declared ' \
             +f'at line {Empha_color}{list_addr[strs]}\n')

    else:
        line = line.replace(',',' ').replace(';',' ')
        list_addr[strs] = line_num
        xde_lists[strs] = line.split()[1:]

# common declare type: VECT, FMATR
def push_tonser_declare (strs, line_num, line, xde_lists, list_addr):

    if strs not in xde_lists: 
        xde_lists[strs] = {}
        list_addr[strs] = {}

    line = regx.sub(r'\s*=\s*',' ',line)
    wordlist = line.split()
    list_addr[strs][wordlist[1]] = line_num
    xde_lists[strs][wordlist[1]] = wordlist[2:]

# common code line : @x, $Cx
def push_code_line (line_num, line, keywd_tag, xde_lists, list_addr):
    code_find = 0
    key_words = keywd_tag['paragraph']

    # tackle that code line write between matrix and other paragraph
    if key_words == 'matrix':
        key_words = keywd_tag['bf_matrix']

    if key_words in ['BFmate','AFmate','func','stif','mass','damp']:

        code_find = 1

        if key_words not in xde_lists['code']:
            xde_lists['code'][key_words] = []
            list_addr['code'][key_words] = []

        xde_lists['code'][key_words].append(line)
        list_addr['code'][key_words].append(line_num)

    if code_find == 0:
        print(f'{Error_color}Error NSN05: line {line_num}, ' \
            + 'wrong position inserted.\n')

# stif, mass, damp declare
def push_weak_declare (strs, line_num, line, keywd_tag, xde_lists, list_addr):

    if strs in xde_lists:
        print(f'{Error_color}Error NSN06: line {Empha_color}' \
            + f'{line_num}, {strs} {Error_color}has been declared ' \
            + f'at line {Empha_color}{list_addr[strs][0]}.\n')

    else:
        list_addr[strs], xde_lists[strs] = [], []
        wordlist = line.split()

        if len(wordlist) > 1:
            list_addr[strs].append(line_num)
            xde_lists[strs] = wordlist[1:]

        else:
            keywd_tag['paragraph'] = strs

def sec_parse(ges_info, xde_lists, list_addr):

    # 3.0 parse disp and func for complex
    if 'cmplx_tag' in xde_lists and xde_lists['cmplx_tag'] == 1:

        if 'disp' in xde_lists:

            xde_lists['cmplx_disp'] = xde_lists['disp'].copy()
            xde_lists['disp'].clear()

            for strs in xde_lists['cmplx_disp']:
                xde_lists['disp'].append(strs+'r')
                xde_lists['disp'].append(strs+'i')

        if 'func' in xde_lists:

            xde_lists['cmplx_func'] = xde_lists['func'].copy()
            xde_lists['func'].clear()

            for strs in xde_lists['cmplx_func']:
                xde_lists['func'].append(strs+'r')
                xde_lists['func'].append(strs+'i')

    # 3.1 parsing shap
    if 'shap' in xde_lists:
        parse_shap(ges_info, xde_lists)

    # 3.2 parsing mate
    if 'mate' in xde_lists:
        parse_mate(xde_lists)

    # 3.3 parsing gaus
    if 'gaus' in xde_lists:

        if xde_lists['gaus'][0] == '%3':
            xde_lists['gaus'] = ges_info['gaus_type']

        else:
            xde_lists['gaus'] = xde_lists['gaus'][0]

    # 3.4 parsing mass and damp
    if 'mass' in xde_lists:

        if  xde_lists['mass'][0] == '%1':
            xde_lists['mass'][0] = 'lump'

        if  len(xde_lists['mass']) == 1:
            xde_lists['mass'].append('1.0')

    if 'damp' in xde_lists:

        if  xde_lists['damp'][0] == '%1':
            xde_lists['damp'][0] = 'lump'

        if  len(xde_lists['damp']) == 1:
            xde_lists['mass'].append('1.0')

    # 3.5 parsing fvect, fmatr, vect, matrix
    if 'fvect' in xde_lists:

        for lists in xde_lists['fvect'].values():

            if len(lists) == 0:
                lists.append('1')

            if len(lists) == 1:
                lists += ['' for ii in range(int(lists[0]))]

    if 'fmatr' in xde_lists:

        for lists in xde_lists['fmatr'].values():

            if len(lists) == 0:
                lists += ['1','1']

            if len(lists) == 2:
                lists += [['' for ii in range(int(lists[1]))] \
                              for ii in range(int(lists[0]))]

    if 'vect' in xde_lists:

        for lists in xde_lists['vect'].values():
            if not lists[0].isnumeric():
                lists.insert(0,str(len(lists)))

    if 'matrix' in xde_lists:

        for lists in xde_lists['matrix'].values():

            if  not lists[0].isnumeric() \
            and not lists[1].isnumeric() :
                row = len(lists)
                clm = len(lists[0].split())
                lists.insert(0,str(clm))
                lists.insert(0,str(row))

            else: 
                row = int(lists[0])

            for ii in range(row):
                lists[ii+2] = lists[ii+2].split()

    if 'load' in xde_lists:
        if xde_lists['load'][0].isnumeric():
            xde_lists['load'] \
                = ['+[' + xde_lists['disp'][i] + ']*' + xde_lists['load'][i+1] \
                    for i in range(int(xde_lists['load'][0]))]

    # 3.6 parsing code
    parse_code(xde_lists)

    if sec_check == 1:
        import json
        file = open(ifo_folder+'sec_check.json',mode='w')
        file.write(json.dumps(xde_lists,indent=4))
        file.close()
# end sec_parse()

def parse_shap(ges_info, xde_lists):
    shap_dict = {}

    # 3.1.1 common shap (maybe user declare twice or more, so the last active)
    for shap_list in xde_lists['shap']:

        if len(shap_list) == 2:

            if  shap_list[0] == '%1': 
                shap_list[0] = ges_info['shap_form']

            if  shap_list[1] == '%2': 
                shap_list[1] = ges_info['shap_nodn']

            base_shap_type = shap_list[0] + shap_list[1]
            shap_dict[base_shap_type] = xde_lists['disp'].copy()

            if 'coef' in xde_lists:
                xde_lists['coef_shap'] = {}
                xde_lists['coef_shap'][base_shap_type] = xde_lists['coef'].copy()

    # 3.1.2 penalty or mix shap
    for shap_list in xde_lists['shap']:

        if len(shap_list) >= 3:

            if  shap_list[0] == '%1':
                shap_list[0] = ges_info['shap_form']

            if  shap_list[1] == '%4' \
            or  shap_list[1].isnumeric():

                var_list  = shap_list[2:]
                disp_find_n = len(set(var_list)&set(xde_lists['disp']))
                
                coef_find_n = 0
                if 'coef' in xde_lists:
                    coef_find_n = len(set(var_list)&set(xde_lists['coef']))

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
                    if subs_shap_type not in xde_lists['coef_shap']:
                        xde_lists['coef_shap'][subs_shap_type] = []

                for var_name in var_list:

                    if var_name.isnumeric():
                        continue

                    if 'coef' not in xde_lists:
                        if var_name not in xde_lists['disp'] :
                            continue

                    else:
                        if  var_name not in xde_lists['disp'] \
                        and var_name not in xde_lists['coef'] :
                            continue

                    if var_name in shap_dict[base_shap_type]:
                        shap_dict[base_shap_type].remove(var_name)
                        shap_dict[subs_shap_type].append(var_name)

                    if 'coef_shap' in xde_lists:

                        if var_name in xde_lists['coef_shap'][base_shap_type]:
                            xde_lists['coef_shap'][base_shap_type].remove(var_name)
                            xde_lists['coef_shap'][subs_shap_type].append(var_name)

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

    xde_lists['shap'] = shap_dict
# end parse_shap()

def parse_mate(xde_lists):

    mate_dict = {}
    mate_dict['default'] = {}
    mate_var = []
    mate_val = []

    for strs in xde_lists['mate']:

        if regx.match(r'[a-z]\w*', strs, regx.I) == None :
            mate_val.append(strs)

        else:
            mate_var.append(strs)

    for var_i, var in enumerate(mate_var):

        if var_i < len(mate_val):
            mate_dict['default'][var] = mate_val[var_i]

        else:
            mate_dict['default'][var] = '0.0'

    xde_lists['mate'] = mate_dict
# end parse_mate()

def parse_code(xde_lists):

    regx_key = r'\$C[CPV6]|@[LAWSR]|ARRAY'

    for code_place in xde_lists['code'].keys():
        for code_i, code_line in enumerate(xde_lists['code'][code_place]):
            code_regx = regx.match(regx_key,code_line,regx.I)

            if code_regx == None:
                # say something
                continue

            code_key = code_regx.group()

            if   code_key.lower() == '$cc' \
            or   code_key.lower() == '$c6':
                xde_lists['code'][code_place][code_i] \
                    = 'Insr_Code: ' + code_line.replace(code_key,'').lstrip()

            elif code_key.lower() == '$cv':
                xde_lists['code'][code_place][code_i] \
                    = 'Tnsr_Asgn: ' + code_line.replace(code_key,'').lstrip()

            elif code_key.lower() == '$cp':
                xde_lists['code'][code_place][code_i] \
                    = 'Cplx_Asgn: ' + code_line.replace(code_key,'').lstrip()

            # 3.6.2 parsing operator
            elif code_key.lower() == '@l':

                opr_list = code_line.replace(code_key,'').lstrip().split()
                opr_expr = opr_list[0]
                opr_name = opr_expr.split('.')[0]
                asgn_type = opr_list[1].lower()

                var_prefxs = ['',  '',   '',     '[']
                var_posfxs = ['',  '_i', '_i_j', ']']
                asgn_types = ['c', 'v',  'm',    'f']

                if asgn_type == 'n':

                    if   opr_name.lower() == 'singular':
                        xde_lists['code'][code_place][code_i] \
                            = 'Oprt_Asgn: '+opr_expr

                    elif opr_name.lower() == 'vol':
                        xde_lists['code'][code_place][code_i] \
                            = 'Oprt_Asgn: '+opr_expr

                elif asgn_type in asgn_types:

                    type_indx = asgn_types.index(asgn_type)
                    prefx_str = var_prefxs[type_indx]
                    posfx_str = var_posfxs[type_indx]

                    if asgn_type == 'f':

                        if   'fvect' in xde_lists \
                        and opr_list[2] in xde_lists['fvect']:
                            posfx_str = '_i'   + posfx_str

                        elif 'fmatr' in xde_lists \
                        and opr_list[2] in xde_lists['fmatr']:
                            posfx_str = '_i_j' + posfx_str

                    temp_str  = 'Oprt_Asgn: ' \
                              + prefx_str + opr_list[2] + posfx_str \
                              + '=' + opr_expr + '(' \
                              + ','.join(opr_list[3:]) + ')'

                    xde_lists['code'][code_place][code_i] = temp_str

            # 3.6.3 parsing assignment
            elif code_key.lower() == '@a':
                expr = code_line.replace(code_key,'').lstrip().split('=')
                xde_lists['code'][code_place][code_i] \
                    = 'Func_Asgn: [' + expr[0].rstrip() \
                    + ']=' + expr[1].lstrip()

            elif code_key.lower() == '@r':
                expr = code_line.replace(code_key,'').lstrip().split('=')
                xde_lists['code'][code_place][code_i] \
                    = 'Func_Asgn: [' + expr[0].rstrip() \
                    + ']=' + expr[1].lstrip().replace('[','').replace(']','')

            elif code_key.lower() in ['@w','@s']:
                opr_list = code_line.replace(code_key,'').lstrip().split()
                temp_str = 'Func_Asgn: '

                for strs, prefx, posfx \
                in zip(['vect', 'matrix', 'fvect', 'fmatr' ], \
                       ['',     '',       '[',     '['     ],
                       ['_i=',  '_i_j=',  '_i]=',  '_i_j]=']) :

                    if strs in xde_lists \
                    and opr_list[0] in xde_lists[strs]:
                        prefx_str, posfx_str = prefx, posfx

                temp_str += prefx_str + opr_list[0] + posfx_str

                temp_str += opr_list[1] + '[' + ','.join(opr_list[2:]) + ']'

                xde_lists['code'][code_place][code_i] = temp_str

            elif code_key.lower() == 'array':

                var_list = code_line.replace(code_key,'').strip().split(',')
                temp_str = 'Insr_Code: double '

                for var_strs in var_list:
                    var_name = var_strs.strip().split('[')[0]
                    idx_list = regx.findall(r'\[\d+\]',var_strs,regx.I)

                    if len(idx_list) == 1:
                        vect_len = idx_list[0].lstrip('[').rstrip(']')

                        if 'vect' not in xde_lists : 
                            xde_lists['vect'] = {}

                        xde_lists['vect'][var_name]  = [vect_len] \
                            + [var_name + '[' + str(ii+1) + ']' \
                                for ii in range(int(vect_len))]

                        var_strs = var_name + '[' + str(int(vect_len)+1) +']'

                    elif len(idx_list) == 2:

                        matr_row = idx_list[0].lstrip('[').rstrip(']')
                        matr_clm = idx_list[1].lstrip('[').rstrip(']')

                        if 'matrix' not in xde_lists :
                            xde_lists['matrix'] = {}

                        xde_lists['matrix'][var_name] = [matr_row, matr_clm] \
                            + [[var_name+'['+str(ii+1)+']['+str(jj+1)+']' \
                                for jj in range(int(matr_clm))] \
                                    for ii in range(int(matr_row))]

                    temp_str += var_strs + ','
                    
                xde_lists['code'][code_place][code_i] = temp_str.rstrip(',') +';'
# end parse_code()
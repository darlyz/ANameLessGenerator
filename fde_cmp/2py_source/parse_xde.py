'''
 Copyright: Copyright (c) 2019
 Created: 2019-3-30
 Author: Zhang_Licheng
 Title: parse the xde file and check it
 All rights reserved
'''
import re as regx

def parse_xde(gesname, coor_type, xde_lists, list_addr, xdefile):
    
    # 0 prepare
    ges_shap_type = regx.search(r'[ltqwc][1-9]+',gesname,regx.I).group()
    ges_gaus_type = regx.search(r'g[1-9]+',gesname,regx.I)
    if ges_gaus_type != None:
        ges_gaus_type = ges_gaus_type.group()

    dim = regx.search(r'[1-9]+',coor_type,regx.I).group()
    axi = coor_type.split('d')[1]

    ges_shap_nodn = regx.search(r'[1-9]+',ges_shap_type,regx.I).group()
    ges_shap_form = ges_shap_type[0]

    keyws_reg  = r'DEFI|DISP|COEF|COOR|SHAP|GAUS|MATE|MASS|DAMP|STIF|'
    keyws_reg += r'FUNC|VECT|MATRIX|FVECT|FMATR|ARRAY|DIST|LOAD|END|'
    keyws_reg += r'\$C[CPV]|\$I|@[LAWSR]|COMMON|ARRAY'

    keywd_tag = {'disp':0, 'coor':0, 'shap':0, \
                 'gaus':0, 'stif':0, 'load':0, \
                 'mate':0, 'mass':0, 'damp':0, \
                 'complex':0, 'paragraph':'BFmate',\
    }

    line_i = 0
    stitchline = ''
    xde_lists['code'] = {}
    list_addr['code'] = {}

    # 1 fist step parsing while read xde to xde_lists
    for line in xdefile.readlines():
        line_i += 1

        # 1.1 deal with comment and blank line
        # 1.1.1 identify comment and stitch the next line begin with '\'
        line = stitchline + line
        if line.find('\\') != -1 :
            stitchline = line.split('\\')[0]
            continue
        else:
            stitchline = ''

        # 1.1.2 skip comment line and blank line
        if regx.match(r'\s*[\\(//)]*\n',line,regx.I) != None:
            continue

        # 1.1.3 identify comment begin with '//'
        if line.find('//') != -1:
            line = line.split('//')[0]+'\n'
            if regx.match(r'\$CC \n',line,regx.I) != None:
                continue

        # 1.1.4 pop the space from head and tail
        line = line.strip()

        # 1.2 retrieve the keywords
        code_regx = regx.match(keyws_reg,line,regx.I)

        # 1.2.1 find the keyword at the head
        if code_regx != None:

            matrix_name = ''
            matrix_line = ''
            keywd = code_regx.group().lower()

            # 1.2.1.1 match and pop to xde_lists
            if keywd in ['disp','coef','coor','gaus']:
                pushkeydeclar(keywd, line_i, line, xde_lists, list_addr)

            elif keywd == 'mate':
                pushkeydeclar('mate', line_i, line, xde_lists, list_addr)
                keywd_tag['paragraph'] = 'AFmate'

            elif keywd == 'vect':
                pushcomdeclar('vect', line_i, line, xde_lists, list_addr)
                if line.find('|') != -1:
                    keywd_tag['complex'] = 1

            elif keywd == 'fmatr':
                pushcomdeclar('fmatr', line_i, line, xde_lists, list_addr)
                line_list = line.strip().split()
                if len(line_list) == 2:
                    xde_lists['fvect'][line_list[1]].append('1')
                    xde_lists['fvect'][line_list[1]].append('1')

            elif keywd == 'fvect':
                pushcomdeclar('fvect', line_i, line, xde_lists, list_addr)
                line_list = line.strip().split()
                if len(line_list) == 2:
                    xde_lists['fvect'][line_list[1]].append('1')

            elif keywd.find('$')!= -1 or keywd.find('@')!= -1:
                line = line.replace('%1',ges_shap_form).replace('%2',ges_shap_nodn)
                pushcodeline (line_i, line, keywd_tag, xde_lists, list_addr)
                if code_regx.group().lower() == '$cp':
                    keywd_tag['complex'] = 1

            elif keywd in ['common','array']:
                line = line.replace('%1',ges_shap_form).replace('%2',ges_shap_nodn)
                pushcodeline (line_i, line, keywd_tag, xde_lists, list_addr)

            elif keywd in ['mass','damp','stif']:
                pushwekdeclar(keywd, line_i, line, keywd_tag, xde_lists, list_addr)

            elif keywd == 'shap':
                if not 'shap' in xde_lists:
                    list_addr['shap'] = []
                    xde_lists['shap'] = []
                list_addr['shap'].append(line_i)
                wordlist = line.split()
                wordlist.pop(0)
                xde_lists['shap'].append(wordlist)

            elif keywd == 'dist':
                if line.find('|') != -1:
                    keywd_tag['complex'] = 1
                if keywd_tag['paragraph'] in ['mass','damp','stif']:
                    xde_lists[keywd_tag['paragraph']].append('dist')
                    xde_lists[keywd_tag['paragraph']].append(line.split('=')[1].strip())
                    list_addr[keywd_tag['paragraph']].append(line_i)

            elif keywd == 'load':
                if line.find('|') != -1:
                    keywd_tag['complex'] = 1
                if not 'load' in xde_lists:
                    xde_lists['load'] = []
                    list_addr['load'] = []
                xde_lists['load'].append(line.split('=')[1].strip())
                list_addr['load'].append(line_i)
                keywd_tag['paragraph'] = 'load'

            elif keywd == 'func':
                wordlist = line.split()
                if len(wordlist) != 1:
                    if not 'func' in xde_lists:
                        xde_lists['func'] = []
                    keywd_tag['func'] = 1
                    for j in range(2,len(wordlist)+1):
                        xde_lists['func'].append(wordlist[j-1])
                else:
                    keywd_tag['paragraph'] = 'func'

            elif keywd == 'matrix':
                pushcomdeclar('matrix', line_i, line, xde_lists, list_addr)
                matrix_name = line.split()[1]
                matrix_line = list_addr['matrix'][matrix_name]
                list_addr['matrix'][matrix_name] = []
                list_addr['matrix'][matrix_name].append(matrix_line)
                keywd_tag['paragraph'] = 'matrix'

            elif keywd == 'userc':
                pass

            elif keywd == 'end':
                pass

            elif keywd == 'defi':
                pass
        
        # 1.2.2 find the non-keyword-head line in 'func' 'stif' 'mass' and 'damp' paragraph
        else:

            # 1.2.2.1 find complex tag
            if line.find('|') != -1:
                keywd_tag['complex'] = 1

            keywd = keywd_tag['paragraph']

            # 1.2.2.2 find weak form and disp var deform in non-keyword-head line
            if  keywd in ['mass','damp','stif','load'] \
            and keywd in xde_lists:

                if line.find('[')!= -1 and line.find(']')!= -1:

                    xde_lists[keywd].append(line)
                    list_addr[keywd].append(line_i)

            elif  keywd == 'func':

                if line.find('[')!= -1 and line.find(']')!= -1:

                    xde_lists['code'][keywd].append(line)
                    list_addr['code'][keywd].append(line_i)

            elif keywd == 'matrix' :
                xde_lists['matrix'][matrix_name].append(line)
                list_addr['matrix'][matrix_name].append(line_i)

            else:
                print('redundant information or wrong declare, line {}: '.format(line_i)+line)

    # 2 checking
    #from check_xde import check_xde
    #error = check_xde(xde_lists,list_addr,ges_shap_type,ges_gaus_type)
    #if error == True:
    #    return error
     
    # 3 second step parsing
    # 3.1 parsing shap
    if 'shap' in xde_lists:
        shap_dict = {}

        # 3.1.1 common shap (maybe user declare twice or more, so the last active)
        for shap_list in xde_lists['shap']:
            if len(shap_list) == 2:
                if  shap_list[0] == '%1':
                    shap_list[0] = ges_shap_form
                if  shap_list[1] == '%2':
                    shap_list[1] = ges_shap_nodn
                base_shap_type = shap_list[0] + shap_list[1]

                shap_dict[base_shap_type] = []
                for disp_var in xde_lists['disp']:
                    shap_dict[base_shap_type].append(disp_var)

                if 'coef' in xde_lists:
                    xde_lists['coef_shap'] = {}
                    xde_lists['coef_shap'][base_shap_type] = []
                    for coef_var in xde_lists['coef']:
                        xde_lists['coef_shap'][base_shap_type].append(coef_var)

        # 3.1.2 penalty or mix shap
        for shap_list in xde_lists['shap']:
            if len(shap_list) >= 3:
                if  shap_list[0] == '%1':
                    shap_list[0] = ges_shap_form

                if  shap_list[1] == '%4' \
                or  shap_list[1].isnumeric():

                    var_list  = shap_list[2:len(shap_list)]
                    disp_find_n = len(set(var_list)&set(xde_lists['disp']))

                    coef_find_n = 0
                    if 'coef' in xde_lists:
                        coef_find_n = len(set(var_list)&set(xde_lists['coef']))

                    if disp_find_n > 0 or coef_find_n > 0:
                        if   base_shap_type == 't6' :
                            if shap_list[1] == '%4' :
                                shap_list[1] = '3'
                        elif base_shap_type == 'q9' :
                            if shap_list[1] == '%4' :
                                shap_list[1] = '4'
                        elif base_shap_type == 'w10':
                            if shap_list[1] == '%4' :
                                shap_list[1] = '4'
                        elif base_shap_type == 'c27':
                            if shap_list[1] == '%4' :
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

                        if var_name in xde_lists['coef_shap'][base_shap_type]:
                            xde_lists['coef_shap'][base_shap_type].remove(var_name)
                            xde_lists['coef_shap'][subs_shap_type].append(var_name)

                elif shap_list[1] == '%2c' \
                or  (shap_list[1][-1] == 'c' \
                and  shap_list[1][:-1].isnumeric) :

                    var_list = shap_list[2:len(shap_list)]
                    pena_var_list = []

                    for var_name in var_list:
                        if var_name.isnumeric():
                            continue
                        if var_name.find('_'):
                            pena_var = var_name.split('_')[0]
                        else: pena_var = var_name
                        pena_var_list.append(pena_var)
                    
                    pena_var_list = set(pena_var_list)&set(xde_lists['disp'])

                    shap_list[1]   = shap_list[1].replace('%2',ges_shap_nodn)
                    subs_shap_type = shap_list[0]+shap_list[1]

                    if subs_shap_type not in shap_dict:
                        shap_dict[subs_shap_type] = []

                    for pena_var in pena_var_list :
                        shap_dict[base_shap_type].remove(pena_var)
                        shap_dict[subs_shap_type].append(pena_var)

        xde_lists['shap'] = shap_dict

    # 3.2 parsing gaus
    if ges_gaus_type != None: 
          xde_lists['gaus'] = ges_gaus_type
    else: xde_lists['gaus'] = ges_shap_type

    # 3.3 parsing mate
    mate_dict = {}
    mate_dict['default'] = {}
    mate_var = []
    mate_val = []
    regx_var = r'[a-z]\w*'

    for strs in xde_lists['mate']:
        if regx.match(regx_var, strs, regx.I) == None :
            mate_val.append(strs)
        else:
            mate_var.append(strs)

    var_i = 0
    for var in mate_var:
        if var_i < len(mate_val):
            mate_dict['default'][var] = mate_val[var_i]
        else:
            mate_dict['default'][var] = 0.0
        var_i += 1
    xde_lists['mate'] = mate_dict

    # 3.4 parsing mass and damp
    if 'mass' in xde_lists:
        if  xde_lists['mass'][0] == '%1':
            xde_lists['mass'][0] = 'lump'
    if 'damp' in xde_lists:
        if  xde_lists['damp'][0] == '%1':
            xde_lists['damp'][0] = 'lump'

    # 3.5 parsing fvect, fmatr, vect, matrix
    if 'fvect' in xde_lists:
        for lists in xde_lists['fvect'].values():
            if len(lists) == 1:
                for ii in range(int(lists[0])):
                    lists.append('')
    if 'fmatr' in xde_lists:
        for lists in xde_lists['fmatr'].values():
            if len(lists) == 2:
                for ii in range(int(lists[0])):
                    lists.append([])
                    for jj in range(int(lists[1])):
                        lists[ii+2].append('')
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
            for ii in range(2,len(lists)):
                lists[ii] = lists[ii].split()

    # 3.6 parsing code
    regx_key = r'\$C[CPV]|@[LAWSR]|ARRAY'
    for code_place in xde_lists['code'].keys():
        
        code_line_count = len(xde_lists['code'][code_place])
        for code_line, code_i in zip(xde_lists['code'][code_place], range(code_line_count)):
            code_regx = regx.match(regx_key,code_line,regx.I)

            if code_regx != None:
                code_key = code_regx.group()

                if   code_key.lower() == '$cc':
                    xde_lists['code'][code_place][code_i] = code_line.replace(code_key,'Insr_Code:')
                elif code_key.lower() == '$cv':
                    xde_lists['code'][code_place][code_i] = code_line.replace(code_key,'Tnsr_Asgn:')
                elif code_key.lower() == '$cp':
                    xde_lists['code'][code_place][code_i] = code_line.replace(code_key,'Cplx_Asgn:')

                # 3.6.2 parsing operator
                elif code_key.lower() == '@l':
                    opr_list = code_line.split()
                    operator_expr = opr_list[1]
                    operator_name = operator_expr.split('.')[0]
                    assign_type   = opr_list[2].lower()

                    if assign_type == 'n':
                        if   operator_name.lower() == 'singular':
                            xde_lists['code'][code_place][code_i] = 'Oprt_Asgn: '+operator_expr
                        elif operator_name.lower() == 'vol':
                            xde_lists['code'][code_place][code_i] = 'Oprt_Asgn: '+operator_expr

                    else:
                        var_prefix = ['',  '',   '',     '[']
                        var_posfix = ['',  '_i', '_i_j', ']']
                        assgn_type = ['c', 'v',  'm',    'f']

                        for asgn_type, var_prefx, var_posfx in zip(assgn_type, var_prefix, var_posfix) :
                            if assign_type == asgn_type :
                                if asgn_type == 'f':
                                    if   'fvect' in xde_lists and opr_list[3] in xde_lists['fvect']:
                                        var_posfx = '_i'   + var_posfx
                                    elif 'fmatr' in xde_lists and opr_list[3] in xde_lists['fmatr']:
                                        var_posfx = '_i_j' + var_posfx

                                temp_str  = 'Oprt_Asgn: ' + var_prefx + opr_list[3] + var_posfx
                                temp_str += '=' + operator_expr + '('

                                for ii in range(4,len(opr_list)):
                                    temp_str += opr_list[ii] + ','
                                xde_lists['code'][code_place][code_i] = temp_str.rstrip(',') + ')'

                # 3.6.3 parsing assignment
                elif code_key.lower() == '@a':
                    code_line = code_line[3:len(code_line)]
                    expr = code_line.split('=')
                    xde_lists['code'][code_place][code_i] \
                        = 'Func_Asgn: [' + expr[0].rstrip() + ']=' + expr[1].lstrip()

                elif code_key.lower() == '@r':
                    code_line = code_line[3:len(code_line)]
                    expr = code_line.split('=')
                    xde_lists['code'][code_place][code_i-1] \
                        = 'Func_Asgn: [' + expr[0].rstrip() + ']=' + expr[1].lstrip().replace('[','').replace(']','')

                elif code_key.lower() == '@w':
                    opr_list = code_line.split()
                    temp_str = 'Func_Asgn: '+opr_list[1]
                    for strs, idxs in zip(['vect','matrix'], ['_i=','_i_j=']):
                        if  strs in xde_lists and opr_list[1] in xde_lists[strs]:
                            temp_str += idxs + opr_list[2] + '['
                            for ii in range(3,len(opr_list)):
                                temp_str += opr_list[ii] + ','
                            xde_lists['code'][code_place][code_i] = temp_str.rstrip(',') + ']'

                elif code_key.lower() == '@s':
                    opr_list = code_line.split()
                    temp_str = 'Func_Asgn: [' + opr_list[1]
                    for strs, idxs in zip(['fvect','fmatr'], ['_i]=','_i_j]=']):
                        if  strs in xde_lists and opr_list[1] in xde_lists[strs]:
                            temp_str += idxs + opr_list[2] + '['
                            for ii in range(3,len(opr_list)):
                                temp_str += opr_list[ii] + ','
                            xde_lists['code'][code_place][code_i] = temp_str.rstrip(',') + ']'

                elif code_key.lower() == 'array':
                    var_list = code_line[5:len(code_line)].split(',')
                    temp_str = 'Insr_Code: double '

                    for var_strs in var_list:
                        var_name = var_strs.strip().split('[')[0]
                        idx_list = regx.findall(r'\[\d+\]',var_strs,regx.I)

                        if len(idx_list) == 1:
                            vect_len = idx_list[0].lstrip('[').rstrip(']')
                            
                            if 'vect' not in xde_lists :
                                xde_lists['vect'] = {}
                            xde_lists['vect'][var_name] = []

                            xde_lists['vect'][var_name].append(vect_len)
                            for ii in range(int(vect_len)):
                                xde_lists['vect'][var_name].append(var_name + '[' + str(ii+1) + ']')

                            var_strs = var_name + '[' + str(int(vect_len)+1) +']'

                        elif len(idx_list) == 2:
                            matr_row = idx_list[0].lstrip('[').rstrip(']')
                            matr_clm = idx_list[1].lstrip('[').rstrip(']')

                            if 'matrix' not in xde_lists: 
                                xde_lists['matrix'] = {}
                            xde_lists['matrix'][var_name] = []

                            xde_lists['matrix'][var_name].append(matr_row)
                            xde_lists['matrix'][var_name].append(matr_clm)
                            for ii in range(int(matr_row)):
                                xde_lists['matrix'][var_name].append([])
                                for jj in range(int(matr_clm)):
                                    xde_lists['matrix'][var_name][ii+2].append(var_name+'['+str(ii+1)+']['+str(jj+1)+']')
                        
                        temp_str += var_strs + ','
                    xde_lists['code'][code_place][code_i] = temp_str.rstrip(',') +';'
    return False

# key declare type1: DISP, COEF, COOR, GAUS, MATE
def pushkeydeclar (strs, matrix_line, line, xde_lists, list_addr):
    if strs in xde_lists:
        print('warn: line {0}, duplicated declare, {1} has been declared at line {2}'.format(matrix_line,strs,list_addr[strs]))
    else:
        list_addr[strs] = matrix_line
        xde_lists[strs] = []
        line = line.replace(',',' ').replace(';',' ')
        wordlist = line.split()
        for j in range(2,len(wordlist)+1): xde_lists[strs].append(wordlist[j-1])

# common declare type: VECT, FMATR
def pushcomdeclar (strs, matrix_line, line, xde_lists, list_addr):
    if strs not in xde_lists: 
        xde_lists[strs] = {}
        list_addr[strs] = {}
    wordlist = line.split()
    for j in range(2,len(wordlist)+1):
        if j == 2:
            xde_lists[strs][wordlist[1]]=[]
            list_addr[strs][wordlist[1]]=matrix_line
        else:
            xde_lists[strs][wordlist[1]].append(wordlist[j-1])

# common code line : @x, $Cx
def pushcodeline (matrix_line, line, keywd_tag, xde_lists, list_addr):
    code_find = 0
    keywd = keywd_tag['paragraph']
    if keywd in ['BFmate','AFmate','func','stif','mass','damp']:
        code_find = 1
        if keywd not in xde_lists['code']:
            xde_lists['code'][keywd] = []
            list_addr['code'][keywd] = []
        xde_lists['code'][keywd].append(line)
        list_addr['code'][keywd].append(matrix_line)
    if code_find == 0:
        print('error: line {}, wrong position inserted'.format(matrix_line))

# stif, mass, damp declare
def pushwekdeclar (strs, matrix_line, line, keywd_tag, xde_lists, list_addr):
    if strs in xde_lists:
        print('error: line {0}, duplicated declare, {1} has been declared at line {2}'.format(matrix_line,strs,list_addr[strs][0]))
    else:
        list_addr[strs] = []
        xde_lists[strs] = []
        wordlist = line.split()
        if len(wordlist) > 1:
            list_addr[strs].append(matrix_line)
            for j in range(2,len(wordlist)+1):
                xde_lists[strs].append(wordlist[j-1])
        else:
            keywd_tag['paragraph'] = strs